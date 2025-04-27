import flet as ft
import matplotlib.pyplot as plt 
import pyodbc
import json
import os
from dotenv import load_dotenv
load_dotenv()


SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USER = os.getenv("SQL_USER")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")
driver = 'ODBC Driver 18 for SQL Server'
connection_string = f"Driver={driver};Server={SQL_SERVER};Database={SQL_DATABASE};Uid={SQL_USER};Pwd={SQL_PASSWORD};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"


def create_content_block(title, description, color, shadow_color):
        return ft.Container(
            content=ft.Column([
                ft.Text(title, size=20, weight="bold", color="black"),
                ft.Text(description, color="black"),
            ]),
            padding=20,
            bgcolor=color,
            border_radius=15,
            shadow=ft.BoxShadow(blur_radius=10, color=shadow_color),
            col={"sm": 12, "md": 6, "xl": 4},
        )
    

def df_to_flet_table(df):
    # Create DataTable columns from DataFrame headers
    columns = [ft.DataColumn(ft.Text(col)) for col in df.columns] 
    rows = [
        ft.DataRow(
            cells=[ft.DataCell(ft.Text(str(cell))) for cell in row]
        )
        for row in df.values
    ] 
    return ft.DataTable(columns=columns, rows=rows)


def print_churn_results():
    with open("churnResults.json", "r") as f:
        churn_results= json.load(f)
    num_samples = churn_results.get("num_samples", 0)
    num_churned = churn_results.get("num_churned", 0)
    churn_rate= churn_results.get("churn_rate", 0)
    return num_samples, num_churned, churn_rate

normal_radius = 50
hover_radius = 60
normal_title_style = ft.TextStyle(
    size=16, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD
)
hover_title_style = ft.TextStyle(
    size=22,
    color=ft.Colors.WHITE,
    weight=ft.FontWeight.BOLD,
    shadow=ft.BoxShadow(blur_radius=2, color=ft.Colors.BLACK54),
)

def connection_check():
    try:
        # Attempt to connect to the database
        conn = pyodbc.connect(connection_string)
        conn.close()  # Close connection if successful
        return True  # Connection successful
    except Exception as e:
        print(f"Failed to connect to Azure SQL Database: {str(e)}")
        return False  # Connection failed
    


# def on_chart_event(e: ft.PieChartEvent):
#         for idx, section in enumerate(chart.sections):
#             if idx == e.section_index:
#                 section.radius = hover_radius
#                 section.title_style = hover_title_style
#             else:
#                 section.radius = normal_radius
#                 section.title_style = normal_title_style
#         chart.update()

#     chart = ft.PieChart(
#         sections=[
#             ft.PieChartSection(
#                 num_churned,
#                 title="Churn",
#                 title_style=normal_title_style,
#                 color=ft.Colors.BLUE,
#                 radius=normal_radius,
#             ),
#             ft.PieChartSection(
#                 num_nochurned,
#                 title="No Churn",
#                 title_style=normal_title_style,
#                 color=ft.Colors.YELLOW,
#                 radius=normal_radius,
#             ) 
#         ],
#         sections_space=0,
#         center_space_radius=40,
#         on_chart_event=on_chart_event,
#         expand=True,
#     )