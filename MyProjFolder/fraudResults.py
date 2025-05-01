import os
from dotenv import load_dotenv
load_dotenv()
from uploadingTable.fraudTables.checkingFraud import checkingFraudTable


fraud_df = checkingFraudTable() 

def ConnectionString():

    SQL_SERVER = os.getenv("SQL_SERVER")
    SQL_DATABASE = os.getenv("SQL_DATABASE")
    SQL_USER = os.getenv("SQL_USER")
    SQL_PASSWORD = os.getenv("SQL_PASSWORD")
    driver = 'ODBC Driver 18 for SQL Server'
    connection_string = f"Driver={driver};Server={SQL_SERVER};Database={SQL_DATABASE};Uid={SQL_USER};Pwd={SQL_PASSWORD};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    return connection_string



logistic = fraud_df['LogisticPrediction']
randomforest = fraud_df['RandomForestPrediction']
meta = fraud_df['MetaPrediction']
fraud_samples = len(fraud_df['MetaPrediction'])
num_fraud = sum(fraud_df['MetaPrediction'])
num_no_fraud = fraud_samples - num_fraud
fraud_rate = (num_fraud / fraud_samples) * 100 