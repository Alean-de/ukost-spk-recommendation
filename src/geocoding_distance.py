from pathlib import Path
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.distance import geodesic

# ============================================================
# PATH SETUP
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'

INPUT_FILE = PROCESSED_DIR / '04_feature_engineering.csv'
OUTPUT_FILE = PROCESSED_DIR / '05_final_dataset_dengan_jarak.csv'
CHECKPOINT_FILE = PROCESSED_DIR / '05_checkpoint_jarak.csv'

df = pd.read_csv(INPUT_FILE)

# Titik acuan kedua kampus Ukrida
KOORDINAT_KAMPUS_1 = (-6.1783, 106.7881)  # Tanjung Duren
KOORDINAT_KAMPUS_2 = (-6.1852, 106.7825)  # Arjuna / FK

# ============================================================
# BOUNDING BOX JAKARTA -- tanpa ini Nominatim bisa mencocokkan
# nama tempat yang sama persis tapi ada di kota/negara lain,
# sehingga jarak jadi tidak masuk akal (sudah pernah kejadian).
# ============================================================
JAKARTA_BBOX = {
    'lat_min': -6.40, 'lat_max': -5.95,
    'lon_min': 106.65, 'lon_max': 106.98,
}
VIEWBOX = [
    (JAKARTA_BBOX['lat_max'], JAKARTA_BBOX['lon_min']),
    (JAKARTA_BBOX['lat_min'], JAKARTA_BBOX['lon_max']),
]


def dalam_jakarta(lat, lon):
    return (JAKARTA_BBOX['lat_min'] <= lat <= JAKARTA_BBOX['lat_max'] and
            JAKARTA_BBOX['lon_min'] <= lon <= JAKARTA_BBOX['lon_max'])


# ============================================================
# GEOCODER + RATE LIMITER
# ============================================================
geolocator = Nominatim(user_agent="ukost_spk_app_v2")
geocode = RateLimiter(
    geolocator.geocode,
    min_delay_seconds=1.2,
    max_retries=2,
    error_wait_seconds=5,
)


def cari_koordinat(query):
    try:
        hasil = geocode(query, viewbox=VIEWBOX, bounded=True, country_codes='id', timeout=10)
        if hasil and dalam_jakarta(hasil.latitude, hasil.longitude):
            return hasil.latitude, hasil.longitude
    except Exception as e:
        print(f"  Error geocoding '{query}': {e}")
    return None, None


# ============================================================
# CACHE: per nama_kost & per lokasi, supaya kost dengan gedung
# yang sama (beda tipe_kamar) tidak digeocode berulang-ulang.
# ============================================================
cache_gedung = {}
cache_lokasi = {}


def dapatkan_koordinat_kost(row):
    nama_kost = row['nama_kost']
    lokasi = row['lokasi']

    # Percobaan 1: nama_kost (sudah tanpa suffix tipe_kamar) + lokasi
    key_gedung = f"{nama_kost}|{lokasi}"
    if key_gedung not in cache_gedung:
        query = f"{nama_kost}, {lokasi}, Jakarta Barat, Indonesia"
        cache_gedung[key_gedung] = cari_koordinat(query)
    lat, lon = cache_gedung[key_gedung]
    if lat is not None:
        return lat, lon, 'kost_spesifik'

    # Percobaan 2 (fallback): centroid lokasi/kecamatan saja
    if lokasi not in cache_lokasi:
        query = f"Kecamatan {lokasi}, Jakarta Barat, Indonesia"
        cache_lokasi[lokasi] = cari_koordinat(query)
    lat, lon = cache_lokasi[lokasi]
    if lat is not None:
        return lat, lon, 'perkiraan_lokasi'

    return None, None, 'gagal'


# ============================================================
# PROSES GEOCODING TIAP BARIS, DENGAN CHECKPOINT
# ============================================================
lat_list, lon_list, akurasi_list = [], [], []
total = len(df)

print(f"\nSedang geocoding otomatis gratis (OSM/Nominatim) untuk {total} baris...")
for idx, row in df.iterrows():
    lat, lon, akurasi = dapatkan_koordinat_kost(row)
    lat_list.append(lat)
    lon_list.append(lon)
    akurasi_list.append(akurasi)

    if (idx + 1) % 10 == 0 or (idx + 1) == total:
        print(f"  [{idx + 1}/{total}] {row['nama_kost'][:35]:<35} -> {akurasi}")

    if (idx + 1) % 50 == 0:
        df_sementara = df.iloc[: idx + 1].copy()
        df_sementara['latitude'] = lat_list
        df_sementara['longitude'] = lon_list
        df_sementara['akurasi_geocoding'] = akurasi_list
        df_sementara.to_csv(CHECKPOINT_FILE, index=False)

df['latitude'] = lat_list
df['longitude'] = lon_list
df['akurasi_geocoding'] = akurasi_list

print("\n=== RINGKASAN AKURASI GEOCODING ===")
ringkasan = df['akurasi_geocoding'].value_counts()
print(ringkasan)
print(f"\nPersentase kost_spesifik: {ringkasan.get('kost_spesifik', 0) / total * 100:.1f}%")

# ============================================================
# HITUNG JARAK KE KEDUA KAMPUS (KM)
# ============================================================
def hitung_jarak(row, titik_kampus):
    if pd.notnull(row['latitude']) and pd.notnull(row['longitude']):
        koordinat_kos = (row['latitude'], row['longitude'])
        return round(geodesic(koordinat_kos, titik_kampus).km, 2)
    return None


print("\nMenghitung jarak ke Kampus 1 & Kampus 2...")
df['jarak_kampus_1'] = df.apply(hitung_jarak, titik_kampus=KOORDINAT_KAMPUS_1, axis=1)
df['jarak_kampus_2'] = df.apply(hitung_jarak, titik_kampus=KOORDINAT_KAMPUS_2, axis=1)

# ============================================================
# SIMPAN DATASET FINAL
# ============================================================
df_final = df.drop(columns=['latitude', 'longitude'])
df_final.to_csv(OUTPUT_FILE, index=False)

print("\nSelesai 100% otomatis tanpa bayar / tanpa kartu!")
print(f"Saved to: {OUTPUT_FILE}")
print(df_final[['nama_kost', 'lokasi', 'jarak_kampus_1', 'jarak_kampus_2', 'akurasi_geocoding']].head(10))