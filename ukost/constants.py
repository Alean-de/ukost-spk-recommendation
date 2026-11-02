PRIORITY_CRITERIA = [
    {'id': 'harga', 'name': 'Harga Sewa', 'icon': 'fas fa-money-bill-wave', 'description': 'Kesesuaian harga dengan budget yang ditentukan'},
    {'id': 'jarak', 'name': 'Jarak ke Kampus', 'icon': 'fas fa-route', 'description': 'Kedekatan lokasi kost dengan kampus'},
    {'id': 'fasilitas', 'name': 'Kelengkapan Fasilitas', 'icon': 'fas fa-th-list', 'description': 'Ketersediaan fasilitas yang dibutuhkan'},
    # {'id': 'keamanan', 'name': 'Keamanan Lingkungan', 'icon': 'fas fa-shield-alt', 'description': 'Tingkat keamanan di sekitar kost'},
    # {'id': 'kenyamanan', 'name': 'Kebersihan & Kenyamanan', 'icon': 'fas fa-star', 'description': 'Kondisi kebersihan dan kenyamanan kost'},
]

FACILITY_WEIGHTS = {
    1 : 4.43,
    2 : 3.92,
    3 : 4.43,
    4 : 4.64,
    5 : 4.68,
    6 : 4.43,
}

CRITERIA_BASE_WEIGHTS = {
    'harga': 4.60,
    'jarak': 4.66,
    'facility': round(sum(FACILITY_WEIGHTS.values()) / len(FACILITY_WEIGHTS), 2),
}