import logging
import pyodbc
from azure.functions import TimerRequest
from datetime import datetime, timezone
from dotenv import load_dotenv 
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.preprocessing import StandardScaler, LabelEncoder

def ConnectionString():

    SQL_SERVER = os.getenv("SQL_SERVER")
    SQL_DATABASE = os.getenv("SQL_DATABASE")
    SQL_USER = os.getenv("SQL_USER")
    SQL_PASSWORD = os.getenv("SQL_PASSWORD")
    driver = 'ODBC Driver 18 for SQL Server'
    connection_string = f"Driver={driver};Server={SQL_SERVER};Database={SQL_DATABASE};Uid={SQL_USER};Pwd={SQL_PASSWORD};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    return connection_string

def FraudPredictionModels(X_test_df):
    try:
        scaler = joblib.load("Models/FraudModels/scaler.pkl")
        print("[Fraud] Scaler loaded successfully.")
    except Exception as e:
        logging.error(f"[Fraud] Failed to load scaler: {e}")
        raise

    try:
        label_encoders = joblib.load("Models/FraudModels/label_encoder.pkl")
        print("[Fraud] Label encoders loaded successfully.")
    except Exception as e:
        logging.error(f"[Fraud] Failed to load label encoders: {e}")
        raise

    try:
        X_train_columns = np.load("Models/FraudModels/x_column_names.npy", allow_pickle=True).tolist()
        print("[Fraud] Training column names loaded successfully.")
    except Exception as e:
        logging.error(f"[Fraud] Failed to load training column names: {e}")
        raise

    try:
        lr_model = joblib.load("Models/FraudModels/lr_model.pkl")
        print("[Fraud] Logistic Regression model loaded successfully.")
    except Exception as e:
        logging.error(f"[Fraud] Failed to load Logistic Regression model: {e}")
        raise

    try:
        rf_model = joblib.load("Models/FraudModels/rf_model.pkl")
        print("[Fraud] Random Forest model loaded successfully.")
    except Exception as e:
        logging.error(f"[Fraud] Failed to load Random Forest model: {e}")
        raise

    try:
        meta_model = joblib.load("Models/FraudModels/meta_model.pkl")
        print("[Fraud] Meta model loaded successfully.")
    except Exception as e:
        logging.error(f"[Fraud] Failed to load Meta model: {e}")
        raise

    # Save original TransactionID if exists
    transaction_ids = X_test_df["TransactionID"] if "TransactionID" in X_test_df.columns else pd.Series([f"Index_{i}" for i in range(len(X_test_df))])

    # Add missing columns
    for col in X_train_columns:
        if col not in X_test_df.columns:
            X_test_df[col] = 0

    # Drop unexpected columns
    extra_cols = [col for col in X_test_df.columns if col not in X_train_columns]
    if extra_cols:
        # print(f"Dropping unexpected columns: {extra_cols}")
        X_test_df.drop(columns=extra_cols, inplace=True)

    # Reorder columns to match training set
    X_test_df = X_test_df[X_train_columns]

    # Properly encode categorical columns
    for col in label_encoders:
        if col in X_test_df.columns:
            le = label_encoders[col]
            test_vals = X_test_df[col].astype(str)
            le_classes = list(le.classes_)
            if 'unknown' not in le_classes:
                le_classes.append('unknown')
                le.classes_ = np.array(le_classes)
            X_test_df[col] = test_vals.map(lambda x: x if x in le_classes else 'unknown')
            X_test_df[col] = le.transform(X_test_df[col])

    # Check for missing expected columns
    missing_cols = set(X_train_columns) - set(X_test_df.columns)
    for col in missing_cols:
        #print(f"Adding missing column: {col} (filled with 0s)")
        X_test_df[col] = 0

    # Ensure the DataFrame has all expected columns in correct order
    X_test_df = X_test_df[X_train_columns]

    # Convert all to numeric
    X_test_df = X_test_df.apply(pd.to_numeric, errors='coerce')

    # Check for NaNs
    if X_test_df.isnull().any().any():
        print("Found NaN values after numeric conversion:")
        print(X_test_df.isnull().sum()[X_test_df.isnull().sum() > 0])
        X_test_df.fillna(0, inplace=True)

    # Scale features
    X_test_scaled = scaler.transform(X_test_df)

    # Predict
    lr_predictions = (lr_model.predict_proba(X_test_scaled)[:, 1] > 0.5).astype(int)
    rf_predictions = rf_model.predict(X_test_scaled)
    meta_input = np.column_stack([lr_predictions, rf_predictions])
    meta_predictions = (meta_model.predict(meta_input) < 0.3).astype(int)


    return lr_predictions, rf_predictions, meta_input, meta_predictions, transaction_ids

load_dotenv()

connection_string = ConnectionString()


def main(mytimer: TimerRequest) -> None:
    #utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()

    try:
        print("Fraud timer trigger started.")
        logging.info("Fraud timer trigger started.")
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor() 

        cursor.execute("SELECT * FROM FraudTable WHERE Processed = 0")
        rows = cursor.fetchall()

        if not rows:
            logging.info("No unprocessed fraud data found.")
            return

        columns = [col[0] for col in cursor.description]
        X_test_df = pd.DataFrame.from_records(rows, columns=columns)
        lr_predictions, rf_predictions, meta_input, meta_predictions, transaction_ids = FraudPredictionModels(X_test_df)

        #Optional: check probability outputs
        logging.info("\nPredictions completed successfully.")
        logging.info(f"Logistic Regression Predictions: {lr_predictions[:10]}")
        logging.info(f"Random Forest Predictions: {rf_predictions[:10]}")
        logging.info(f"Meta Model Predictions: {meta_predictions[:10]}")
        # Save predictions
        X_test_df['LR_Prediction'] = lr_predictions
        X_test_df['RF_Prediction'] = rf_predictions
        X_test_df['Meta_Prediction'] = meta_predictions
        X_test_df['TransactionID'] = transaction_ids
        X_test_df.to_csv("predictions_output.csv", index=False)
        print("Predictions saved to predictions_output.csv.")

        # Print readable results
        print("\nDetailed Prediction Results:")
        for i in range(len(meta_predictions)):
            tx_id = transaction_ids.iloc[i]
            verdict = "YES" if meta_predictions[i] == 1 else "NO"
            print(f"TransactionID: {tx_id} Fraud: {verdict}")

         
        for _, record in X_test_df.iterrows():
            TransactionID = record["TransactionID"]
            if "TransactionID" in record:
                cursor.execute("UPDATE FraudTable SET Processed=1 WHERE TransactionID=?", record["TransactionID"])
            else:
                logging.warning("Missing TransactionID for a record, skipping update.")



        conn.commit()
        print("All fraud predictions processed")
        logging.info("All fraud predictions processed.")

    except Exception as e:
        logging.error(f"Error in fraud prediction trigger: {e}")

    if mytimer and mytimer.past_due:
        logging.info('The timer is past due!')


 
