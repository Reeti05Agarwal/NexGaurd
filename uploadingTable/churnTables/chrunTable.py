import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os
from helpers import ConnectionString

# Load environment variables
load_dotenv()

# Read CSV file
df = pd.read_csv("company_data.csv", low_memory=False)


connection_string = ConnectionString()

# Use URL encoding for the connection string
encoded_connection_string = quote_plus(connection_string)

# Create SQLAlchemy engine
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={encoded_connection_string}")

# Upload DataFrame to a new table (replace if exists)
try:
    df.to_sql('ChurnTable', con=engine, index=False, if_exists='replace')
    print("Data uploaded to Azure SQL Database successfully!")
except Exception as e:
    print(f"Failed to upload data: {str(e)}")
