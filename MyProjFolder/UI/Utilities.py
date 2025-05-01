import flet as ft
import pandas as pd
import matplotlib.pyplot as plt 
import pyodbc
import json
import os
from dotenv import load_dotenv
from uploadingTable.churnTables.checkingChurn import checkingChurnTable
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
                ft.Text(title, size=24, weight="bold", color="black"),
                ft.Text(description, size=18, color="black"),
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


def print_churn_results(churn_df):
    num_samples = len(churn_df['PredictedChurn'])
    processed=churn_df['Processed'].astype(int).sum()
    num_churned = sum(churn_df['PredictedChurn'])
    churn_rate = (num_churned / processed) * 100
    num_nochurned = processed - num_churned
    return num_samples, num_churned, churn_rate, num_nochurned, processed

def print_fraud_results(fraud_df):
    logistic = fraud_df['LogisticPrediction']
    randomforest = fraud_df['RandomForestPrediction']
    meta = fraud_df['MetaPrediction']
    fraud_samples = len(fraud_df['MetaPrediction'])
    num_fraud = sum(fraud_df['MetaPrediction'])
    num_no_fraud = fraud_samples - num_fraud
    fraud_rate = (num_fraud / fraud_samples) * 100 

    return fraud_samples, num_fraud, fraud_rate, num_no_fraud

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

def plot_churn_rate(churn_pie, not_churn_pie):
    total = churn_pie + not_churn_pie

    def on_churn_chart_event(e: ft.PieChartEvent):
        for idx, section in enumerate(churn_chart.sections):
            if idx == e.section_index:
                percent = round((section.value / total) * 100, 1)
                section.title = f"{section.title.split()[0]} {percent}%"
                section.radius = hover_radius
                section.title_style = hover_title_style
            else:
                section.title = section.title.split()[0]  # reset to original label
                section.radius = normal_radius
                section.title_style = normal_title_style
        churn_chart.update()

    churn_chart = ft.PieChart(
        sections=[
            ft.PieChartSection(
                value=churn_pie,
                title="Churn",
                title_style=normal_title_style,
                color=ft.Colors.RED,
                radius=normal_radius,
            ),
            ft.PieChartSection(
                value=not_churn_pie,
                title="Retain",
                title_style=normal_title_style,
                color=ft.Colors.GREEN,
                radius=normal_radius,
            )
        ],
        sections_space=0,
        center_space_radius=40,
        on_chart_event=on_churn_chart_event,
        expand=True,
    )

    return churn_chart

def plot_churn_reasons(df):
    churn_reasons = df['churn_reason'].value_counts().items()
    if not churn_reasons:
        return ft.Text("No churn reasons data available.")
    
    churn_reasons_list = list(churn_reasons)
    max_y_value = max([count for _, count in churn_reasons_list]) + 10
    
    bar_width = 30 
    spacing = 10
    bar_groups = []
    for idx, (reason, count) in enumerate(churn_reasons_list):         
        bar_groups.append(
            ft.BarChartGroup(
                x=idx,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=count,
                        width=bar_width,
                        color=ft.Colors.DEEP_PURPLE_400,
                        tooltip=reason,
                        border_radius=5,
                    ),
                ],
            )
        )  
    chart = ft.BarChart(
        bar_groups=bar_groups,
        border=ft.border.all(1, ft.Colors.GREY_400),
        left_axis=ft.ChartAxis(labels_size=40, title=ft.Text("Churn Reasons Count"), title_size=40),
        bottom_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(value=i, label=ft.Container(ft.Text(reason), padding=10))
                for i, (reason, _) in enumerate(churn_reasons_list)  # Ensure this is over churn_reasons_list
            ],
            labels_size=18,
        ),
        horizontal_grid_lines=ft.ChartGridLines(color=ft.Colors.WHITE10, width=1, dash_pattern=[3, 3]),
        tooltip_bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.WHITE54),
        tooltip_fit_inside_horizontally=True,
        tooltip_fit_inside_vertically=True,
        max_y=max_y_value,
        interactive=True,
        expand=True,
    )
    return chart

def plot_sentiment_trends(df):
    if 'satisfactionscore' not in df.columns:
        return ft.Text("Missing 'satisfactionscore' column", color=ft.Colors.RED)

    df = df[['satisfactionscore']].dropna().reset_index()
    df['bucket'] = (df.index // 20) * 20

    trend_df = df.groupby('bucket').agg({'satisfactionscore': 'mean'}).reset_index()

    if trend_df.shape[0] < 2:
        return ft.Text("Not enough variation to display a trend.", color=ft.Colors.RED)

    data_points = [
        ft.LineChartDataPoint(x=int(row['bucket']), y=float(row['satisfactionscore']))
        for _, row in trend_df.iterrows()
    ]

    x_labels = [
        ft.ChartAxisLabel(value=int(row['bucket']), label=ft.Container(ft.Text(str(int(row['bucket'])), size=12)))
        for _, row in trend_df.iterrows()
    ]

    y_labels = [
        ft.ChartAxisLabel(value=v, label=ft.Container(ft.Text(str(v), size=12)))
        for v in range(1, 6)
    ]

    chart = ft.LineChart(
        data_series=[
            ft.LineChartData(
                data_points=data_points,
                stroke_width=3,
                color=ft.Colors.BLUE,
                curved=True,
                stroke_cap_round=True,
            )
        ],
        border=ft.border.all(1, ft.Colors.GREY_400),
        left_axis=ft.ChartAxis(
            labels=y_labels,
            labels_size=40,
            title=ft.Text("Average Satisfaction Score"),
            title_size=40,
        ),
        bottom_axis=ft.ChartAxis(
            labels=x_labels,
            labels_size=40,
            title=ft.Text("Feedback Bucket"),
            title_size=40,
        ),
        horizontal_grid_lines=ft.ChartGridLines(color=ft.Colors.WHITE10, width=1, dash_pattern=[3, 3]),
        vertical_grid_lines=ft.ChartGridLines(color=ft.Colors.WHITE10, width=1, dash_pattern=[3, 3]),
        tooltip_bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.WHITE54),
        tooltip_fit_inside_horizontally=True,
        tooltip_fit_inside_vertically=True,
        min_y=0,
        max_y=5,
        min_x=trend_df['bucket'].min(),
        max_x=trend_df['bucket'].max(),
        expand=True,
        interactive=True,
    )

    return chart

def plot_cltv_distribution(df):
    if 'cltv' not in df.columns:
        return ft.Text("Missing 'cltv' column", color=ft.Colors.RED)

    cltv_data = df['cltv'].dropna()
    bin_ranges = pd.cut(cltv_data, bins=10)
    counts = bin_ranges.value_counts().sort_index()

    bar_groups = []
    x_labels = []

    for idx, (interval, count) in enumerate(counts.items()):
        label = f"{interval.left:.1f}–{interval.right:.1f}"
        bar_groups.append(
            ft.BarChartGroup(
                x=idx,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=count,
                        width=30,
                        color=ft.Colors.GREEN_ACCENT_400,
                        tooltip=label,
                        border_radius=5,
                    )
                ],
            )
        )
        x_labels.append(
            ft.ChartAxisLabel(
                value=idx,
                label=ft.Container(ft.Text(label, size=10), padding=5)
            )
        )

    chart = ft.BarChart(
        bar_groups=bar_groups,
        border=ft.border.all(1, ft.Colors.GREY_400),
        left_axis=ft.ChartAxis(
            labels_size=40,
            title=ft.Text("Customer Count"),
            title_size=40
        ),
        bottom_axis=ft.ChartAxis(
            labels=x_labels,
            labels_size=30,
            title=ft.Text("CLTV Range"),
            title_size=40
        ),
        horizontal_grid_lines=ft.ChartGridLines(color=ft.Colors.WHITE10, width=1, dash_pattern=[3, 3]),
        tooltip_bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.WHITE54),
        tooltip_fit_inside_horizontally=True,
        tooltip_fit_inside_vertically=True,
        max_y=max(counts) + 20,
        expand=True,
        interactive=True,
    )

    return chart

def plot_churn_over_tenure(df):
    if 'tenure_months' not in df.columns or 'churn' not in df.columns:
        return ft.Text("Missing 'tenure_months' or 'churn' column", color=ft.Colors.RED)

    churn_rate = df.groupby('tenure_months')['churn'].mean()
    fake_months = list(range(0, 73, max(1, 73 // len(churn_rate))))
    norm_to_fake_month = dict(zip(sorted(churn_rate.index), fake_months[:len(churn_rate)]))

    data_points = [
        ft.LineChartDataPoint(x=norm_to_fake_month[tenure], y=rate)
        for tenure, rate in churn_rate.items()
    ]

    x_labels = [
        ft.ChartAxisLabel(value=fake_month, label=ft.Container(ft.Text(str(fake_month), size=12)))
        for fake_month in range(0, 73, 6)
    ]

    y_labels = [
        ft.ChartAxisLabel(value=y, label=ft.Container(ft.Text(f"{int(y * 100)}%", size=12)))
        for y in [i / 10 for i in range(0, 11)]
    ]

    chart = ft.LineChart(
        data_series=[ft.LineChartData(data_points, color=ft.Colors.PINK)],
        border=ft.border.all(1, ft.Colors.GREY_400),
        left_axis=ft.ChartAxis(
            labels=y_labels,
            labels_size=40,
            title=ft.Text("Churn Probability (%)"),
            title_size=40,
        ),
        bottom_axis=ft.ChartAxis(
            labels=x_labels,
            labels_size=40,
            title=ft.Text("Tenure (Months)"),
            title_size=40,
        ),
        horizontal_grid_lines=ft.ChartGridLines(color=ft.Colors.WHITE10, width=1, dash_pattern=[3, 3]),
        vertical_grid_lines=ft.ChartGridLines(color=ft.Colors.WHITE10, width=1, dash_pattern=[3, 3]),
        tooltip_bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.WHITE54),
        min_y=0,
        max_y=1,
        min_x=0,
        max_x=72,
        interactive=True,
        expand=True,
    )
    return chart


# def plot_purchase_behavior(df):
#     # Extract relevant columns for purchase behavior
#     conversion_rate = df['conversion_rate'].mean()
#     aov = df['average_order_value'].mean()
#     abandoned_cart_rate = df['abandoned_cart_rate'].mean()
    
#     labels = ["Conversion Rate", "Average Order Value", "Abandoned Cart Rate"]
#     values = [conversion_rate, aov, abandoned_cart_rate]
    
#     bar_groups = [
#         ft.BarChartGroup(
#             x=idx,
#             bar_rods=[ft.BarChartRod(
#                 from_y=0,
#                 to_y=value,
#                 width=40,
#                 color=ft.Colors.GREEN if idx == 0 else ft.Colors.RED,
#                 tooltip=label,
#                 border_radius=0,
#             )],
#         )
#         for idx, (label, value) in enumerate(zip(labels, values))
#     ]

#     chart = ft.BarChart(
#         bar_groups=bar_groups,
#         border=ft.border.all(1, ft.Colors.GREY_400),
#         left_axis=ft.ChartAxis(labels_size=40, title=ft.Text("Metric Value"), title_size=40),
#         bottom_axis=ft.ChartAxis(
#             labels=[ft.ChartAxisLabel(value=i, label=ft.Container(ft.Text(label), padding=10))
#                     for i, label in enumerate(labels)],
#             labels_size=20,
#         ),
#         horizontal_grid_lines=ft.ChartGridLines(color=ft.Colors.GREY_300, width=1, dash_pattern=[3, 3]),
#         tooltip_bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.GREY_300),
#         max_y=max(values) + 10,
#         interactive=True,
#         expand=True,
#     )
#     return chart

# def plot_customer_segments(df):
#     # Extract customer segment data
#     customer_segments = df['customer_segment'].value_counts().items()
    
#     chart = ft.PieChart(
#         segments=[ft.PieChartSegment(
#             value=value,
#             label=segment,
#             color=ft.Colors.GREEN if idx % 2 == 0 else ft.Colors.RED,
#         ) for idx, (segment, value) in enumerate(customer_segments)],
#         expand=True,
#     )
#     return chart

# def plot_predictive_analytics(df):
#     # Assuming predictive columns are in the DataFrame
#     predicted_growth = df['predicted_sales_growth'].mean()
#     predicted_churn_rate = df['predicted_churn_rate'].mean()
    
#     chart = ft.LineChart(
#         line_series=[
#             ft.LineChartSeries(
#                 name="Predicted Sales Growth",
#                 data=[ft.LineChartDataPoint(x=0, y=predicted_growth)],
#                 color=ft.Colors.BLUE,
#                 tooltip="Predicted Sales Growth"
#             ),
#             ft.LineChartSeries(
#                 name="Predicted Churn Rate",
#                 data=[ft.LineChartDataPoint(x=1, y=predicted_churn_rate)],
#                 color=ft.Colors.RED,
#                 tooltip="Predicted Churn Rate"
#             ),
#         ],
#         border=ft.border.all(1, ft.Colors.GREY_400),
#         left_axis=ft.ChartAxis(labels_size=20, title="Growth / Churn Rate", title_size=20),
#         bottom_axis=ft.ChartAxis(labels=["Q1", "Q2"], labels_size=12),
#         horizontal_grid_lines=ft.ChartGridLines(color=ft.Colors.GREY_300, width=1, dash_pattern=[3, 3]),
#         tooltip_bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.GREY_300),
#         max_y=max(predicted_growth, predicted_churn_rate) + 10,
#         interactive=True,
#         expand=True,
#     )
#     return chart

# Generate Customer Report
def generate_customer_report():
    df = checkingChurnTable()   
    num_samples, num_churned, churn_rate, num_nochurned, processed= print_churn_results(df)
    churn_pie = num_churned / processed * 100
    not_churn_pie = num_nochurned / processed * 100
    report= ft.Container(
        bgcolor=ft.Colors.BLACK87,
        padding=10,
        border_radius=15,
        content=ft.Column(
            controls=[                
                ft.ResponsiveRow(
                    expand=True,
                    controls=[
                        ft.Container(
                            content=create_content_block(
                                "Churn Analysis",
                                f"Total Number of Records: {num_samples} \n"
                                f"Scanned Records: {processed}\n"
                                f"Churned Records: {num_churned} \n"
                                f"No Churn Records: {num_nochurned} \n"
                                f"Churn Rate: {churn_rate:.2f}%",
                                ft.Colors.TEAL_100,
                                ft.Colors.TEAL_300
                            ),
                            border_radius=15,
                            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.TEAL_300),  
                            col={"sm": 12, "md": 6, "xl": 6},  
                            expand=True,
                            height=300,
                        ),
                        ft.Container(
                            content=plot_churn_rate(churn_pie, not_churn_pie),
                            border_radius=15,
                            bgcolor=ft.Colors.BLACK54,
                            col={"sm": 12, "md": 6, "xl": 6},  
                            expand=True,
                            height=300,
                        ),
                    ]
                ),
                ft.Text("Executive Summary", size=24, weight="bold", color=ft.Colors.WHITE70),

                ft.Text("Customer Churn Analysis", size=20, weight="bold", color=ft.Colors.WHITE70),

                ft.ResponsiveRow(
                    controls=[
                        ft.Container(
                            content=plot_churn_reasons(df),
                            padding=10,
                            border_radius=15,
                            expand=True,
                            bgcolor=ft.Colors.BLACK54
                        ),
                    ]
                ),
                
                ft.Text("Customer Satisfaction & Sentiment Analysis", size=20, weight="bold", color=ft.Colors.WHITE70),
                # Sentiment Trends Line Chart
                ft.ResponsiveRow(
                    controls=[
                        ft.Container(
                            content=plot_sentiment_trends(df),
                            padding=10,
                            border_radius=15,
                            expand=True,
                            bgcolor=ft.Colors.BLACK54
                        ),
                    ]
                ),

                ft.Text("Churn Rate v/s Customer's Tenure Analysis", size=20, weight="bold", color=ft.Colors.WHITE70),
                # Sentiment Trends Line Chart
                ft.ResponsiveRow(
                    controls=[
                        ft.Container(
                            content=plot_churn_over_tenure(df),
                            padding=10,
                            border_radius=15,
                            expand=True,
                            bgcolor=ft.Colors.BLACK54
                        ),
                    ]
                ),

                ft.Text("Customer Lifetime Value Analysis", size=20, weight="bold", color=ft.Colors.WHITE70),
                # Sentiment Trends Line Chart
                ft.ResponsiveRow(
                    controls=[
                        ft.Container(
                            content=plot_cltv_distribution(df),
                            padding=10,
                            border_radius=15,
                            expand=True,
                            bgcolor=ft.Colors.BLACK54
                        ),
                    ]
                ),
            ]
        )
    )
    return report
