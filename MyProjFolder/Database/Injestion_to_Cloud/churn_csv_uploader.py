import time
import pandas as pd
import sys, os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # points to MyProjFolder/Database
sys.path.append(BASE_DIR)
from db_config import get_connection
from mysql.connector import Error


CSV_PATH = "Data/churn_data.csv"
BATCH_SIZE = 10
SLEEP_SECONDS = 30

print("Starting CSV uploader...")

try:
    df = pd.read_csv(CSV_PATH, low_memory=False) 

    # Normalize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.replace("-", "_", regex=False)
        .str.replace(" ", "_", regex=False)
    )

    conn = get_connection()
    cursor = conn.cursor()

    # Get DB columns
    cursor.execute("DESCRIBE ChurnTable")
    db_columns = {row[0] for row in cursor.fetchall()}

    # Keep only valid columns
    df = df[[col for col in df.columns if col in db_columns]]

    columns = ",".join(f"`{col}`" for col in df.columns)
    placeholders = ",".join(["%s"] * len(df.columns))

    insert_sql = f"""
    INSERT INTO ChurnTable ({columns})
    VALUES ({placeholders})
    """

    pointer = 0

    while pointer < len(df):
        batch = df.iloc[pointer:pointer + BATCH_SIZE]

        for _, row in batch.iterrows():
            cursor.execute(insert_sql, tuple(row))

        conn.commit()
        pointer += BATCH_SIZE
        print(f"Uploaded {pointer} rows")
        time.sleep(SLEEP_SECONDS)


except KeyboardInterrupt:
    print("\n Upload stopped by user (Ctrl+C). Gracefully shutting down...")

except Error as e:
    print(f" Database error: {e}")
    if conn:
        conn.rollback()

except Exception as e:
    print(f"Unexpected error: {e}")

finally:
    try:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("Database connection closed safely.")
    except:
        pass