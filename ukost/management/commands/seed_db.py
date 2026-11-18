from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ukost.models import (
    University, Faculty, StudyProgram, Cluster,
    Kost, Facility, KostFacility, KostPromotion, UserDetail
)

class Command(BaseCommand):
    help = 'Seed database with initial Universities, Faculties, Study Programs, Clusters, Facilities, Kost, and Demo User'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting database seed...'))

        # 1. Universities
        u1, _ = University.objects.get_or_create(
            id=1,
            defaults={
                'name': 'Universitas Kristen Krida Wacana - Kampus 1 Tanjung Duren',
                'location': 'Tanjung Duren',
                'address_detail': 'Jl. Tanjung Duren Raya No. 4, Grogol Petamburan, Jakarta Barat'
            }
        )
        u2, _ = University.objects.get_or_create(
            id=2,
            defaults={
                'name': 'Universitas Kristen Krida Wacana - Kampus 2 Kedoya',
                'location': 'Kedoya',
                'address_detail': 'Jl. Arjuna Utara No. 6, Kebon Jeruk, Jakarta Barat'
            }
        )
        self.stdout.write(self.style.SUCCESS('Universities seeded.'))

        # 2. Faculties & Study Programs
        faculties_data = {
            'Fakultas Teknik & Ilmu Komputer': [
                'Informatika',
                'Sistem Informasi',
                'Teknik Elektro',
                'Teknik Sipil',
                'Teknik Industri'
            ],
            'Fakultas Kedokteran': [
                'Kedokteran',
                'Profesi Dokter'
            ],
            'Fakultas Kedokteran Gigi': [
                'Kedokteran Gigi',
                'Profesi Dokter Gigi'
            ],
            'Fakultas Ekonomi & Bisnis': [
                'Manajemen',
                'Akuntansi'
            ],
            'Fakultas Ilmu Sosial & Humaniora': [
                'Sastra Inggris'
            ],
            'Fakultas Psikologi': [
                'Psikologi'
            ]
        }

        created_prodis = []
        default_faculty = None
        default_prodi = None

        for fac_name, prodis in faculties_data.items():
            fac, _ = Faculty.objects.get_or_create(name=fac_name)
            if not default_faculty:
                default_faculty = fac
            for prodi_name in prodis:
                sp, _ = StudyProgram.objects.get_or_create(faculty=fac, name=prodi_name)
                created_prodis.append(sp)
                if not default_prodi:
                    default_prodi = sp
        self.stdout.write(self.style.SUCCESS('Faculties and Study Programs seeded.'))

        # 3. Clusters
        c1, _ = Cluster.objects.get_or_create(id=1, defaults={'cluster': 'Budget Friendly (Ekonomis)'})
        c2, _ = Cluster.objects.get_or_create(id=2, defaults={'cluster': 'Standard Nyaman'})
        c3, _ = Cluster.objects.get_or_create(id=3, defaults={'cluster': 'Premium & Eksklusif'})
        self.stdout.write(self.style.SUCCESS('Clusters seeded.'))

        # 4. Facilities
        facilities_map = {
            1: 'Wi-Fi Cepat',
            2: 'Kamar Mandi Dalam',
            3: 'AC (Air Conditioner)',
            4: 'Parkir Motor & Mobil',
            5: 'CCTV & Security 24 Jam',
            6: 'Dapur Bersama',
            7: 'Laundry',
            8: 'Furnitur Lengkap',
            9: 'Akses 24 Jam',
            10: 'Listrik Termasuk',
            11: 'Jendela Kamar',
        }

        fac_objs = {}
        for fid, fname in facilities_map.items():
            f_obj, _ = Facility.objects.get_or_create(id=fid, defaults={'name': fname})
            fac_objs[fid] = f_obj
        self.stdout.write(self.style.SUCCESS('Facilities seeded.'))

        # 5. Kosts
        kost_definitions = [
            {
                'id': '1',
                'name': 'Kost Pondok Mahasiswa Bahagia',
                'cluster': c2,
                'gender_type': Kost.GenderType.PUTRA,
                'location': 'Tanjung Duren',
                'address_details': 'Jl. Taman Apel No. 14, Tanjung Duren, Jakarta Barat',
                'price': 1300000,
                'distance_1': 1200,
                'distance_2': 2500,
                'waiting_list': False,
                'no_deposit_required': False,
                'facilities': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            },
            {
                'id': '2',
                'name': 'Kost Griya Asri Kampus',
                'cluster': c2,
                'gender_type': Kost.GenderType.CAMPUR,
                'location': 'Kedoya',
                'address_details': 'Jl. Kedoya Raya No. 27, Kedoya, Jakarta Barat',
                'price': 1500000,
                'distance_1': 2800,
                'distance_2': 1800,
                'waiting_list': False,
                'no_deposit_required': False,
                'facilities': [1, 2, 3, 4, 5, 7, 8, 9, 11],
            },
            {
                'id': '3',
                'name': 'Kost Melati Indah',
                'cluster': c1,
                'gender_type': Kost.GenderType.PUTRI,
                'location': 'Tanjung Duren',
                'address_details': 'Jl. Melati No. 8, Tanjung Duren Utara, Jakarta Barat',
                'price': 1100000,
                'distance_1': 2100,
                'distance_2': 3200,
                'waiting_list': False,
                'no_deposit_required': False,
                'facilities': [1, 2, 4, 5, 6, 8, 9],
            },
            {
                'id': '4',
                'name': 'Kost Residence Garden View',
                'cluster': c3,
                'gender_type': Kost.GenderType.CAMPUR,
                'location': 'Tanjung Duren',
                'address_details': 'Jl. Tanjung Duren Barat No. 5, Jakarta Barat',
                'price': 2200000,
                'distance_1': 800,
                'distance_2': 2100,
                'waiting_list': False,
                'no_deposit_required': True,
                'facilities': [1, 2, 3, 4, 5, 6, 7, 8, 9, 11],
            },
            {
                'id': '5',
                'name': 'Kost Wisma Mandiri',
                'cluster': c1,
                'gender_type': Kost.GenderType.PUTRA,
                'location': 'Kedoya',
                'address_details': 'Jl. Pilar Raya No. 19, Kedoya Selatan, Jakarta Barat',
                'price': 950000,
                'distance_1': 3500,
                'distance_2': 1200,
                'waiting_list': False,
                'no_deposit_required': True,
                'facilities': [1, 4, 5, 8, 9, 10],
            },
            {
                'id': '6',
                'name': 'Kost Anggrek Harmoni',
                'cluster': c2,
                'gender_type': Kost.GenderType.PUTRI,
                'location': 'Tanjung Duren',
                'address_details': 'Jl. Anggrek No. 3, Tanjung Duren, Jakarta Barat',
                'price': 1400000,
                'distance_1': 1500,
                'distance_2': 2700,
                'waiting_list': False,
                'no_deposit_required': False,
                'facilities': [1, 2, 3, 4, 5, 6, 8, 9, 11],
            },
            {
                'id': '7',
                'name': 'Kost Urban Living Suites',
                'cluster': c3,
                'gender_type': Kost.GenderType.CAMPUR,
                'location': 'Kedoya',
                'address_details': 'Jl. Panjang No. 45, Kedoya, Jakarta Barat',
                'price': 2800000,
                'distance_1': 2400,
                'distance_2': 900,
                'waiting_list': False,
                'no_deposit_required': False,
                'facilities': [1, 2, 3, 4, 5, 6, 7, 8, 9, 11],
            },
            {
                'id': '8',
                'name': 'Kost Cendana Residence',
                'cluster': c1,
                'gender_type': Kost.GenderType.PUTRA,
                'location': 'Tanjung Duren',
                'address_details': 'Jl. Cendana No. 12, Tanjung Duren Selatan, Jakarta Barat',
                'price': 1200000,
                'distance_1': 1000,
                'distance_2': 2400,
                'waiting_list': False,
                'no_deposit_required': False,
                'facilities': [1, 2, 4, 5, 7, 8, 9],
            },
        ]

        for kdata in kost_definitions:
            k_obj, _ = Kost.objects.update_or_create(
                id=kdata['id'],
                defaults={
                    'cluster_id': kdata['cluster'],
                    'gender_type': kdata['gender_type'],
                    'name': kdata['name'],
                    'location': kdata['location'],
                    'address_details': kdata['address_details'],
                    'price': kdata['price'],
                    'distance_to_campus_1': kdata['distance_1'],
                    'distance_to_campus_2': kdata['distance_2'],
                    'waiting_list': kdata['waiting_list'],
                    'no_deposit_required': kdata['no_deposit_required'],
                }
            )

            # Assign facilities
            for fid in kdata['facilities']:
                if fid in fac_objs:
                    KostFacility.objects.get_or_create(kost=k_obj, facility=fac_objs[fid])

            # Sample promo
            if k_obj.id == '1':
                KostPromotion.objects.get_or_create(
                    kost=k_obj,
                    discount_name='Diskon Mahasiswa Baru',
                    defaults={
                        'is_first_month_promo': True,
                        'first_month_discount': 100000,
                        'other_promo_label': 'Diskon Bulan Pertama Rp100.000',
                    }
                )
            elif k_obj.id == '4':
                KostPromotion.objects.get_or_create(
                    kost=k_obj,
                    discount_name='Cashback Sewa 6 Bulan',
                    defaults={
                        'has_long_term_promo': True,
                        'long_term_promo_detail': 'Hemat Rp500.000 sewa 6 bulan',
                        'long_term_savings_amount': 500000,
                    }
                )

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(kost_definitions)} Kosts with facilities.'))

        # 6. Create or update Demo Users for testing profile & login
        users_to_seed = [
            {
                'nim': '412021001',
                'email': 'jonathan.agustinus@civitas.ukrida.ac.id',
                'first_name': 'Jonathan',
                'last_name': 'Agustinus',
                'password': 'password123',
                'campus': u1,
                'faculty': default_faculty,
                'prodi': default_prodi,
            },
            {
                'nim': '412022001',
                'email': 'mahasiswa.ukrida@student.ukrida.ac.id',
                'first_name': 'Mahasiswa',
                'last_name': 'UKRIDA',
                'password': 'demo1234',
                'campus': u1,
                'faculty': default_faculty,
                'prodi': default_prodi,
            }
        ]

        from ukost.models import Favorite, History
        for udata in users_to_seed:
            u_obj, _ = User.objects.get_or_create(
                username=udata['nim'],
                defaults={
                    'email': udata['email'],
                    'first_name': udata['first_name'],
                    'last_name': udata['last_name'],
                }
            )
            u_obj.set_password(udata['password'])
            u_obj.save()

            UserDetail.objects.update_or_create(
                user=u_obj,
                defaults={
                    'university': udata['campus'],
                    'faculty': udata['faculty'],
                    'study_program': udata['prodi'],
                    'nim': udata['nim'],
                }
            )

            # Seed favorites (Kost 1 & Kost 4)
            k1 = Kost.objects.filter(id='1').first()
            k4 = Kost.objects.filter(id='4').first()
            if k1:
                Favorite.objects.get_or_create(user=u_obj, kost=k1)
            if k4:
                Favorite.objects.get_or_create(user=u_obj, kost=k4)

            # Seed sample histories
            if not History.objects.filter(user=u_obj).exists():
                History.objects.create(
                    user=u_obj,
                    university=u1,
                    gender='Semua',
                    budget_limit=2000000,
                    radius_limit=3000,
                    facility=['1', '2', '3', '4'],
                    criteria_weight={'harga': 5, 'jarak': 4, 'fasilitas': 4}
                )
                History.objects.create(
                    user=u_obj,
                    university=u2,
                    gender='Putra',
                    budget_limit=1500000,
                    radius_limit=2000,
                    facility=['1', '2', '8'],
                    criteria_weight={'harga': 4, 'jarak': 5, 'fasilitas': 3}
                )

        self.stdout.write(self.style.SUCCESS('Demo users, favorites, and search histories seeded successfully!'))
        self.stdout.write(self.style.SUCCESS('All database seeding completed successfully!'))

