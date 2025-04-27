from fastapi import FastAPI
from azure.eventhub import EventHubConsumerClient
import json
import joblib
import pandas as pd
from dotenv import load_dotenv
import os
import numpy as np

'''
1. Initialises fast api
2. loads pre trained model
3. connects to azure event hub

4. parses json data from the event
5. converts it into dataframe
6. runs ai model to predict if its fraud or not
7. logs the prediction result to console
8. save prediction to azure sql (TO DO)
9. send the alerts/notification (TO DO)
'''
 

app = FastAPI()



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

# Event Hub connection
EVENT_CONNECTION_STR = os.getenv("EVENTHUB_CONNECTION_STRING")
EVENTHUB_NAME = os.getenv("EVENTHUB_NAME")

def on_event(partition_context, event):
    data = json.loads(event.body_as_str())
    df = pd.DataFrame([data])

    prediction = model.predict(df)[0]
    print(f"Transaction {data['transaction_id']} Prediction: {prediction}")

    # TODO: Save to DB, send alert if fraud

    partition_context.update_checkpoint(event)

@app.on_event("startup")
async def startup_event():
    client = EventHubConsumerClient.from_connection_string(
        EVENT_CONNECTION_STR, consumer_group="$Default", eventhub_name=EVENTHUB_NAME
    )
    client.receive(on_event=on_event, starting_position="-1")

@app.get("/")
def health():
    return {"status": "running"}
