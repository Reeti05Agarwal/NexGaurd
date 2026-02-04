import time
from MyProjFolder.Database.db_config import get_connection
from MyProjFolder.Models.fraud_inference import predict_fraud   # or churn model

POLL_INTERVAL = 60

print("⏱️ Inference trigger started...")

while True:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM FraudTable
        WHERE Processed = 0
        LIMIT 20
    """)
    rows = cursor.fetchall()

    if not rows:
        print("⏸️ No new records")
    else:
        for row in rows:
            prediction, probability = predict_fraud(row)

            cursor.execute("""
                UPDATE FraudTable
                SET
                    PredictedChurn = %s,
                    ChurnProbability = %s,
                    Processed = 1
                WHERE customer_id = %s
            """, (
                prediction,
                probability,
                row["customer_id"]
            ))

        print(f"⚡ Processed {len(rows)} records")

    cursor.close()
    conn.close()
    time.sleep(POLL_INTERVAL)
