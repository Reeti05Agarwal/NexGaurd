# import os
# from dotenv import load_dotenv
# load_dotenv()
# from uploadingTable.churnTables.checkingChurn import checkingChurnTable 


# churn_df = checkingChurnTable()   

# def ConnectionString():

#     SQL_SERVER = os.getenv("SQL_SERVER")
#     SQL_DATABASE = os.getenv("SQL_DATABASE")
#     SQL_USER = os.getenv("SQL_USER")
#     SQL_PASSWORD = os.getenv("SQL_PASSWORD")
#     driver = 'ODBC Driver 18 for SQL Server'
#     connection_string = f"Driver={driver};Server={SQL_SERVER};Database={SQL_DATABASE};Uid={SQL_USER};Pwd={SQL_PASSWORD};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
#     return connection_string

# num_samples, num_churned, churn_rate, num_nochurned = print_churn_results(churn_df)
# churn_pie = num_churned / num_samples * 100
# not_churn_pie = num_nochurned / num_samples * 100
# churn_table = df_to_flet_table(churn_df)  