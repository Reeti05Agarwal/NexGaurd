import azure.functions as func
import logging
import pyodbc
from .tx_func import send_to_eventhub  # Import the Event Hub sender
from dotenv import load_dotenv
import os
from helpers import ConnectionString
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler, LabelEncoder


    




connection_string = ConnectionString()
app = func.FunctionApp()

@app.timer_trigger(schedule="0 */5 * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False)
def fetchAndPush(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')

    try:
        # Connect to Azure SQL Database
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Transactions WHERE Processed=0")
        rows = cursor.fetchall()

        if not rows:
            logging.info("No unprocessed transactions found.")
            return

    
        columns = [column[0] for column in cursor.description]
        X_test_df = pd.DataFrame.from_records(rows, columns=columns)
        lr_predictions, rf_predictions, meta_input, meta_predictions = FraudPredictionModels(X_test_df)


        # Optional: check probability outputs
        print("\n[✓] Predictions completed successfully.")
        print(f"Logistic Regression Predictions: {lr_predictions[:10]}")
        print(f"Random Forest Predictions: {rf_predictions[:10]}")
        print(f"Meta Model Predictions: {meta_predictions[:10]}")
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

        # Send to Event Hub
        success = send_to_eventhub(row_dict)
        if success:
            # Mark transaction as processed in DB
            cursor.execute(
                "UPDATE Transactions SET Processed=1 WHERE TransactionID=?",
                row.TransactionID
            )
            conn.commit()
            logging.info(f"Transaction {row.TransactionID} sent and marked processed.")
        else:
            logging.warning(f"Transaction {row.TransactionID} failed to send.")

        logging.info("All fetched transactions processed successfully.")

    except Exception as e:
        logging.error(f"Error during transaction processing: {e}")
