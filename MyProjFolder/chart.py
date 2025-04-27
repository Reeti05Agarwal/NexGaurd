import flet as ft
from uploadingTable.churnTables.checkingChurn import checkingChurnTable 
from uploadingTable.fraudTables.checkingFraud import checkingFraudTable
from UI.Utilities import create_content_block, print_fraud_results, df_to_flet_table, print_churn_results, connection_check


def main(page: ft.Page):


    fraud_df = checkingFraudTable()   
    fraud_samples, num_fraud, fraud_rate, num_no_fraud = print_fraud_results(fraud_df)
    fraud_pie = num_fraud / fraud_samples * 100
    not_fraud_pie = num_no_fraud / fraud_samples * 100
    #fraud_pie = round(fraud_pie, 2)
    fruad_table = df_to_flet_table(fraud_df)   
    churn_df = checkingChurnTable()   
    num_samples, num_churned, churn_rate, num_nochurned = print_churn_results(churn_df)
    churn_pie = num_churned / num_samples * 100
    not_churn_pie = num_nochurned / num_samples * 100
    churn_table = df_to_flet_table(churn_df)  

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

    def on_chart_event(e: ft.PieChartEvent):
        for idx, section in enumerate(chart.sections):
            if idx == e.section_index:
                section.radius = hover_radius
                section.title_style = hover_title_style
            else:
                section.radius = normal_radius
                section.title_style = normal_title_style
        chart.update()

    chart = ft.PieChart(
        sections=[
            ft.PieChartSection(
                fraud_pie,
                title="Fraud",
                title_style=normal_title_style,
                color=ft.Colors.BLUE,
                radius=normal_radius,
            ),
            ft.PieChartSection(
                not_fraud_pie,
                title="Not Fraud",
                title_style=normal_title_style,
                color=ft.Colors.YELLOW,
                radius=normal_radius,
            )
        ],
        sections_space=0,
        center_space_radius=40,
        on_chart_event=on_chart_event,
        expand=True,
    )

    page.add(chart)

ft.app(main)