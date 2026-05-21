"""
WSN Anomali Tespiti - Flask Backend API
"""

import os
import math
from datetime import datetime

import numpy as np
import pandas as pd
from flask import Flask, jsonify
from flask_cors import CORS

from simulation import generate_simulation_logs, MIN_LOG_COUNT
from anomaly_detection import train_and_detect, save_results, get_riskiest_node

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "dataset", "wsn_simulated_logs.csv")

os.makedirs(os.path.dirname(DATASET_PATH), exist_ok=True)

app = Flask(__name__)
CORS(app)

_cache = {"df": None, "stats": None}


def _to_json(df):
    if df is None or df.empty:
        return []
    records = df.copy()
    for col in records.columns:
        if records[col].dtype == bool:
            records[col] = records[col].astype(bool)
    out = []
    for row in records.to_dict(orient="records"):
        clean = {}
        for k, v in row.items():
            if k == "is_anomaly":
                clean[k] = bool(v)
            elif isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                clean[k] = None
            elif isinstance(v, (np.integer,)):
                clean[k] = int(v)
            elif isinstance(v, (np.floating,)):
                clean[k] = float(v)
            else:
                clean[k] = v
        out.append(clean)
    return out


def _stats(df):
    if df is None or df.empty:
        return {
            "total_nodes": 10,
            "active_nodes": 0,
            "total_logs": 0,
            "anomaly_count": 0,
            "anomaly_nodes": 0,
            "avg_battery": 0,
            "avg_error_rate": 0,
            "system_status": "Veri Yok",
            "riskiest_node": "Yok",
        }
    is_anom = df["is_anomaly"].astype(bool) if "is_anomaly" in df.columns else pd.Series([False] * len(df))
    anomaly_count = int(is_anom.sum())
    anomaly_nodes = int(df[is_anom]["node_id"].nunique()) if anomaly_count else 0
    active_nodes = int(df["node_id"].nunique())

    if anomaly_count == 0:
        system_status = "Normal"
    elif anomaly_count < 50:
        system_status = "Dikkat"
    else:
        system_status = "Riskli"

    return {
        "total_nodes": 10,
        "active_nodes": active_nodes,
        "total_logs": len(df),
        "anomaly_count": anomaly_count,
        "anomaly_nodes": anomaly_nodes,
        "avg_battery": round(float(df["battery_level"].mean()), 1),
        "avg_error_rate": round(float(df["error_rate"].mean()), 3),
        "system_status": system_status,
        "riskiest_node": get_riskiest_node(df.assign(is_anomaly=is_anom)),
    }


def _run_pipeline(path):
    df = train_and_detect(path)
    save_results(df, path)
    _cache["df"] = df
    _cache["stats"] = _stats(df)
    return df


def _get_data():
    if _cache["df"] is not None:
        return _cache["df"]
    if os.path.exists(DATASET_PATH):
        df = pd.read_csv(DATASET_PATH)
        if "is_anomaly" in df.columns:
            df["is_anomaly"] = df["is_anomaly"].astype(str).str.lower().isin(["true", "1"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            df = _run_pipeline(DATASET_PATH)
        _cache["df"] = df
        _cache["stats"] = _stats(df)
        return df
    return pd.DataFrame()


@app.route("/start-simulation", methods=["POST"])
def start_simulation():
    try:
        _cache["df"] = None
        _cache["stats"] = None
        generate_simulation_logs(DATASET_PATH, min_logs=MIN_LOG_COUNT)
        df = _run_pipeline(DATASET_PATH)
        s = _cache["stats"]
        return jsonify({
            "success": True,
            "message": f"{len(df)} log üretildi, {s['anomaly_count']} anomali bulundu.",
            "total_logs": len(df),
            "anomaly_count": s["anomaly_count"],
            "stats": s,
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/logs", methods=["GET"])
def get_logs():
    return jsonify(_to_json(_get_data()))


@app.route("/anomalies", methods=["GET"])
def get_anomalies():
    df = _get_data()
    if df.empty or "is_anomaly" not in df.columns:
        return jsonify([])
    return jsonify(_to_json(df[df["is_anomaly"].astype(bool)]))


@app.route("/dashboard-stats", methods=["GET"])
def dashboard_stats():
    _get_data()
    return jsonify(_cache["stats"] or _stats(pd.DataFrame()))


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "csv": os.path.exists(DATASET_PATH)})


def _init():
    if os.path.exists(DATASET_PATH):
        _get_data()
    else:
        generate_simulation_logs(DATASET_PATH, min_logs=MIN_LOG_COUNT)
        _run_pipeline(DATASET_PATH)


_init()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True, use_reloader=False)
