from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from ukost.models import (
    University, Kost, Facility, KostFacility, History,
)
from ukost.services import apply_hard_filters, calculate_topsis

PRIORITIES = {'harga': 3, 'jarak': 3, 'fasilitas': 3}


class BaseTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', password='pass12345')
        self.client = Client()
        self.client.login(username='tester', password='pass12345')

        self.univ = University.objects.create(
            name='UKRIDA Kampus 1', location='Jakarta', address_detail='-'
        )
        self.wifi = Facility.objects.create(name='WiFi')
        self.ac = Facility.objects.create(name='AC')

        # Murah, dekat, punya WiFi + AC, putri
        self.kost_a = Kost.objects.create(
            id='K001', name='Kost A', gender_type='Putri',
            location='x', address_details='x',
            price=1000000, distance_to_campus_1=300, distance_to_campus_2=5000,
        )
        # Mahal, jauh, punya WiFi saja, putra
        self.kost_b = Kost.objects.create(
            id='K002', name='Kost B', gender_type='Putra',
            location='x', address_details='x',
            price=2000000, distance_to_campus_1=2000, distance_to_campus_2=300,
        )
        KostFacility.objects.create(kost=self.kost_a, facility=self.wifi)
        KostFacility.objects.create(kost=self.kost_a, facility=self.ac)
        KostFacility.objects.create(kost=self.kost_b, facility=self.wifi)


class HardFilterTests(BaseTestCase):
    def test_filter_gender(self):
        qs = apply_hard_filters(campus_id=self.univ.id, room_type='Putri')
        self.assertEqual([k.id for k in qs], ['K001'])

    def test_semua_tidak_memfilter_gender(self):
        qs = apply_hard_filters(campus_id=self.univ.id, room_type='Semua')
        self.assertEqual(qs.count(), 2)

    def test_filter_harga(self):
        qs = apply_hard_filters(campus_id=self.univ.id, max_price=1500000)
        self.assertEqual([k.id for k in qs], ['K001'])

    def test_filter_jarak_kampus_1(self):
        qs = apply_hard_filters(campus_id=1, max_distance=1000)
        self.assertEqual([k.id for k in qs], ['K001'])

    def test_filter_jarak_kampus_2(self):
        qs = apply_hard_filters(campus_id=2, max_distance=1000)
        self.assertEqual([k.id for k in qs], ['K002'])

    def test_fasilitas_wajib(self):
        qs = apply_hard_filters(
            campus_id=self.univ.id, mandatory_facilities=[self.ac.id]
        )
        self.assertEqual([k.id for k in qs], ['K001'])

    def test_semua_fasilitas_wajib_harus_terpenuhi(self):
        qs = apply_hard_filters(
            campus_id=self.univ.id,
            mandatory_facilities=[self.wifi.id, self.ac.id],
        )
        self.assertEqual([k.id for k in qs], ['K001'])


class TopsisTests(BaseTestCase):
    def test_kosong_mengembalikan_list_kosong(self):
        qs = Kost.objects.none()
        self.assertEqual(
            calculate_topsis(kost=qs, user_priorities=PRIORITIES, univ_id=1), []
        )

    def test_kost_lebih_murah_dan_dekat_ranking_1(self):
        results = calculate_topsis(
            kost=Kost.objects.all(), user_priorities=PRIORITIES, univ_id=1
        )
        self.assertEqual(results[0]['kost'].id, 'K001')
        self.assertEqual(results[0]['rank'], 1)
        self.assertGreater(results[0]['score'], results[1]['score'])

    def test_satu_kost_skornya_1(self):
        results = calculate_topsis(
            kost=Kost.objects.filter(id='K001'),
            user_priorities=PRIORITIES, univ_id=1,
        )
        self.assertEqual(results[0]['score'], 1.0)

    def test_key_hasil_lengkap(self):
        results = calculate_topsis(
            kost=Kost.objects.all(), user_priorities=PRIORITIES, univ_id=1
        )
        for key in ['kost', 'score', 'id', 'price', 'distance',
                    'room_type', 'scores', 'rank']:
            self.assertIn(key, results[0])

    def test_prioritas_mengubah_urutan(self):
        Kost.objects.create(
            id='K003', name='Kost C', gender_type='Putri',
            location='x', address_details='x',
            price=600000, distance_to_campus_1=3000, distance_to_campus_2=3000,
        )
        qs = Kost.objects.filter(id__in=['K001', 'K003'])

        harga_dominan = calculate_topsis(
            kost=qs,
            user_priorities={'harga': 5, 'jarak': 1, 'fasilitas': 1},
            univ_id=1,
        )
        jarak_dominan = calculate_topsis(
            kost=qs,
            user_priorities={'harga': 1, 'jarak': 5, 'fasilitas': 1},
            univ_id=1,
        )
        self.assertEqual(harga_dominan[0]['kost'].id, 'K003')  # murah menang
        self.assertEqual(jarak_dominan[0]['kost'].id, 'K001')  # dekat menang


class WizardSessionTests(BaseTestCase):
    def test_alur_wizard_lengkap(self):
        r1 = self.client.post(reverse('cari_kost'), {
            'campus': self.univ.id, 'room_type': 'Putri',
            'max_price': 1500000, 'max_distance': 1000,
        })
        self.assertRedirects(r1, reverse('fasilitas'))

        r2 = self.client.post(reverse('fasilitas'), {'facilities': [self.wifi.id]})
        self.assertRedirects(r2, reverse('prioritas'))

        r3 = self.client.post(reverse('prioritas'), {
            'priority_harga': 5, 'priority_jarak': 3, 'priority_fasilitas': 2,
        })
        self.assertRedirects(r3, reverse('rekomendasi'))

        prefs = self.client.session['search_prefs']
        self.assertEqual(prefs['room_type'], 'Putri')
        self.assertEqual(prefs['priorities']['harga'], 5)

        self.assertEqual(History.objects.filter(user=self.user).count(), 1)

        r4 = self.client.get(reverse('rekomendasi'))
        self.assertEqual(r4.status_code, 200)
        self.assertContains(r4, 'Kost A')
        self.assertNotContains(r4, 'Kost B')

    def test_rekomendasi_tanpa_session_redirect_ke_langkah_1(self):
        r = self.client.get(reverse('rekomendasi'))
        self.assertRedirects(r, reverse('cari_kost'))

    def test_fasilitas_tanpa_langkah_1_redirect(self):
        r = self.client.post(reverse('fasilitas'), {'facilities': [self.wifi.id]})
        self.assertRedirects(r, reverse('cari_kost'))

    def test_halaman_wizard_butuh_login(self):
        anon = Client()
        r = anon.get(reverse('cari_kost'))
        self.assertEqual(r.status_code, 302)
        self.assertIn('/login', r.url)


class ApiTests(BaseTestCase):
    def test_list_kost(self):
        r = self.client.get(reverse('api_kost_list'))
        self.assertEqual(r.status_code, 200)

    def test_detail_kost(self):
        r = self.client.get(reverse('api_kost_detail', kwargs={'kost_id': 'K001'}))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['name'], 'Kost A')

    def test_detail_kost_tidak_ada_404(self):
        r = self.client.get(reverse('api_kost_detail', kwargs={'kost_id': 'XXX'}))
        self.assertEqual(r.status_code, 404)

    def test_rekomendasi_dan_riwayat_tersimpan(self):
        r = self.client.post(
            reverse('api_rekomendasi'),
            {
                'univ': self.univ.id, 'room_type': 'Putri',
                'max_price': 1500000, 'max_distance': 1000,
                'facilities': [self.wifi.id],
                'priorities': {'harga': 5, 'jarak': 3, 'fasilitas': 2},
            },
            content_type='application/json',
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['count'], 1)

        riwayat = self.client.get(reverse('api_riwayat'))
        self.assertEqual(riwayat.status_code, 200)
        self.assertEqual(len(riwayat.json()), 1)

    def test_rekomendasi_input_tidak_valid(self):
        r = self.client.post(
            reverse('api_rekomendasi'),
            {'room_type': 'Salah'},
            content_type='application/json',
        )
        self.assertEqual(r.status_code, 400)

    def test_api_butuh_login(self):
        anon = Client()
        r = anon.get(reverse('api_kost_list'))
        self.assertIn(r.status_code, (401, 403))