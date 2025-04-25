import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

conn = pyodbc.connect(
    f"DRIVER=ODBC Driver 18 for SQL Server;"
    f"SERVER={os.getenv('SQL_SERVER')};"
    f"DATABASE={os.getenv('SQL_DATABASE')};"
    f"UID={os.getenv('SQL_USER')};"
    f"PWD={os.getenv('SQL_PASSWORD')};"
    f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
)

cursor = conn.cursor()
cursor.execute("ALTER TABLE FraudTable ADD Processed BIT NOT NULL DEFAULT 0;")
conn.commit()
print("Column 'Processed' added successfully!")
cursor.close()
conn.close()
