"""
WSN simülasyon modülü - 10 node ile log üretimi ve anomali senaryoları.
"""

import os
import random
from datetime import datetime, timedelta

import pandas as pd

NODES = [f"Node_{i}" for i in range(1, 11)]
MIN_LOG_COUNT = 500

# Anomali node eşleştirmeleri
ANOMALY_NODES = {
    "Node_3": "suspicious_activity",
    "Node_5": "energy_drop",
    "Node_7": "node_silence",
    "Node_2": "communication_error",
    "Node_9": "packet_loss",
    "Node_6": "node_failure",
}


def _normal_log(node_id: str, timestamp: datetime, battery: float) -> dict:
    return {
        "node_id": node_id,
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "packet_count": random.randint(15, 45),
        "battery_level": round(max(5.0, battery), 2),
        "error_rate": round(random.uniform(0.01, 0.08), 3),
        "signal_strength": round(random.uniform(-65, -45), 1),
        "transmission_delay": round(random.uniform(5, 25), 1),
        "status": "normal",
    }


def _anomaly_log(node_id: str, timestamp: datetime, battery: float, status: str) -> dict:
    base = {
        "node_id": node_id,
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "battery_level": round(max(2.0, battery), 2),
        "signal_strength": round(random.uniform(-80, -50), 1),
        "status": status,
    }

    if status == "suspicious_activity":
        base.update({
            "packet_count": random.randint(180, 350),
            "error_rate": round(random.uniform(0.05, 0.15), 3),
            "transmission_delay": round(random.uniform(10, 40), 1),
        })
    elif status == "energy_drop":
        base.update({
            "packet_count": random.randint(10, 30),
            "battery_level": round(random.uniform(5, 15), 2),
            "error_rate": round(random.uniform(0.02, 0.10), 3),
            "transmission_delay": round(random.uniform(15, 50), 1),
        })
    elif status == "communication_error":
        base.update({
            "packet_count": random.randint(10, 35),
            "error_rate": round(random.uniform(0.35, 0.75), 3),
            "transmission_delay": round(random.uniform(30, 80), 1),
        })
    elif status == "packet_loss":
        base.update({
            "packet_count": random.randint(8, 25),
            "error_rate": round(random.uniform(0.15, 0.35), 3),
            "transmission_delay": round(random.uniform(120, 280), 1),
        })
    elif status == "node_failure":
        base.update({
            "packet_count": random.randint(0, 5),
            "battery_level": round(random.uniform(10, 40), 2),
            "error_rate": round(random.uniform(0.60, 0.95), 3),
            "transmission_delay": round(random.uniform(200, 500), 1),
        })
    else:
        base.update({
            "packet_count": random.randint(15, 40),
            "error_rate": round(random.uniform(0.01, 0.10), 3),
            "transmission_delay": round(random.uniform(5, 30), 1),
        })

    return base


def generate_simulation_logs(
    output_path: str,
    min_logs: int = MIN_LOG_COUNT,
    duration_minutes: int = 90,
    interval_seconds: int = 20,
) -> pd.DataFrame:
    """
    WSN ağı simülasyonu çalıştırır ve CSV dosyasına kaydeder.
    En az min_logs (varsayılan 500) kayıt üretir.
    """
    output_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Minimum log sayısını garanti et
    steps_needed = (min_logs + len(NODES) - 1) // len(NODES)
    total_steps = max(
        (duration_minutes * 60) // interval_seconds,
        steps_needed,
    )

    start_time = datetime.now() - timedelta(seconds=total_steps * interval_seconds)
    logs = []
    battery_levels = {node: random.uniform(70, 100) for node in NODES}

    silence_start = total_steps // 3
    silence_end = silence_start + max(total_steps // 4, 5)

    for step in range(total_steps):
        current_time = start_time + timedelta(seconds=step * interval_seconds)

        for node_id in NODES:
            battery_levels[node_id] -= random.uniform(0.05, 0.25)
            battery = battery_levels[node_id]

            if node_id == "Node_7" and silence_start <= step <= silence_end:
                continue

            if node_id == "Node_6" and random.random() < 0.30:
                logs.append(_anomaly_log(node_id, current_time, battery, "node_failure"))
                continue

            if node_id in ANOMALY_NODES:
                status = ANOMALY_NODES[node_id]
                trigger_chance = {
                    "Node_3": 0.55,
                    "Node_5": 0.40,
                    "Node_2": 0.60,
                    "Node_9": 0.50,
                }.get(node_id, 0.35)

                if random.random() < trigger_chance:
                    logs.append(_anomaly_log(node_id, current_time, battery, status))
                else:
                    logs.append(_normal_log(node_id, current_time, battery))
            else:
                logs.append(_normal_log(node_id, current_time, battery))

    # Node_7 sessizlik kaydı
    silence_status_time = start_time + timedelta(seconds=silence_end * interval_seconds)
    logs.append({
        "node_id": "Node_7",
        "timestamp": silence_status_time.strftime("%Y-%m-%d %H:%M:%S"),
        "packet_count": 0,
        "battery_level": round(battery_levels["Node_7"], 2),
        "error_rate": 0.0,
        "signal_strength": -90.0,
        "transmission_delay": 0.0,
        "status": "node_silence",
    })

    df = pd.DataFrame(logs)
    df = df.sort_values("timestamp").reset_index(drop=True)
    df.to_csv(output_path, index=False)

    print(f"[simulation] {len(df)} log -> {output_path}")
    return df


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "dataset", "wsn_simulated_logs.csv")
    df = generate_simulation_logs(csv_path)
    print(f"Tamamlandı: {len(df)} kayıt")
