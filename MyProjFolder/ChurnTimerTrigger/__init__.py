import logging
import pyodbc
from azure.functions import TimerRequest
from datetime import datetime, timezone
import pandas as pd
import numpy as np
import json
import joblib
from sklearn.preprocessing import LabelEncoder, StandardScaler
import os
from dotenv import load_dotenv
load_dotenv()

# === Load models and encoders ===
try:
    gbr_model = joblib.load("Models/ChurnModels/gbr_model.pkl")
    print("[Churn] GBR model loaded successfully.")
    logging.info("[Churn] GBR model loaded successfully.")
except Exception as e: 
    print(f"[Churn] Failed to load GBR model: {e}")
    logging.error(f"[Churn] Failed to load GBR model: {e}")
    raise

try:
    rf_model = joblib.load("Models/ChurnModels/rf_model.pkl")
    print("[Churn] Random Forest model loaded successfully.")
    logging.info("[Churn] Random Forest model loaded successfully.")
except Exception as e:
    print(f"[Churn] Failed to load Random Forest model: {e}")
    logging.error(f"[Churn] Failed to load Random Forest model: {e}")
    raise

try:
    meta_model = joblib.load("Models/ChurnModels/meta_model.pkl")
    print("[Churn] Meta model loaded successfully.")
    logging.info("[Churn] Meta model loaded successfully.")
except Exception as e:
    print(f"[Churn] Failed to load Meta model: {e}")
    logging.error(f"[Churn] Failed to load Meta model: {e}")
    raise

try:
    label_encoders = joblib.load("Models/ChurnModels/label_encoders.pkl")
    print("[Churn] Label Encoders loaded successfully.")
    logging.info("[Churn] Label Encoders loaded successfully.")
except Exception as e:
    print(f"[Churn] Failed to load Label Encoders: {e}")
    logging.error(f"[Churn] Failed to load Label Encoders: {e}")
    raise

try:
    scaler = joblib.load("Models/ChurnModels/scaler.pkl")
    print("[Churn] Scaler loaded successfully.")
    logging.info("[Churn] Scaler loaded successfully.")
except Exception as e:
    print(f"[Churn] Failed to load Scaler: {e}")
    logging.error(f"[Churn] Failed to load Scaler: {e}")
    raise

try:
    column_names = np.load("Models/ChurnModels/X_train_columns.npy", allow_pickle=True)
    print("[Churn] Column names loaded successfully.")
    logging.info("[Churn] Column names loaded successfully.")
except Exception as e:
    print(f"[Churn] Failed to load Column Names: {e}")
    logging.error(f"[Churn] Failed to load Column Names: {e}")
    raise


def ConnectionString():

    SQL_SERVER = os.getenv("SQL_SERVER")
    SQL_DATABASE = os.getenv("SQL_DATABASE")
    SQL_USER = os.getenv("SQL_USER")
    SQL_PASSWORD = os.getenv("SQL_PASSWORD")
    driver = 'ODBC Driver 18 for SQL Server'
    connection_string = f"Driver={driver};Server={SQL_SERVER};Database={SQL_DATABASE};Uid={SQL_USER};Pwd={SQL_PASSWORD};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    return connection_string

def preprocess_for_inference(df):
    drop_cols = [
        'customer_id', 'count', 'zip_code', 'lat_long', 'surname', 'rownumber',
        'state', 'city', 'latitude', 'longitude', 'churn_reason', 'churn_score',
        'churn_value', 'geography'
    ]
    df = df.drop(columns=[col for col in drop_cols if col in df.columns], errors='ignore')

    if 'churn' in df.columns:
        df['churn'] = df['churn'].astype(str).str.lower().map({
            'yes': 1, 'no': 0, 'true': 1, 'false': 0, '1': 1, '0': 0
        }).fillna(0).astype(int)

    binary_categoricals = [
        'gender', 'senior_citizen', 'partner', 'dependents', 'phone_service', 
        'paperless_billing', 'complain', 'maritalstatus'
    ]
    le = LabelEncoder()
    for col in binary_categoricals:
        if col in df.columns:
            df[col] = df[col].fillna('No')
            df[col] = le.fit_transform(df[col].astype(str))

    multi_cat_cols = [
        'internet_service', 'online_security', 'online_backup', 'device_protection',
        'tech_support', 'streaming_tv', 'streaming_movies', 'payment_method', 
        'contract', 'preferredlogindevice', 'preferedordercat', 'preferredpaymentmode'
    ]
    for col in multi_cat_cols:
        if col in df.columns:
            df[col] = df[col].fillna('Unknown')

    df = pd.get_dummies(df, columns=[col for col in multi_cat_cols if col in df.columns])

    for col in df.select_dtypes(include='object').columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df.fillna(df.median(numeric_only=True), inplace=True)

    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    num_cols = [col for col in num_cols if col != 'churn']
    scaler = StandardScaler()
    df[num_cols] = scaler.fit_transform(df[num_cols])

    return df

def ChurnPredictionsModels(df):
   
    preprocessed_data = preprocess_for_inference(df)

    # === Drop extra columns and ensure correct order ===
    preprocessed_data = preprocessed_data.reindex(columns=column_names, fill_value=0)

    # === Encode any remaining label-encoded fields ===
    for col, le in label_encoders.items():
        if col in preprocessed_data.columns:
            preprocessed_data[col] = le.transform(preprocessed_data[col].astype(str))

    # === Final Scaling with trained scaler ===
    preprocessed_data.replace([np.inf, -np.inf], np.nan, inplace=True)
    preprocessed_data.fillna(0, inplace=True)
    inference_data_scaled = scaler.transform(preprocessed_data)

    # === Meta-model prediction ===
    meta_features = np.zeros((inference_data_scaled.shape[0], 2))
    meta_features[:, 0] = gbr_model.predict(inference_data_scaled)
    meta_features[:, 1] = rf_model.predict(inference_data_scaled)

    final_preds = meta_model.predict(meta_features)
    final_probs = meta_model.predict_proba(meta_features)[:, 1]

    return final_preds, final_probs



connection_string = ConnectionString()

def main(mytimer: TimerRequest) -> None:
    #utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    print("Timer trigger function ran.")
    logging.info("Timer trigger function ran.")
    try:
        conn = pyodbc.connect(connection_string)

        cursor = conn.cursor()

        # Fetch rows where churn prediction is not yet processed
        cursor.execute("SELECT TOP 1000 * FROM ChurnTable WHERE Processed=0")
        rows = cursor.fetchall()  # by using fetchall, all the rows are returned as tuples, not objects with attributes

        # If there are no new records to process, log and exit
        if not rows:
            print("No unprocessed churn data found")
            logging.info("No unprocessed churn data found.")
            return

        # Prepare batch dataframe
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame.from_records(rows, columns=columns)
        # Getting final predictions and probability 
        
        final_preds, final_probs = ChurnPredictionsModels(df)
        max_prob = max(final_probs)
        if max_prob > 0.7:
            threshold = 0.5
        elif max_prob > 0.4:
            threshold = 0.3
        else:
            threshold = 0.1  
        final_preds = (final_probs >= threshold).astype(int)

        print("Predictions:", final_preds)
        print("Prediction Probabilities:", final_probs)

        df['PredictedChurn'] =  final_preds
        df['ChurnProbability'] = final_probs
        df['Processed'] = 1 
        #df.to_csv("inference_results.csv", index=False)
        #print("[] Inference results saved to inference_results.csv")
       
        num_samples = len(df['PredictedChurn'])
        num_churned = sum(df['PredictedChurn'])
        churn_rate = (num_churned / num_samples) * 100
 
        print("\n=== Churn Prediction Summary ===")
        print(f"Total Customers Inferred: {num_samples}")
        print(f"Predicted to Churn: {num_churned}")
        print(f"Churn Rate: {churn_rate:.2f}%")

        for index, row in df.iterrows():
                    update_query = """
                        UPDATE ChurnTable
                        SET PredictedChurn = ?, ChurnProbability = ?, Processed = ?
                        WHERE customer_id = ?
                    """
                    cursor.execute(update_query, 
                        int(row['PredictedChurn']), 
                        float(row['ChurnProbability']), 
                        int(row['Processed']), 
                        row['customer_id']
                    )


        conn.commit()
        print(f"Successfully updated {len(df)} churn prediction records.")
        logging.info(f"Successfully updated {len(df)} churn prediction records.")
    except Exception as e:
        print(f"Churn processing failed: {e}")
        logging.error(f"Churn processing failed: {e}")
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

    if mytimer.past_due:
        logging.info('The timer is past due!')
 
    