import azure.functions as func
import pyodbc
import datetime
import json
import logging
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder, StandardScaler
import os
from dotenv import load_dotenv
load_dotenv()

global num_samples, num_churned, churn_rate

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

    # === Load models and encoders ===
    gbr_model = joblib.load("Models/Churn/gbr_model.pkl")
    rf_model = joblib.load("Models/Churn/rf_model.pkl")
    meta_model = joblib.load("Models/Churn/meta_model.pkl")

    label_encoders = joblib.load("Models/Churn/label_encoders.pkl")
    scaler = joblib.load("Models/Churn/scaler.pkl")
    column_names = np.load("Models/Churn/X_train_columns.npy", allow_pickle=True)
    
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
app = func.FunctionApp()

@app.timer_trigger(schedule="0 */1 * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def predictChurn(myTimer: func.TimerRequest) -> None:
    print("Timer trigger function ran.")
    logging.info("Timer trigger function ran.")
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Fetch rows where churn prediction is not yet processed
        cursor.execute("SELECT * FROM ChurnTable WHERE Processed=0")
        rows = cursor.fetchall()
        # by using fetchall, all the rows are returned as tuples, not objects with attributes

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

        print("Predictions:", final_preds)
        print("Prediction Probabilities:", final_probs)

        df['Prediction'] =  final_preds
        df['Probability'] = final_probs
        df.to_csv("inference_results.csv", index=False)
        print("[] Inference results saved to inference_results.csv")

        
        num_samples = len(final_preds)
        num_churned = sum(final_preds)
        churn_rate = (num_churned / num_samples) * 100
 
        print("\n=== Churn Prediction Summary ===")

        logging.info({
            "total_inferred": num_samples,
            "predicted_churned": num_churned,
            "churn_rate": churn_rate
        })

        print(f"Total Customers Inferred: {num_samples}")
        print(f"Predicted to Churn: {num_churned}")
        print(f"Churn Rate: {churn_rate:.2f}%")

        for row, prediction in zip(df.itertuples(index=False), final_preds):
            customer_id = getattr(row, 'customer_id')
            logging.info(f"Customer {customer_id} -> Churn: {prediction}")
            cursor.execute("UPDATE ChurnTable SET Processed=1 WHERE customer_id=?",
                        customer_id)


        conn.commit()
        print("All churn predictions processed")
        logging.info("All churn predictions processed.")
    except Exception as e:
        print(f"Churn processing failed: {e}")
        logging.error(f"Churn processing failed: {e}")
    
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')

@app.timer_trigger(schedule="0 */5 * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def fraud_prediction_trigger(myTimer: func.TimerRequest) -> None:
    
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')