import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os
from dotenv import load_dotenv



def ConnectionString():

    SQL_SERVER = os.getenv("SQL_SERVER")
    SQL_DATABASE = os.getenv("SQL_DATABASE")
    SQL_USER = os.getenv("SQL_USER")
    SQL_PASSWORD = os.getenv("SQL_PASSWORD")
    driver = 'ODBC Driver 18 for SQL Server'
    connection_string = f"Driver={driver};Server={SQL_SERVER};Database={SQL_DATABASE};Uid={SQL_USER};Pwd={SQL_PASSWORD};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    return connection_string

# Load environment variables
load_dotenv()

# Read CSV file
df = pd.read_csv("x_test_inference.csv", low_memory=False)


connection_string = ConnectionString()

# Use URL encoding for the connection string
encoded_connection_string = quote_plus(connection_string)

# Create SQLAlchemy engine
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={encoded_connection_string}")

# Upload DataFrame to a new table (replace if exists)
try:
    df.to_sql('FraudTable', con=engine, index=False, if_exists='replace')
    print("Data uploaded to Azure SQL Database successfully!")
except Exception as e:
    print(f"Failed to upload data: {str(e)}")
