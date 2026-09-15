from pathlib import Path
import re
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

# Kolom-kolom rc-price*/bg-u-* di bawah ini AWALNYA masuk daftar hapus
# (karena starts-with 'rc-price'/'bg-u-'), tapi ternyata dibutuhkan
# untuk UI website (hard filter & info promo) -- jadi dikecualikan
# dari penghapusan dan malah diproses lebih lanjut.
KOLOM_DIPERTAHANKAN = {
    'bg-u-ml-xxxs',
    'rc-price__additional-discount',
    'rc-price__additional-discount-price',
    'rc-price__other-promo-label',
    'rc-price__long-term-rate',
}

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
    'bg-u-ml-xxxs': 'status_ketersediaan_raw',
    'rc-price__additional-discount': 'diskon_bulan_pertama_raw',
    'rc-price__additional-discount-price': 'harga_sebelum_diskon_raw',
    'rc-price__other-promo-label': 'promo_label_raw',
    'rc-price__long-term-rate': 'promo_sewa_lama_raw',
}

KOLOM_BARU = [
    'gender_type', 'nama_kost', 'lokasi',
    'kamar_mandi_dalam', 'wifi', 'ac', 'kloset_duduk', 'kasur', 'akses_24_jam',
    'harga_raw', 'periode_sewa',
    'status_ketersediaan_raw', 'diskon_bulan_pertama_raw',
    'harga_sebelum_diskon_raw', 'promo_label_raw', 'promo_sewa_lama_raw',
]

KEYWORD_MAP = {
    'kamar_mandi_dalam': ['k. mandi dalam', 'kamar mandi dalam'],
    'wifi': ['wifi'],
    'ac': ['ac'],
    'kloset_duduk': ['kloset duduk'],
    'kasur': ['kasur'],
    'akses_24_jam': ['akses 24 jam'],
}

# Parser untuk singkatan rupiah gaya Mamikos: "184rb" -> 184000,
# "1.2jt" -> 1200000. Dipakai untuk diskon & promo sewa jangka panjang.
POLA_RUPIAH_SINGKAT = re.compile(r'(?i)(\d+(?:[.,]\d+)?)\s*(rb|jt)')


def parse_rupiah_singkat(teks):
    if pd.isna(teks):
        return None
    match = POLA_RUPIAH_SINGKAT.search(str(teks))
    if not match:
        return None
    angka = float(match.group(1).replace(',', '.'))
    satuan = match.group(2).lower()
    pengali = 1_000 if satuan == 'rb' else 1_000_000
    return int(angka * pengali)


def extract_facilities(row, kolom_mentah, keyword_map):
    combined_text = ' '.join(row[kolom_mentah].dropna().astype(str)).lower()
    return pd.Series({
        fas: any(kw in combined_text for kw in kws)
        for fas, kws in keyword_map.items()
    })


def bersihkan_data(raw_file, label=''):
    """Membersihkan satu file raw hasil scraping Mamikos: drop kolom
    tidak terpakai, rename, konversi harga & fasilitas, ekstrak info
    promo/ketersediaan untuk UI, dan standarisasi nilai lokasi/periode_sewa."""
    print(f"\n--- Membersihkan data {label} ({raw_file.name}) ---")
    df = pd.read_csv(raw_file)

    # 1. Hapus kolom yang tidak dipakai
    #    (KOLOM_DIPERTAHANKAN dikecualikan meskipun prefix-nya cocok)
    kolom_dihapus = [
        col for col in df.columns
        if col.startswith(('rc-facilities_divider', 'bg-c-', 'rc-price', 'bg-u-', 'rc-overview'))
        and col not in KOLOM_DIPERTAHANKAN
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
    kolom_promo_mentah = [
        'status_ketersediaan_raw', 'diskon_bulan_pertama_raw',
        'harga_sebelum_diskon_raw', 'promo_label_raw', 'promo_sewa_lama_raw',
    ]
    kolom_akhir = ['harga', 'periode_sewa'] + kolom_promo_mentah
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

    # 7. Olah kolom ketersediaan & promo untuk kebutuhan UI/hard filter
    # 7a. Ketersediaan: ada isinya -> perlu daftar tunggu; kosong -> bisa langsung sewa
    df['perlu_daftar_tunggu'] = df['status_ketersediaan_raw'].notna()

    # 7b. Diskon bulan pertama (rupiah). Tidak ada promo -> 0, bukan NaN,
    #     supaya gampang dipakai untuk filter/urutkan di website.
    df['diskon_bulan_pertama'] = df['diskon_bulan_pertama_raw'].apply(parse_rupiah_singkat).fillna(0).astype(int)

    # 7c. Harga sebelum diskon. Tidak ada promo -> sama dengan harga saat ini.
    df['harga_sebelum_diskon'] = (
        df['harga_sebelum_diskon_raw']
        .astype(str)
        .str.replace('Rp', '', regex=False)
        .str.replace('.', '', regex=False)
        .str.strip()
    )
    df['harga_sebelum_diskon'] = pd.to_numeric(df['harga_sebelum_diskon'], errors='coerce')
    df['harga_sebelum_diskon'] = df['harga_sebelum_diskon'].fillna(df['harga']).astype(int)

    # 7d. Promo label: pisahkan info 'bebas deposit' (hard filter) dari
    #     promo lain yang bukan soal deposit (mis. 'MidYear Promo Untung'),
    #     supaya tidak ada info yang hilang / tercampur.
    df['bebas_deposit'] = df['promo_label_raw'].str.contains('deposit', case=False, na=False)
    df['promo_label_lainnya'] = df['promo_label_raw'].where(~df['bebas_deposit'])

    # 7e. Promo sewa jangka panjang: simpan teks aslinya untuk ditampilkan,
    #     plus flag boolean dan nilai hemat maksimal (rupiah) untuk filter/urut.
    df['promo_sewa_lama'] = df['promo_sewa_lama_raw']
    df['ada_promo_sewa_lama'] = df['promo_sewa_lama_raw'].notna()
    df['hemat_sewa_lama'] = df['promo_sewa_lama_raw'].apply(parse_rupiah_singkat).fillna(0).astype(int)

    df = df.drop(columns=[
        'status_ketersediaan_raw', 'diskon_bulan_pertama_raw',
        'harga_sebelum_diskon_raw', 'promo_label_raw', 'promo_sewa_lama_raw',
    ])

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
print("\nRingkasan kolom baru:")
print("perlu_daftar_tunggu:", df_clean['perlu_daftar_tunggu'].value_counts().to_dict())
print("bebas_deposit      :", df_clean['bebas_deposit'].value_counts().to_dict())
print("ada_promo_sewa_lama:", df_clean['ada_promo_sewa_lama'].value_counts().to_dict())
print("promo_label_lainnya:", df_clean['promo_label_lainnya'].value_counts(dropna=True).to_dict())