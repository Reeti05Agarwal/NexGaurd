import pyodbc
import os
from dotenv import load_dotenv
import sys

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

action = sys.argv[1].lower()  # get the first argument, lowercase for safety

if action == "add":
    cursor.execute("ALTER TABLE ChurnTable ADD ChurnProbability FLOAT NOT NULL DEFAULT 0;")
    cursor.execute("ALTER TABLE ChurnTable ADD PredictedChurn INT NOT NULL DEFAULT 0;")
    cursor.execute("ALTER TABLE ChurnTable ADD Processed BIT NOT NULL DEFAULT 0;")

    conn.commit()
    print("Column 'Processed' added successfully!")
if action == "drop":
    for column_name in ['Processed', 'PredictedChurn', 'ChurnProbability']:
        cursor.execute(f"""
            DECLARE @ConstraintName NVARCHAR(200)
            SELECT @ConstraintName = dc.name
            FROM sys.default_constraints dc
            INNER JOIN sys.columns c ON c.default_object_id = dc.object_id
            WHERE c.object_id = OBJECT_ID('ChurnTable') AND c.name = '{column_name}'

            IF @ConstraintName IS NOT NULL
            BEGIN
                EXEC('ALTER TABLE ChurnTable DROP CONSTRAINT ' + @ConstraintName)
            END
        """)
    conn.commit()

    
    # Now drop the column
    cursor.execute("ALTER TABLE ChurnTable DROP COLUMN Processed;")
    conn.commit()
    
    print("Column 'Processed' and its constraint dropped successfully!")

 

cursor.close()
conn.close()
