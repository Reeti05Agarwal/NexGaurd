from db_config import get_connection

conn = get_connection()
cursor = conn.cursor()

tables = ["ChurnTable", "FraudTable", "users"]

# --- Count rows ---
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]   # consume result
    print(f"📊 {table}: {count} rows")

# --- Churn sample ---
print("\nSample Unprocessed Churn Records:")
cursor.execute("""
    SELECT customer_id, Processed, PredictedChurn
    FROM ChurnTable
    WHERE Processed = 0
    LIMIT 5
""")
for row in cursor.fetchall():
    print(row)

# --- Fraud sample ---
print("\nSample Unprocessed Fraud Records:")
cursor.execute("""
    SELECT TransactionID, Meta_Prediction, Processed
    FROM FraudTable
    WHERE Processed = 0
    LIMIT 5
""")
for row in cursor.fetchall():
    print(row)

# --- Users sample ---
print("\nSample Users Records:")
cursor.execute("""
    SELECT id, email
    FROM users
    LIMIT 5
""")
for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()
