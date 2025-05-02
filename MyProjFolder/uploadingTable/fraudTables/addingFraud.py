import pyodbc
import os
import sys
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
if len(sys.argv) < 2:
    print("Please provide an argument: 'add' or 'drop'")
    sys.exit(1)

action = sys.argv[1].lower() 

if action == "add":
    cursor.execute("ALTER TABLE FraudTable ADD LR_Prediction FLOAT NOT NULL DEFAULT 0;")
    cursor.execute("ALTER TABLE FraudTable ADD RF_Prediction FLOAT NOT NULL DEFAULT 0;")
    cursor.execute("ALTER TABLE FraudTable ADD Meta_Prediction INT NOT NULL DEFAULT 0;")
    cursor.execute("ALTER TABLE FraudTable ADD Processed BIT NOT NULL DEFAULT 0;")
    conn.commit()
    print("Column 'Processed' added successfully!")
if action == "drop":
    for column_name in ['Processed', 'LR_Prediction', 'RF_Prediction', 'Meta_Prediction']:
        cursor.execute(f"""
            DECLARE @ConstraintName NVARCHAR(200)
            SELECT @ConstraintName = dc.name
            FROM sys.default_constraints dc
            INNER JOIN sys.columns c ON c.default_object_id = dc.object_id
            WHERE c.object_id = OBJECT_ID('FraudTable') AND c.name = '{column_name}'

            IF @ConstraintName IS NOT NULL
            BEGIN
                EXEC('ALTER TABLE FraudTable DROP CONSTRAINT ' + @ConstraintName)
            END
        """)
        cursor.execute(f"ALTER TABLE FraudTable DROP COLUMN {column_name};")
    conn.commit()

        
    print("Column 'Processed', 'LR_Prediction', 'RF_Prediction', 'Meta_Prediction' and its constraint dropped successfully!")

cursor.close()
conn.close()
