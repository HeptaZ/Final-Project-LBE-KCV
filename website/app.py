"""
Backend Flask untuk menghubungkan form web (index.html) dengan model
yang sudah dilatih di FP_LBE_KCV.ipynb.

Alur singkat (analoginya seperti pramusaji yang antar pesanan ke dapur):
  1. Browser (index.html + script.js) mengirim data form ke sini lewat fetch().
  2. preprocess() menyusun ulang data itu persis seperti kolom yang dipakai
     saat training (one-hot encoding arah angin & daerah, tambah kolom
     tanggal, dst).
  3. Tergantung model yang dipilih user (lr/dt/knn), datanya di-scale (kalau
     perlu) lalu dilempar ke model yang sesuai untuk diprediksi.
  4. Hasilnya (Banjir / Tidak Banjir) dikirim balik sebagai JSON ke browser.

Jalankan dengan:  python app.py
Lalu buka index.html di browser (double click juga bisa).
"""

import os
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # supaya index.html yang dibuka langsung dari file:// / port lain boleh memanggil API ini

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")

REQUIRED_FILES = [
    "ohe_arah_avg.pkl", "ohe_arah_max.pkl", "ohe_nama_daerah.pkl",
    "knn_scaler.pkl", "log_reg_scaler.pkl", "feature_columns.pkl",
    "model_knn.pkl", "model_logreg.pkl", "model_dtree.pkl",
]

_missing = [f for f in REQUIRED_FILES if not os.path.exists(os.path.join(MODELS_DIR, f))]
if _missing:
    raise FileNotFoundError(
        "File model belum lengkap di folder 'models/': " + ", ".join(_missing) +
        "\nJalankan cell 'EXPORT MODEL UNTUK WEB APP' di notebook dulu, lalu "
        "taruh hasilnya (folder models_export) di sini dengan nama folder 'models'."
    )

ohe_arah_avg = joblib.load(os.path.join(MODELS_DIR, "ohe_arah_avg.pkl"))
ohe_arah_max = joblib.load(os.path.join(MODELS_DIR, "ohe_arah_max.pkl"))
ohe_nama_daerah = joblib.load(os.path.join(MODELS_DIR, "ohe_nama_daerah.pkl"))
knn_scaler = joblib.load(os.path.join(MODELS_DIR, "knn_scaler.pkl"))
log_reg_scaler = joblib.load(os.path.join(MODELS_DIR, "log_reg_scaler.pkl"))
feature_columns = joblib.load(os.path.join(MODELS_DIR, "feature_columns.pkl"))

MODELS = {
    "knn": joblib.load(os.path.join(MODELS_DIR, "model_knn.pkl")),
    "lr": joblib.load(os.path.join(MODELS_DIR, "model_logreg.pkl")),   # sebenarnya Logistic Regression
    "dt": joblib.load(os.path.join(MODELS_DIR, "model_dtree.pkl")),
}

NUMERIC_FIELDS = [
    "suhu-min", "suhu-max", "suhu-rata", "kelembapan", "curah-hujan",
    "durasi-matahari", "angin-max", "arah-angin-max", "angin-rata",
]


def derajat_ke_arah(deg):
    """Sama persis dengan fungsi di notebook: ubah derajat (0-360) jadi arah mata angin."""
    deg = float(deg) % 360
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    idx = int((deg + 22.5) // 45) % 8
    return directions[idx]


def preprocess(payload):
    """Susun 1 baris data dari form menjadi DataFrame dengan kolom persis
    seperti saat training (feature_columns)."""
    now = datetime.now()

    base = pd.DataFrame([{
        "suhu_min": payload["suhu-min"],
        "suhu_max": payload["suhu-max"],
        "suhu_avg": payload["suhu-rata"],
        "kelembapan_avg": payload["kelembapan"],
        "curah_hujan": payload["curah-hujan"],
        "durasi_matahari": payload["durasi-matahari"],
        "kecepatan_angin_max": payload["angin-max"],
        "kecepatan_angin_avg": payload["angin-rata"],
        # Model dilatih dengan fitur turunan tanggal (bulan/hari/tahun/hari_dalam_minggu).
        # Form tidak punya input tanggal, jadi kita pakai tanggal hari ini.
        "bulan": now.month,
        "hari": now.day,
        "tahun": now.year,
        "hari_dalam_minggu": now.weekday(),
    }])

    arah_max_compass = derajat_ke_arah(payload["arah-angin-max"])
    ohe_max_df = pd.DataFrame(
        ohe_arah_max.transform([[arah_max_compass]]),
        columns=ohe_arah_max.get_feature_names_out(),
    )

    ohe_avg_df = pd.DataFrame(
        ohe_arah_avg.transform([[payload["arah-angin-terbanyak"]]]),
        columns=ohe_arah_avg.get_feature_names_out(),
    )

    ohe_daerah_df = pd.DataFrame(
        ohe_nama_daerah.transform([[payload["nama-daerah"]]]),
        columns=ohe_nama_daerah.get_feature_names_out(),
    )

    full = pd.concat([base, ohe_avg_df, ohe_max_df, ohe_daerah_df], axis=1)
    # Samakan urutan & kelengkapan kolom persis seperti saat training.
    full = full.reindex(columns=feature_columns, fill_value=0)
    return full


@app.route("/predict", methods=["POST"])
def predict():
    payload = request.get_json(silent=True) or {}

    model_key = payload.get("model-prediksi")
    if model_key not in MODELS:
        return jsonify({"error": "Model prediksi tidak dikenal."}), 400

    for field in NUMERIC_FIELDS:
        if field not in payload:
            return jsonify({"error": f"Field '{field}' wajib diisi."}), 400
        try:
            payload[field] = float(payload[field])
        except (TypeError, ValueError):
            return jsonify({"error": f"Field '{field}' harus berupa angka."}), 400

    try:
        features = preprocess(payload)
    except ValueError as e:
        # Biasanya ini muncul kalau kategori (mis. nama daerah / arah angin)
        # tidak pernah muncul saat training.
        return jsonify({"error": f"Nilai kategori tidak dikenali: {e}"}), 400

    model = MODELS[model_key]

    if model_key == "knn":
        X = knn_scaler.transform(features)
    elif model_key == "lr":
        X = log_reg_scaler.transform(features)
    else:  # decision tree, tidak butuh scaling
        X = features.values

    pred = int(model.predict(X)[0])

    proba = None
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[0].tolist()

    return jsonify({
        "status": "Banjir" if pred == 1 else "Tidak Banjir",
        "prediksi": pred,
        "probabilitas": proba,
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "models_loaded": list(MODELS.keys())})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
