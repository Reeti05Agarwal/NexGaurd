import azure.functions as func
import pyodbc
import logging
import os
import json
from azure.eventhub import EventHubProducerClient, EventData
from dotenv import load_dotenv
from helpers import ConnectionString
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler, LabelEncoder

def FraudPredictionModels(X_test_df):
    scaler = joblib.load("scaler.pkl")
    label_encoders = joblib.load("label_encoder.pkl")
    X_train_columns = np.load("x_column_names.npy", allow_pickle=True).tolist()

    lr_model = joblib.load("lr_model.pkl")
    rf_model = joblib.load("rf_model.pkl")
    meta_model = joblib.load("meta_model.pkl") 

    # Save original TransactionID if exists
    transaction_ids = X_test_df["TransactionID"] if "TransactionID" in X_test_df.columns else pd.Series([f"Index_{i}" for i in range(len(X_test_df))])

    # Add missing columns
    for col in X_train_columns:
        if col not in X_test_df.columns:
            X_test_df[col] = 0

    # Drop unexpected columns
    extra_cols = [col for col in X_test_df.columns if col not in X_train_columns]
    if extra_cols:
        print(f"[!] Dropping unexpected columns: {extra_cols}")
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
        print(f"[!] Adding missing column: {col} (filled with 0s)")
        X_test_df[col] = 0

    # Ensure the DataFrame has all expected columns in correct order
    X_test_df = X_test_df[X_train_columns]

    # Convert all to numeric
    X_test_df = X_test_df.apply(pd.to_numeric, errors='coerce')

    # Check for NaNs
    if X_test_df.isnull().any().any():
        print("[!] Found NaN values after numeric conversion:")
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

def get_eventhub_client():
    return EventHubProducerClient.from_connection_string(
        conn_str=os.getenv("EVENT_HUB_CONNECTION_STRING"),
        eventhub_name=os.getenv("EVENT_HUB_NAME")
    )

app = func.FunctionApp()

@app.timer_trigger(schedule="0 */2 * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False)
def fraud_prediction_trigger(myTimer: func.TimerRequest) -> None:
    try:
        logging.info("Fraud timer trigger started.")
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor() 

        cursor.execute("SELECT * FROM FraudTable WHERE Processed = 0")
        rows = cursor.fetchall()

        if not rows:
            logging.info("No unprocessed fraud data found.")
            return

        columns = [col[0] for col in cursor.description]
        X_test_df = [dict(zip(columns, row)) for row in rows]
        lr_predictions, rf_predictions, meta_input, meta_predictions, transaction_ids = FraudPredictionModels(X_test_df)

        #Optional: check probability outputs
        logging.info("\n[✓] Predictions completed successfully.")
        logging.info(f"Logistic Regression Predictions: {lr_predictions[:10]}")
        logging.info(f"Random Forest Predictions: {rf_predictions[:10]}")
        logging.info(f"Meta Model Predictions: {meta_predictions[:10]}")
        # Save predictions
        X_test_df['LR_Prediction'] = lr_predictions
        X_test_df['RF_Prediction'] = rf_predictions
        X_test_df['Meta_Prediction'] = meta_predictions
        X_test_df['TransactionID'] = transaction_ids
        X_test_df.to_csv("predictions_output.csv", index=False)
        print("[✓] Predictions saved to predictions_output.csv.")

        # Print readable results
        print("\n[✓] Detailed Prediction Results:")
        for i in range(len(meta_predictions)):
            tx_id = transaction_ids.iloc[i]
            verdict = "YES" if meta_predictions[i] == 1 else "NO"
            print(f"TransactionID: {tx_id} → Fraud: {verdict}")

        # Convert to JSON string
        event_data_batch = [EventData(json.dumps(record)) for record in X_test_df]

        # Send to Event Hub
        producer = get_eventhub_client()
        with producer:
            event_batch = producer.create_batch()
            for data in event_data_batch:
                event_batch.add(data)
            producer.send_batch(event_batch)

        logging.info(f"Sent {len(X_test_df)} fraud records to Event Hub.")

        for record in X_test_df:
            customer_id = record.get("customer_id")
            cursor.execute("UPDATE FraudTable SET Processed=1 WHERE customer_id=?", customer_id)
        conn.commit()

    except Exception as e:
        logging.error(f"Error in fraud prediction trigger: {e}")

    if myTimer.past_due:
        logging.info("Fraud timer is past due.")
