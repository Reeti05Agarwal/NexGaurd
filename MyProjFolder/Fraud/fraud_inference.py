import sys, os
# Add MyProjFolder to sys.path so imports work
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from Database.db_config import get_connection
import joblib, pandas as pd, numpy as np
from dotenv import load_dotenv
import logging

load_dotenv()

# -----------------------------
# Load models once
# -----------------------------
def load_model(path, name):
    try:
        model = joblib.load(path)
        print(f"[Fraud] {name} loaded successfully.")
        logging.info(f"[Fraud] {name} loaded successfully.")
        return model
    except Exception as e:
        print(f"[Fraud] Failed to load {name}: {e}")
        logging.error(f"[Fraud] Failed to load {name}: {e}")
        raise

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "FraudModels")

lr_model = load_model(os.path.join(MODELS_DIR, "lr_model.pkl"), "Logistic Regression model")
rf_model = load_model(os.path.join(MODELS_DIR, "rf_model.pkl"), "Random Forest model")
meta_model = load_model(os.path.join(MODELS_DIR, "meta_model.pkl"), "Meta model")
label_encoders = load_model(os.path.join(MODELS_DIR, "label_encoder.pkl"), "Label Encoders")
scaler = load_model(os.path.join(MODELS_DIR, "scaler.pkl"), "Scaler")
X_train_columns = np.load(os.path.join(MODELS_DIR, "x_column_names.npy"), allow_pickle=True)


# -----------------------------
# Inference function
# -----------------------------
def FraudPredictionModels(X_test_df):
    transaction_ids = X_test_df["TransactionID"].copy()
    for col in X_train_columns:
        if col not in X_test_df.columns:
            X_test_df[col] = 0
    X_test_df = X_test_df[X_train_columns]

    for col, le in label_encoders.items():
        if col in X_test_df.columns:
            test_vals = X_test_df[col].astype(str)
            le_classes = list(le.classes_)
            if "unknown" not in le_classes:
                le_classes.append("unknown")
                le.classes_ = np.array(le_classes)
            X_test_df[col] = test_vals.map(lambda x: x if x in le_classes else "unknown")
            X_test_df[col] = le.transform(X_test_df[col])

    X_test_df = X_test_df.apply(pd.to_numeric, errors="coerce").fillna(0)
    X_scaled = scaler.transform(X_test_df)

    lr_pred = (lr_model.predict_proba(X_scaled)[:, 1] > 0.5).astype(int)
    rf_pred = rf_model.predict(X_scaled)
    meta_input = np.column_stack([lr_pred, rf_pred])
    meta_pred = (meta_model.predict(meta_input) < 0.3).astype(int)

    return transaction_ids, lr_pred, rf_pred, meta_pred


# -----------------------------
# Single-run Inference (for Fargate & Manual)
# -----------------------------
def run_fraud_inference_cycle(limit=20):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM FraudTable WHERE Processed=0 LIMIT %s", (limit,))
    rows = cursor.fetchall()
    if not rows:
        print("⏳ No new fraud records")
        cursor.close()
        conn.close()
        return {"processed": 0}

    df = pd.DataFrame(rows)
    tx_ids, lr, rf, meta = FraudPredictionModels(df)

    for i, tx_id in enumerate(tx_ids):
        cursor.execute("""
            UPDATE FraudTable
            SET LR_Prediction=%s, RF_Prediction=%s, Meta_Prediction=%s, Processed=1
            WHERE TransactionID=%s
        """, (int(lr[i]), int(rf[i]), int(meta[i]), int(tx_id)))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ Processed {len(tx_ids)} fraud records")
    return {"processed": len(tx_ids)}


# -----------------------------
# Manual trigger
# -----------------------------
if __name__ == "__main__":
    run_fraud_inference_cycle()
