from django.test import TestCase, Client
from django.urls import reverse
from ukost.mock_data import MOCK_KOST_DATA


class UKostRoutesTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_all_routes_status_200(self):
        routes = [
            ('home', {}),
            ('login', {}),
            ('register', {}),
            ('cari_kost', {}),
            ('fasilitas', {}),
            ('prioritas', {}),
            ('rekomendasi', {}),
            ('detail_kost', {'kost_id': 1}),
            ('bandingkan', {}),
            ('favorit', {}),
            ('api_kost_list', {}),
            ('api_kost_detail', {'kost_id': 1}),
        ]

        for name, kwargs in routes:
            url = reverse(name, kwargs=kwargs)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"Route {name} ({url}) returned {response.status_code}")

    def test_redirect_routes(self):
        # Riwayat redirect
        resp_riwayat = self.client.get(reverse('riwayat'))
        self.assertEqual(resp_riwayat.status_code, 302)
        self.assertIn('/favorit/?tab=riwayat', resp_riwayat.url)

        # Logout redirect
        resp_logout = self.client.get(reverse('logout'))
        self.assertEqual(resp_logout.status_code, 302)
        self.assertIn('/login/', resp_logout.url)

    def test_kost_detail_content(self):
        url = reverse('detail_kost', kwargs={'kost_id': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Kost Pondok Mahasiswa Bahagia')
        self.assertContains(response, '94%')
