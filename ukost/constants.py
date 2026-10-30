PRIORITY_CRITERIA = [
    {
        'id': 'harga', 
        'name': 'Harga Sewa', 
        'icon': 'fas fa-money-bill-wave', 
        'description': 'Kesesuaian harga dengan budget yang ditentukan'
    },
    {
        'id': 'jarak', 
        'name': 'Jarak ke Kampus', 
        'icon': 'fas fa-route', 
        'description': 'Kedekatan lokasi kost dengan kampus'
    },
    {
        'id': 'fasilitas', 
        'name': 'Kelengkapan Fasilitas', 
        'icon': 'fas fa-th-list', 
        'description': 'Ketersediaan fasilitas yang dibutuhkan'
     },
     {
         'id': 'luas_kamar', 
         'name': 'Luas Kamar', 
         'icon': 'fas fa-th-list', 
         'description': 'Luas kamar yang anda prioritaskan'
      },
]

CRITERIA_BASE_WEIGHTS = {
    'harga': 0.2612,
    'jarak': 0.2556,
    'fasilitas': 0.2520,
    'luas_kamar': 0.2312
}