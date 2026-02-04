# churn_inference.py
import joblib
import pandas as pd
import numpy as np
from dotenv import load_dotenv 
import os
import logging
import sys
# Add MyProjFolder to sys.path so imports work
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from Database.db_config import get_connection


load_dotenv()

# -----------------------------
# Load models and encoders once
# -----------------------------
def load_model(path, name):
    try:
        model = joblib.load(path)
        print(f"[Churn] {name} loaded successfully.")
        logging.info(f"[Churn] {name} loaded successfully.")
        return model
    except Exception as e:
        print(f"[Churn] Failed to load {name}: {e}")
        logging.error(f"[Churn] Failed to load {name}: {e}")
        raise

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "ChurnModels")

gbr_model = load_model(os.path.join(MODELS_DIR, "gbr_model.pkl"), "GBR model")
rf_model = load_model(os.path.join(MODELS_DIR, "rf_model.pkl"), "Random Forest model")
meta_model = load_model(os.path.join(MODELS_DIR, "meta_model.pkl"), "Meta model")
label_encoders = load_model(os.path.join(MODELS_DIR, "label_encoders.pkl"), "Label Encoders")
scaler = load_model(os.path.join(MODELS_DIR, "scaler.pkl"), "Scaler")
column_names = np.load(os.path.join(MODELS_DIR, "X_train_columns.npy"), allow_pickle=True)

 
# -----------------------------
# Preprocess
# -----------------------------
def preprocess_for_inference(df):
    drop_cols = [
        'customer_id', 'count', 'zip_code', 'lat_long', 'surname', 'rownumber',
        'state', 'city', 'latitude', 'longitude', 'churn_reason', 'churn_score',
        'churn_value', 'geography'
    ]
    df = df.drop(columns=[col for col in drop_cols if col in df.columns], errors='ignore')

    # Binary encoding
    binary_categoricals = [
        'gender', 'senior_citizen', 'partner', 'dependents', 'phone_service',
        'paperless_billing', 'complain', 'maritalstatus'
    ]
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    le = LabelEncoder()
    for col in binary_categoricals:
        if col in df.columns:
            df[col] = df[col].fillna('No')
            df[col] = le.fit_transform(df[col].astype(str))

    # Multi-category
    multi_cat_cols = [
        'internet_service', 'online_security', 'online_backup', 'device_protection',
        'tech_support', 'streaming_tv', 'streaming_movies', 'payment_method',
        'contract', 'preferredlogindevice', 'preferedordercat', 'preferredpaymentmode'
    ]
    for col in multi_cat_cols:
        if col in df.columns:
            df[col] = df[col].fillna('Unknown')
    df = pd.get_dummies(df, columns=[col for col in multi_cat_cols if col in df.columns])

    # Numeric conversion
    for col in df.select_dtypes(include='object').columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.fillna(df.median(numeric_only=True), inplace=True)

    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    scaler_local = StandardScaler()
    df[num_cols] = scaler_local.fit_transform(df[num_cols])

    return df

# -----------------------------
# Prediction
# -----------------------------
def ChurnPredictionsModels(df):
    preprocessed_data = preprocess_for_inference(df)
    preprocessed_data = preprocessed_data.reindex(columns=column_names, fill_value=0)

    # Label encoding remaining fields
    for col, le in label_encoders.items():
        if col in preprocessed_data.columns:
            preprocessed_data[col] = le.transform(preprocessed_data[col].astype(str))

    preprocessed_data.replace([np.inf, -np.inf], np.nan, inplace=True)
    preprocessed_data.fillna(0, inplace=True)

    inference_data_scaled = scaler.transform(preprocessed_data)

    # Meta-model
    meta_features = np.column_stack([gbr_model.predict(inference_data_scaled),
                                     rf_model.predict(inference_data_scaled)])
    final_preds = meta_model.predict(meta_features)
    final_probs = meta_model.predict_proba(meta_features)[:, 1]

    # Dynamic threshold
    max_prob = max(final_probs) if len(final_probs) > 0 else 0
    if max_prob > 0.7:
        threshold = 0.5
    elif max_prob > 0.4:
        threshold = 0.3
    else:
        threshold = 0.1
    final_preds = (final_probs >= threshold).astype(int)

    return final_preds, final_probs

# -----------------------------
# Run single batch
# -----------------------------
def run_churn_inference(limit=1000):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT TOP ? * FROM ChurnTable WHERE Processed=0", (limit,))
    rows = cursor.fetchall()
    if not rows:
        print("⏳ No new churn records")
        return {"processed": 0}

    columns = [column[0] for column in cursor.description]
    df = pd.DataFrame.from_records(rows, columns=columns)

    final_preds, final_probs = ChurnPredictionsModels(df)

    df['PredictedChurn'] = final_preds
    df['ChurnProbability'] = final_probs
    df['Processed'] = 1

    for _, row in df.iterrows():
        cursor.execute("""
            UPDATE ChurnTable
            SET PredictedChurn=?, ChurnProbability=?, Processed=?
            WHERE customer_id=?
        """, int(row['PredictedChurn']), float(row['ChurnProbability']), int(row['Processed']), row['customer_id'])

    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ Processed {len(df)} churn records")
    return {"processed": len(df)}

# -----------------------------
# Manual testing
# -----------------------------
if __name__ == "__main__":
    run_churn_inference()
