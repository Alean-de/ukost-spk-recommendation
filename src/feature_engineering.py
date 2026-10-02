from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent  # -> Final Project/
INPUT_FILE = BASE_DIR / 'data' / 'processed' / '04_feature_engineering.csv'
OUTPUT_FILE = BASE_DIR / 'data' / 'processed' / '04a_feature_engineering.csv'

PREFIX_LOKASI = {
    'Grogol Petamburan': 'GP',
    'Kebon Jeruk': 'KJ',
    'Palmerah': 'PL',
    'Gambir': 'GB',
    'Tanah Abang': 'TA',
    'Tambora': 'TB',
}

KOLOM_FINAL = [
    'id_kost', 'gender_type', 'nama_kost', 'lokasi',
    'kamar_mandi_dalam', 'wifi', 'ac', 'kloset_duduk', 'kasur', 'akses_24_jam',
    'harga', 'periode_sewa', 'is_promo_bulan_pertama', 'perlu_daftar_tunggu',
    'diskon_bulan_pertama', 'harga_sebelum_diskon', 'bebas_deposit', 'promo_label_lainnya',
    'promo_sewa_lama', 'ada_promo_sewa_lama', 'hemat_sewa_lama', 'jarak_kampus_1', 'jarak_kampus_2', 'detail_alamat'
]

df = pd.read_csv(INPUT_FILE)

# ============================================================
# 0. HAPUS ID LAMA
#    Baris yang sudah dihapus manual bikin urutan id bolong,
#    jadi id dibuat ulang dari nol di langkah 2.
#    Urutan id mengikuti urutan baris di file input.
# ============================================================
if 'id_kost' in df.columns:
    df = df.drop(columns='id_kost')
df = df.reset_index(drop=True)

# ============================================================
# 1. FLAG PROMO BULAN PERTAMA
#    periode_sewa di sini sudah dinormalisasi oleh data_cleaning.py
#    jadi cukup dicek exact match, tidak perlu str.contains lagi.
# ============================================================
df['is_promo_bulan_pertama'] = df['periode_sewa'] == 'Bulan Pertama'

# ============================================================
# 2. GENERATE ID KOST PER LOKASI (format KST-XX0001)
# ============================================================
lokasi_tanpa_prefix = set(df['lokasi'].unique()) - set(PREFIX_LOKASI)
if lokasi_tanpa_prefix:
    print(f"[PERINGATAN] Lokasi tanpa prefix (dipakai 'XX'): {lokasi_tanpa_prefix}")

# Nomor urut per lokasi, mulai dari 1 untuk tiap wilayah
seq_per_lokasi = df.groupby('lokasi', dropna=False).cumcount() + 1

df['id_kost'] = [
    f"KST-{PREFIX_LOKASI.get(lok, 'XX')}{seq:04d}"
    for lok, seq in zip(df['lokasi'], seq_per_lokasi)
]
assert df['id_kost'].is_unique, "id_kost tidak unik, cek kolom lokasi"

# ============================================================
# 3. SUSUN ULANG KOLOM, id_kost DI PALING DEPAN
#    Kolom di luar KOLOM_FINAL (misal jarak_kampus_1, jarak_kampus_2,
#    detail_alamat) tetap dipertahankan di bagian belakang.
# ============================================================
kolom_lain = [c for c in df.columns if c not in KOLOM_FINAL]
df = df[KOLOM_FINAL + kolom_lain]

# ============================================================
# 4. SIMPAN HASIL AKHIR
# ============================================================
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False)

print(f"Feature engineering selesai -> {OUTPUT_FILE}")
print(f"Kolom tambahan yang ikut dipertahankan: {kolom_lain}")
print(df.groupby('lokasi', dropna=False)['id_kost'].agg(['first', 'last', 'count']))
print(df.head(10))
print(df[['periode_sewa', 'is_promo_bulan_pertama']].value_counts())