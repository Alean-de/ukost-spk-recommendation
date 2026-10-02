from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# ---------------------------------------------------------------------------
# Konfigurasi
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "processed" / "04a_feature_engineering.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "05_data_transformation.csv"

ID_COL = "id_kost"

DROP_COLS = [
    "nama_kost", "promo_label_lainnya", "promo_sewa_lama", "detail_alamat",
    "lokasi", "periode_sewa", "harga_sebelum_diskon", "diskon_bulan_pertama",
    "hemat_sewa_lama", "ada_promo_sewa_lama",
]

BOOLEAN_COLS = [
    "kamar_mandi_dalam", "wifi", "ac", "kloset_duduk", "kasur", "akses_24_jam",
    "is_promo_bulan_pertama", "perlu_daftar_tunggu", "bebas_deposit",
]

DISTANCE_COLS = ["jarak_kampus_1", "jarak_kampus_2"]
PRICE_COL = "harga"
CATEGORICAL_COL = "gender_type"

# Harga di atas persentil ini dipotong (clipping sisi atas saja)
PRICE_CLIP_QUANTILE = 0.99


# ---------------------------------------------------------------------------
# Langkah-langkah transformasi
# ---------------------------------------------------------------------------
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if ID_COL in df.columns:
        df = df.set_index(ID_COL)
    return df


def use_normal_price(df: pd.DataFrame) -> pd.DataFrame:
    """Harga model = harga sebelum diskon (harga normal), supaya ranking tidak
    terpengaruh promo bulan pertama. Harga diskon tetap ada di file 04
    untuk keperluan tampilan."""
    if "harga_sebelum_diskon" not in df.columns:
        return df
    df = df.copy()
    n_na = int(df["harga_sebelum_diskon"].isna().sum())
    n_aneh = int((df["harga_sebelum_diskon"] < df[PRICE_COL]).sum())
    print(f"[harga] harga_sebelum_diskon kosong: {n_na}, lebih kecil dari harga diskon: {n_aneh}")
    df[PRICE_COL] = df["harga_sebelum_diskon"].fillna(df[PRICE_COL])
    return df


def drop_unused_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns=[c for c in DROP_COLS if c in df.columns])


def cast_boolean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ubah kolom boolean jadi 0/1. NaN dianggap 0 (astype(bool) langsung
    akan mengubah NaN menjadi True/1)."""
    df = df.copy()
    for col in BOOLEAN_COLS:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype(bool).astype(int)
    return df


def impute_numeric_median(df: pd.DataFrame) -> pd.DataFrame:
    """Isi NaN pada kolom numerik dengan median kolom tersebut."""
    df = df.copy()
    for col in df.select_dtypes(include=[np.number]).columns:
        n_missing = df[col].isnull().sum()
        if n_missing > 0:
            df[col] = df[col].fillna(df[col].median())
            print(f"[impute] {col}: {n_missing} NaN ({n_missing / len(df):.0%}) diisi median")
    return df


def encode_gender(df: pd.DataFrame) -> pd.DataFrame:
    """One-hot encoding gender. drop_first=True -> kategori 'Campur'
    direpresentasikan oleh Putra=0 dan Putri=0."""
    if CATEGORICAL_COL not in df.columns:
        return df
    return pd.get_dummies(df, columns=[CATEGORICAL_COL], drop_first=True, dtype=int)


def scale_price(df: pd.DataFrame) -> pd.DataFrame:
    """Clip harga sisi atas (persentil 99), lalu Min-Max ke rentang 0-1."""
    if PRICE_COL not in df.columns:
        return df
    df = df.copy()
    batas_atas = df[PRICE_COL].quantile(PRICE_CLIP_QUANTILE)
    n_clipped = int((df[PRICE_COL] > batas_atas).sum())
    harga_clip = df[PRICE_COL].clip(upper=batas_atas)
    df[PRICE_COL] = MinMaxScaler().fit_transform(harga_clip.to_frame())
    print(f"[harga] batas atas = {batas_atas:,.0f}, {n_clipped} data dipotong")
    return df


def scale_distance(df: pd.DataFrame) -> pd.DataFrame:
    """Min-Max jarak kampus ke rentang 0-1."""
    cols = [c for c in DISTANCE_COLS if c in df.columns]
    if not cols:
        return df
    df = df.copy()
    df[cols] = MinMaxScaler().fit_transform(df[cols])
    return df


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    df = load_data(INPUT_FILE)

    df_model = (
        df.pipe(use_normal_price)
          .pipe(drop_unused_columns)
          .pipe(cast_boolean_columns)
          .pipe(impute_numeric_median)
          .pipe(encode_gender)
          .pipe(scale_price)
          .pipe(scale_distance)
    )

    df_model.to_csv(OUTPUT_FILE)

    print(f"\n[SUCCESS] File 05 (Model Ready) tersimpan: {OUTPUT_FILE}")
    print(f"Bentuk data: {df_model.shape}")
    print(df_model[[PRICE_COL, *DISTANCE_COLS]].describe().loc[["min", "50%", "max"]])
    print(df_model.head())


if __name__ == "__main__":
    main()