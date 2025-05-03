import flet as ft
import pandas as pd  
import pyodbc
import os
from dotenv import load_dotenv
from uploadingTable.churnTables.checkingChurn import checkingChurnTable
from uploadingTable.fraudTables.checkingFraud import checkingFraudTable
from uploadingTable.fraudTables.checkingFraud import checkingFraudTable
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
    
def create_card(title, description, color, shadow_color):
    return ft.Container(
        content=ft.Column([
            ft.Text(title, size=20, weight="bold", color="black"),
            ft.Text(description, color="black"),
        ],
        expand=True,               # Let column take full vertical space
        alignment=ft.MainAxisAlignment.START),  # Align content to top
        padding=20,
        bgcolor=color,
        border_radius=15,
        shadow=ft.BoxShadow(blur_radius=10, color=shadow_color),
        col={"sm": 12, "md": 6},
        expand=True               # Let card expand in its container
    )


def create_full_card(title, description, color, shadow_color):
    return ft.Container(
        content=ft.Column([
            ft.Text(title, size=20, weight="bold", color="black"),
            ft.Text(description, color="black"),
        ]),
        padding=20,
        bgcolor=color,
        border_radius=15,
        shadow=ft.BoxShadow(blur_radius=10, color=shadow_color),
        col={"sm": 12, "md": 12}
    )

def df_to_flet_table(df):
    columns = [ft.DataColumn(ft.Text(col)) for col in df.columns] 
    rows = [
        ft.DataRow(
            cells=[ft.DataCell(ft.Text(str(cell))) for cell in row]
        )
        for row in df.values
    ] 
    return ft.DataTable(columns=columns, rows=rows)

def return_flet_table():
    churn_df=checkingChurnTable(5)
    fraud_df=checkingFraudTable()
    return df_to_flet_table(churn_df), df_to_flet_table(fraud_df)


def print_churn_results(churn_df):
    num_samples = len(churn_df['PredictedChurn'])
    processed=churn_df['Processed'].astype(int).sum()
    num_churned = sum(churn_df['PredictedChurn'])
    churn_rate = (num_churned / processed) * 100
    num_nochurned = processed - num_churned
    return num_samples, num_churned, churn_rate, num_nochurned, processed

def print_fraud_results(fraud_df):
    logistic = fraud_df['LR_Prediction']
    randomforest = fraud_df['RF_Prediction']
    meta = fraud_df['Meta_Prediction']
    fraud_samples = len(fraud_df['Meta_Prediction'])
    num_fraud = sum(fraud_df['Meta_Prediction'])
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


def plot_fraud_rate(fraud_pie, not_fraud_pie):
    total = fraud_pie + not_fraud_pie

    def on_fraud_chart_event(e: ft.PieChartEvent):
        for idx, section in enumerate(fraud_chart.sections):
            if idx == e.section_index:
                percent = round((section.value / total) * 100, 1)
                section.title = f"{section.title.split()[0]} {percent}%"
                section.radius = hover_radius
                section.title_style = hover_title_style
            else:
                section.title = section.title.split()[0]
                section.radius = normal_radius
                section.title_style = normal_title_style
        fraud_chart.update()

    fraud_chart = ft.PieChart(
        sections=[
            ft.PieChartSection(
                fraud_pie,
                title="Fraud",
                title_style=normal_title_style,
                color=ft.Colors.RED,
                radius=normal_radius,
            ),
            ft.PieChartSection(
                not_fraud_pie,
                title="Not Fraud",
                title_style=normal_title_style,
                color=ft.Colors.GREEN,
                radius=normal_radius,
            )
        ],
        sections_space=0,
        center_space_radius=40,
        on_chart_event=on_fraud_chart_event,
        expand=True,
    )
    return fraud_chart
def plot_fraud_amt(df):
    if 'TransactionAmt' not in df.columns or 'Meta_Prediction' not in df.columns:
        return ft.Text("Required columns missing.", color=ft.Colors.RED)

    avg_amounts = df.groupby('Meta_Prediction')['TransactionAmt'].mean().items()

    bar_groups = []
    for idx, (fraud_label, avg_amt) in enumerate(avg_amounts):
        label = "Fraud" if fraud_label == 1 else "Not Fraud"
        color = ft.Colors.RED_ACCENT if fraud_label == 1 else ft.Colors.GREEN_ACCENT
        bar_groups.append(
            ft.BarChartGroup(
                x=idx,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=avg_amt,
                        width=30,
                        color=color,
                        tooltip=f"{label}: ${avg_amt:.2f}",
                        border_radius=5,
                    ),
                ],
            )
        )

    return ft.BarChart(
        bar_groups=bar_groups,
        border=ft.border.all(1, ft.Colors.GREY_400),
        left_axis=ft.ChartAxis(labels_size=40, title=ft.Text("Avg. Transaction Amt"), title_size=40),
        bottom_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(value=i, label=ft.Container(ft.Text("Fraud" if k == 1 else "Not Fraud")))
                for i, (k, _) in enumerate(avg_amounts)
            ],
            labels_size=20,
        ),
        horizontal_grid_lines=ft.ChartGridLines(color=ft.Colors.WHITE10, width=1, dash_pattern=[3, 3]),
        tooltip_bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.WHITE54),
        tooltip_fit_inside_horizontally=True,
        tooltip_fit_inside_vertically=True,
        interactive=True,
        expand=True,
    )

def plot_fraud_trend(df):
    if 'TransactionID' not in df.columns or 'Meta_Prediction' not in df.columns:
        return ft.Text("Required columns missing.", color=ft.Colors.RED)

    df = df[['TransactionID', 'Meta_Prediction']].copy()
    df['bucket'] = (df['TransactionID'] // 1000).astype(int)  # Smaller bucket size

    grouped = df.groupby('bucket')['Meta_Prediction'].sum().reset_index()

    if grouped.shape[0] < 2 or grouped['Meta_Prediction'].sum() == 0:
        return ft.Text("Not enough variation to display a trend.", color=ft.Colors.RED)

    data_points = [
        ft.LineChartDataPoint(x=int(row['bucket']), y=int(row['Meta_Prediction']))
        for _, row in grouped.iterrows()
    ]

    x_labels = [
        ft.ChartAxisLabel(value=int(row['bucket']), label=ft.Container(ft.Text(str(int(row['bucket'])))))
        for _, row in grouped.iterrows()
    ]

    return ft.LineChart(
        data_series=[
            ft.LineChartData(
                data_points=data_points,
                stroke_width=3,
                color=ft.Colors.RED,
                curved=True,
                stroke_cap_round=True,
            )
        ],
        border=ft.border.all(1, ft.Colors.GREY_400),
        left_axis=ft.ChartAxis(labels_size=40, title=ft.Text("Fraud Count"), title_size=40),
        bottom_axis=ft.ChartAxis(
            labels=x_labels,
            labels_size=40,
            title=ft.Text("Transaction Buckets"),
            title_size=40,
        ),
        horizontal_grid_lines=ft.ChartGridLines(color=ft.Colors.WHITE10, width=1, dash_pattern=[3, 3]),
        vertical_grid_lines=ft.ChartGridLines(color=ft.Colors.WHITE10, width=1, dash_pattern=[3, 3]),
        tooltip_bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.WHITE54),
        tooltip_fit_inside_horizontally=True,
        tooltip_fit_inside_vertically=True,
        min_y=0,
        max_y=grouped['Meta_Prediction'].max() + 1,
        min_x=grouped['bucket'].min(),
        max_x=grouped['bucket'].max(),
        interactive=True,
        expand=True,
    )




def plot_customer_behavior_trend(df):
    if 'step' not in df.columns or 'amount' not in df.columns:
        return ft.Text("Missing 'step' or 'amount' columns", color=ft.Colors.RED)

    df = df[['step', 'amount']].dropna().sort_values(by='step')
    grouped = df.groupby('step')['amount'].mean().reset_index()

    if grouped.shape[0] < 2:
        return ft.Text("Insufficient data for behavior trends.", color=ft.Colors.RED)

    data_points = [
        ft.LineChartDataPoint(x=row['step'], y=row['amount'])
        for _, row in grouped.iterrows()
    ]

    x_labels = [
        ft.ChartAxisLabel(value=row['step'], label=ft.Container(ft.Text(str(row['step']), size=12)))
        for _, row in grouped.iterrows()
    ]

    chart_amt = ft.LineChart(
        data_series=[
            ft.LineChartData(
                data_points=data_points,
                color=ft.Colors.GREEN,
                stroke_width=3,
                curved=True,
                stroke_cap_round=True,
            )
        ],
        left_axis=ft.ChartAxis(
            title=ft.Text("Avg. Amount"),
            labels_size=40,
            title_size=40
        ),
        bottom_axis=ft.ChartAxis(
            title=ft.Text("Time Step"),
            title_size=40,
            labels=x_labels,
            labels_size=40,
        ),
        border=ft.border.all(1, ft.Colors.GREY_400),
        tooltip_bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.WHITE54),
        min_y=0,
        max_y=float(grouped['amount'].max()) + 10,
        expand=True,
        interactive=True,
    )
    return chart_amt

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

def plot_fraud_chart(fraud_pie, not_fraud_pie):
    total=fraud_pie+not_fraud_pie
    def on_fraud_chart_event(e: ft.PieChartEvent):
        for idx, section in enumerate(fraud_chart.sections):
            if idx == e.section_index:
                percent = round((section.value / total) * 100, 1)
                section.title = f"{section.title.split()[0]} {percent}%"
                section.radius = hover_radius
                section.title_style = hover_title_style
            else:
                section.title = section.title.split()[0]  # reset to original label
                section.radius = normal_radius
                section.title_style = normal_title_style
        fraud_chart.update()

    fraud_chart = ft.PieChart(
        sections=[
            ft.PieChartSection(
                fraud_pie,
                title="Fraud",
                title_style=normal_title_style,
                color=ft.Colors.RED,
                radius=normal_radius,
            ),
            ft.PieChartSection(
                not_fraud_pie,
                title="Not Fraud",
                title_style=normal_title_style,
                color=ft.Colors.GREEN,
                radius=normal_radius,
            )
        ],
        sections_space=0,
        center_space_radius=40,
        on_chart_event=on_fraud_chart_event,
        expand=True,
    )
    return fraud_chart

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


def generate_fraud_report():
    df = checkingFraudTable()   
    fraud_samples, num_fraud, fraud_rate, num_no_fraud= print_fraud_results(df)
    fraud_pie = fraud_rate
    not_fraud_pie = 100-fraud_rate
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
                                "Fraud Analysis",
                                f"Number of New Transactions: {fraud_samples} \n"
                                f"Fraud Detected: {num_fraud} \n"
                                f"No Fraud Detected: {num_no_fraud} \n"
                                f"Fraud Rate: {fraud_rate:.2f}%",
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
                            content=plot_fraud_chart(fraud_pie, not_fraud_pie),
                            border_radius=15,
                            bgcolor=ft.Colors.BLACK54,
                            col={"sm": 12, "md": 6, "xl": 6},  
                            expand=True,
                            height=300,
                        ),
                    ]
                ),
                ft.Text("Executive Fraud Transactions Summary", size=24, weight="bold", color=ft.Colors.WHITE70),

                ft.Text("Compare average transaction amounts for fraud vs non-fraud.", size=20, weight="bold", color=ft.Colors.WHITE70),

                ft.ResponsiveRow(
                    controls=[
                        ft.Container(
                            content=plot_fraud_amt(df),
                            padding=10,
                            border_radius=15,
                            expand=True,
                            bgcolor=ft.Colors.BLACK54
                        ),
                    ]
                ),
                
                ft.Text("Line chart showing fraud count trends over time.", size=20, weight="bold", color=ft.Colors.WHITE70),
                # Sentiment Trends Line Chart
                ft.ResponsiveRow(
                    controls=[
                        ft.Container(
                            content=plot_fraud_trend(df),
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


def generate_customer_report():
    df = checkingChurnTable(-1)   
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



# def generate_fraud_report():
#     df = checkingFraudTable()   
#     fraud_samples, num_fraud, fraud_rate, num_no_fraud= print_fraud_results(df)
#     fraud_pie = fraud_rate
#     not_fraud_pie = 100-fraud_rate
#     report= ft.Container(
#         bgcolor=ft.Colors.BLACK87,
#         padding=10,
#         border_radius=15,
#         content=ft.Column(
#             controls=[                
#                 ft.ResponsiveRow(
#                     expand=True,
#                     controls=[
#                         ft.Container(
#                             content=create_content_block(
#                                 "Fraud Analysis",
#                                 f"Number of New Transactions: {fraud_samples} \n"
#                                 f"Fraud Detected: {num_fraud} \n"
#                                 f"No Fraud Detected: {num_no_fraud} \n"
#                                 f"Fraud Rate: {fraud_rate:.2f}%",
#                                 ft.Colors.TEAL_100,
#                                 ft.Colors.TEAL_300
#                             ),
#                             border_radius=15,
#                             shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.TEAL_300),  
#                             col={"sm": 12, "md": 6, "xl": 6},  
#                             expand=True,
#                             height=300,
#                         ),
#                         ft.Container(
#                             content=plot_fraud_chart(fraud_pie, not_fraud_pie),
#                             border_radius=15,
#                             bgcolor=ft.Colors.BLACK54,
#                             col={"sm": 12, "md": 6, "xl": 6},  
#                             expand=True,
#                             height=300,
#                         ),
#                     ]
#                 )
#             ]
#         )
#     )
#     return report

