import pyodbc
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve SQL Database connection details from environment variables
SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USER = os.getenv("SQL_USER")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")
driver = 'ODBC Driver 18 for SQL Server'

# Create the connection string
connection_string = f"Driver={driver};Server={SQL_SERVER};Database={SQL_DATABASE};Uid={SQL_USER};Pwd={SQL_PASSWORD};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

try:
    # Attempt to connect to the database
    conn = pyodbc.connect(connection_string)
    print("Connected to Azure SQL Database successfully!")
    conn.close()  # Close connection if successful
except Exception as e:
    print(f"Failed to connect to Azure SQL Database: {str(e)}")
