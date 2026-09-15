#Kecepatan eksekusi, Akurasi dan sensitivitas hasil, dan Kompleksitas algoritma 
from pathlib import Path
import pandas as pd

# ============================================================
#                           PATH SETUP
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / 'data' / 'raw'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

RAW_KAMPUS_1 = RAW_DIR / 'mamikos-2026-09-07-ukrida-kampus-1.csv'
RAW_KAMPUS_2 = RAW_DIR / 'mamikos-2026-09-09-ukrida-kampus-2.csv'

CLEAN_KAMPUS_1_FILE = PROCESSED_DIR / '01_clean_kampus_1.csv'
CLEAN_KAMPUS_2_FILE = PROCESSED_DIR / '01_clean_kampus_2.csv'
MERGED_FILE = PROCESSED_DIR / '02_merged_raw.csv'
DEDUPLICATED_FILE = PROCESSED_DIR / '03_deduplicated.csv'

RENAME_MAP = {
    'tipe': 'gender_type',
    'track-list-booking-kost': 'kamar_mandi_dalam',
    'track-list-booking-kost (2)': 'wifi',
    'track-list-booking-kost (3)': 'ac',
    'track-list-booking-kost (4)': 'kloset_duduk',
    'track-list-booking-kost (5)': 'kasur',
    'track-list-booking-kost (6)': 'akses_24_jam',
    'harga': 'harga_raw',
    'tipe_': 'periode_sewa',
}

KOLOM_BARU = [
    'gender_type', 'nama_kost', 'lokasi',
    'kamar_mandi_dalam', 'wifi', 'ac', 'kloset_duduk', 'kasur', 'akses_24_jam',
    'harga_raw', 'periode_sewa',
]

KEYWORD_MAP = {
    'kamar_mandi_dalam': ['k. mandi dalam', 'kamar mandi dalam'],
    'wifi': ['wifi'],
    'ac': ['ac'],
    'kloset_duduk': ['kloset duduk'],
    'kasur': ['kasur'],
    'akses_24_jam': ['akses 24 jam'],
}


def extract_facilities(row, kolom_mentah, keyword_map):
    combined_text = ' '.join(row[kolom_mentah].dropna().astype(str)).lower()
    return pd.Series({
        fas: any(kw in combined_text for kw in kws)
        for fas, kws in keyword_map.items()
    })


def bersihkan_data(raw_file, label=''):
    """Membersihkan satu file raw hasil scraping Mamikos: drop kolom
    tidak terpakai, rename, konversi harga & fasilitas, dan
    standarisasi nilai lokasi/periode_sewa."""
    print(f"\n--- Membersihkan data {label} ({raw_file.name}) ---")
    df = pd.read_csv(raw_file)

    # 1. Hapus kolom yang tidak dipakai
    kolom_dihapus = [
        col for col in df.columns
        if col.startswith(('rc-facilities_divider', 'bg-c-', 'rc-price', 'bg-u-', 'rc-overview'))
    ]
    print(f"Kolom dihapus ({len(kolom_dihapus)}): {kolom_dihapus}")
    df = df.drop(columns=kolom_dihapus, errors='ignore')

    # 2. Rename kolom
    df = df.rename(columns=RENAME_MAP)

    # 3. Susun ulang kolom
    df = df[KOLOM_BARU]

    # 4. Harga -> integer
    df['harga'] = (
        df['harga_raw']
        .astype(str)
        .str.replace('Rp', '', regex=False)
        .str.replace('.', '', regex=False)
        .str.strip()
    )
    df['harga'] = pd.to_numeric(df['harga'], errors='coerce')
    df = df.drop(columns=['harga_raw'])

    # 5. Fasilitas -> boolean
    kolom_identitas = ['gender_type', 'nama_kost', 'lokasi']
    kolom_akhir = ['harga', 'periode_sewa']
    kolom_fasilitas_mentah = [c for c in df.columns if c not in kolom_identitas + kolom_akhir]

    df_fasilitas = df.apply(
        extract_facilities, axis=1,
        kolom_mentah=kolom_fasilitas_mentah, keyword_map=KEYWORD_MAP
    )
    df = pd.concat([df[kolom_identitas], df_fasilitas, df[kolom_akhir]], axis=1)

    # 6. Perbaiki inconsistency data
    df['lokasi'] = (
        df['lokasi']
        .str.replace(r'(?i)\bkecamatan\b', '', regex=True)
        .str.strip()
        .str.title()
        .replace({'Grogol': 'Grogol Petamburan'})
    )
    df['periode_sewa'] = df['periode_sewa'].replace({
        '/bulan': 'Bulanan',
        '(Bulan pertama)': 'Bulan Pertama',
    })

    print(f"Selesai: {len(df)} baris.")
    return df


# ============================================================
# 1. BERSIHKAN MASING-MASING RAW FILE PER KAMPUS
# ============================================================
df_kampus_1 = bersihkan_data(RAW_KAMPUS_1, label='Kampus 1')
df_kampus_1.to_csv(CLEAN_KAMPUS_1_FILE, index=False)
print(f"-> Disimpan ke {CLEAN_KAMPUS_1_FILE}")

df_kampus_2 = bersihkan_data(RAW_KAMPUS_2, label='Kampus 2')
df_kampus_2.to_csv(CLEAN_KAMPUS_2_FILE, index=False)
print(f"-> Disimpan ke {CLEAN_KAMPUS_2_FILE}")

# ============================================================
# 2. GABUNGKAN DATA DUA KAMPUS
# ============================================================
print("\n--- Menggabungkan data kampus 1 & kampus 2 ---")
df_merged = pd.concat([df_kampus_1, df_kampus_2], ignore_index=True)
print(f"Total data setelah digabungkan: {len(df_merged)} baris")
df_merged.to_csv(MERGED_FILE, index=False)
print(f"-> Disimpan ke {MERGED_FILE}")

# ============================================================
# 3. HAPUS DATA DUPLIKAT
#    (kost yang sama bisa muncul di kedua raw file kalau lokasinya
#    dekat kampus 1 maupun kampus 2)
# ============================================================
print("\n--- Deduplikasi data ---")
print(f"Total data sebelum deduplikasi: {len(df_merged)} baris")

subset_dedup = ['nama_kost', 'harga']
duplikat_all = df_merged[df_merged.duplicated(subset=subset_dedup, keep=False)]
duplikat_sorted = duplikat_all.sort_values(by=subset_dedup)
print(f"Total baris yang terlibat dalam duplikasi: {len(duplikat_sorted)} baris")
print("--- Sampel 20 baris data duplikat ---")
print(duplikat_sorted[['nama_kost', 'harga', 'lokasi']].head(20))

df_clean = df_merged.drop_duplicates(subset=subset_dedup, keep='first').copy()

total_terhapus = len(df_merged) - len(df_clean)
print(f"\nJumlah baris dibuang : {total_terhapus} baris")
print(f"Jumlah baris bersih  : {len(df_clean)} baris")

df_clean.to_csv(DEDUPLICATED_FILE, index=False)
print(f"\nData cleaning selesai -> {DEDUPLICATED_FILE}")
print(df_clean.head(10))
print(df_clean.info())
print(df_clean['lokasi'].value_counts())
print(df_clean['periode_sewa'].value_counts())