PRIORITY_CRITERIA = [
    {
        'id': 'harga', 
        'name': 'Harga Sewa', 
        'icon': 'fas fa-money-bill-wave', 
        'description': 'Tingkat kepentingan harga'
    },
    {
        'id': 'jarak', 
        'name': 'Jarak ke Kampus', 
        'icon': 'fas fa-route', 
        'description': 'Tingkat kepentingan lokasi dari kost ke Ukrida'
    },
    {
        'id': 'fasilitas', 
        'name': 'Kelengkapan Fasilitas', 
        'icon': 'fas fa-th-list', 
        'description': 'Tingkat kepentingan kelengkapan fasilitas'
     },
     {
         'id': 'luas kamar', 
         'name': 'Luas Kamar', 
         'icon': 'fas fa-vector-square', 
         'description': 'Tingkat kepentingan keluasan kamar'
    },
    {
        'id': 'keamanan',
        'name': 'Keamanan',
        'icon': 'fas fa-shield-alt',
        'description': 'Tingkat kepentingan keamanan'
    },      
]

CRITERIA_BASE_WEIGHTS = {
    'harga': 0.2612,
    'jarak': 0.2556,
    'fasilitas': 0.2520,
    'luas_kamar': 0.2312
}