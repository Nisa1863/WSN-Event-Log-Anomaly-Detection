"""
WSN log verilerinin temizlenmesi ve ML için hazırlanması.
"""

import pandas as pd
import numpy as np

FEATURE_COLUMNS = [
    "packet_count",
    "battery_level",
    "error_rate",
    "signal_strength",
    "transmission_delay",
]


def load_and_clean(csv_path: str) -> pd.DataFrame:
    """
    CSV dosyasını okur, temizler ve ML için hazırlar.

    Args:
        csv_path: Log CSV dosya yolu

    Returns:
        Temizlenmiş DataFrame
    """
    df = pd.read_csv(csv_path)

    # Eksik değer kontrolü
    numeric_cols = FEATURE_COLUMNS + ["packet_count"]
    for col in FEATURE_COLUMNS:
        if col not in df.columns:
            raise ValueError(f"Eksik sütun: {col}")

    # Sayısal sütunları dönüştür
    for col in FEATURE_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Timestamp dönüşümü
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Eksik satırları temizle
    df = df.dropna(subset=["timestamp"] + FEATURE_COLUMNS)

    # Hatalı değerleri filtrele
    df = df[
        (df["packet_count"] >= 0) &
        (df["battery_level"] >= 0) & (df["battery_level"] <= 100) &
        (df["error_rate"] >= 0) & (df["error_rate"] <= 1) &
        (df["transmission_delay"] >= 0)
    ]

    # Eksik status doldur
    if "status" in df.columns:
        df["status"] = df["status"].fillna("normal")
    else:
        df["status"] = "normal"

    # node_id kontrolü
    df["node_id"] = df["node_id"].astype(str)

    return df.reset_index(drop=True)


def prepare_features(df: pd.DataFrame) -> np.ndarray:
    """ML modeli için özellik matrisi hazırlar."""
    return df[FEATURE_COLUMNS].values
