"""
Isolation Forest ile WSN anomali tespiti.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from preprocessing import load_and_clean, prepare_features, FEATURE_COLUMNS

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "anomaly_model.pkl")


def _generate_explanation(row: pd.Series) -> str:
    """Log kaydına göre anomali açıklaması üretir."""
    node = row["node_id"]
    status = str(row.get("status", "normal"))
    packet = row["packet_count"]
    battery = row["battery_level"]
    error = row["error_rate"]
    delay = row["transmission_delay"]

    explanations = {
        "suspicious_activity": f"{node} normalden fazla veri gönderdiği için şüpheli aktivite olarak işaretlendi.",
        "energy_drop": f"{node} pil seviyesinde ani düşüş olduğu için enerji anomalisi tespit edildi.",
        "node_silence": f"{node} uzun süre veri göndermediği için sessizlik anomalisi oluştu.",
        "communication_error": f"{node} yüksek hata oranı nedeniyle iletişim problemi olarak işaretlendi.",
        "packet_loss": f"{node} yüksek iletim gecikmesi nedeniyle paket kaybı riski taşıyor.",
        "node_failure": f"{node} düğüm arızası olasılığı nedeniyle riskli olarak işaretlendi.",
        "normal": "",
    }

    if status in explanations and explanations[status]:
        return explanations[status]

    # ML tespitine göre kural tabanlı açıklama
    if packet > 150:
        return f"{node} normalden fazla veri gönderdiği için şüpheli aktivite olarak işaretlendi."
    if battery < 20:
        return f"{node} pil seviyesinde ani düşüş olduğu için enerji anomalisi tespit edildi."
    if error > 0.30:
        return f"{node} yüksek hata oranı nedeniyle iletişim problemi olarak işaretlendi."
    if delay > 100:
        return f"{node} yüksek iletim gecikmesi nedeniyle paket kaybı riski taşıyor."
    if packet <= 5 and error > 0.50:
        return f"{node} düğüm arızası olasılığı nedeniyle riskli olarak işaretlendi."

    return f"{node} normal davranıştan sapan ölçümler nedeniyle anomali olarak tespit edildi."


def train_and_detect(csv_path: str, save_model: bool = True) -> pd.DataFrame:
    """
    Modeli eğitir, anomali tespiti yapar ve sonuçları DataFrame'e ekler.

    Returns:
        anomaly_score, is_anomaly, explanation sütunları eklenmiş DataFrame
    """
    df = load_and_clean(csv_path)
    X = prepare_features(df)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(
        n_estimators=100,
        contamination=0.12,
        random_state=42,
    )
    predictions = model.fit_predict(X_scaled)
    scores = model.decision_function(X_scaled)

    # Isolation Forest: -1 = anomali, 1 = normal
    df["anomaly_score"] = np.round(-scores, 4)
    df["is_anomaly"] = predictions == -1

    # Status tabanlı anomalileri de işaretle
    anomaly_statuses = {
        "suspicious_activity", "energy_drop", "node_silence",
        "communication_error", "packet_loss", "node_failure",
    }
    status_anomaly = df["status"].isin(anomaly_statuses)
    df["is_anomaly"] = df["is_anomaly"] | status_anomaly

    df["explanation"] = df.apply(
        lambda r: _generate_explanation(r) if r["is_anomaly"] else "",
        axis=1,
    )

    if save_model:
        os.makedirs(MODEL_DIR, exist_ok=True)
        joblib.dump({"model": model, "scaler": scaler, "features": FEATURE_COLUMNS}, MODEL_PATH)

    # Timestamp string formatına çevir (API için)
    df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

    return df


def save_results(df: pd.DataFrame, csv_path: str) -> None:
    """Anomali sonuçlarını CSV'ye yazar."""
    df.to_csv(csv_path, index=False)


def get_riskiest_node(df: pd.DataFrame) -> str:
    """En çok anomali üreten node'u döndürür."""
    if "is_anomaly" not in df.columns:
        return "N/A"
    anomalies = df[df["is_anomaly"].astype(bool)]
    if anomalies.empty:
        return "Yok"
    counts = anomalies["node_id"].value_counts()
    return counts.index[0]
