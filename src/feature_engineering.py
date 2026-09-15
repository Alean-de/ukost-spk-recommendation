from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent  # -> Final Project/
INPUT_FILE = BASE_DIR / 'data' / 'processed' / '03_deduplicated.csv'
OUTPUT_FILE = BASE_DIR / 'data' / 'processed' / '04_feature_engineering.csv'

df = pd.read_csv(INPUT_FILE)

# ============================================================
# 1. FLAG PROMO BULAN PERTAMA
#    periode_sewa di sini sudah dinormalisasi oleh data_cleaning.py
#    jadi cukup dicek exact match, tidak perlu str.contains lagi.
# ============================================================
df['is_promo_bulan_pertama'] = df['periode_sewa'] == 'Bulan Pertama'

# ============================================================
# 2. GENERATE ID KOST PER LOKASI (format KST-XX0001)
# ============================================================
prefix_lokasi = {
    'Grogol Petamburan': 'GP',
    'Kebon Jeruk': 'KJ',
    'Palmerah': 'PL',
    'Gambir': 'GB',
    'Tanah Abang': 'TA',
    'Tambora': 'TB',
}

# Nomor urut per lokasi, mulai dari 1 untuk tiap wilayah
seq_per_lokasi = df.groupby('lokasi').cumcount() + 1

df['id_kost'] = [
    f"KST-{prefix_lokasi.get(lok, 'XX')}{seq:04d}"
    for lok, seq in zip(df['lokasi'], seq_per_lokasi)
]

# ============================================================
# 3. SUSUN ULANG KOLOM FINAL, id_kost DI PALING DEPAN
# ============================================================
kolom_final = [
    'id_kost', 'gender_type', 'nama_kost', 'lokasi',
    'kamar_mandi_dalam', 'wifi', 'ac', 'kloset_duduk', 'kasur', 'akses_24_jam',
    'harga', 'periode_sewa', 'is_promo_bulan_pertama',
]
df = df[kolom_final]

# ============================================================
# 4. SIMPAN HASIL AKHIR
# ============================================================
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False)

print(f"Feature engineering selesai -> {OUTPUT_FILE}")
print(df.head(10))
print(df[['periode_sewa', 'is_promo_bulan_pertama']].value_counts())