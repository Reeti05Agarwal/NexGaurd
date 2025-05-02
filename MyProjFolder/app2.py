import flet as ft
import matplotlib.pyplot as plt 
from uploadingTable.churnTables.checkingChurn import checkingChurnTable 
from uploadingTable.fraudTables.checkingFraud import checkingFraudTable
from UI.Utilities import create_content_block, create_card, connection_check, generate_customer_report, generate_fraud_report
from flet.auth.providers import AzureOAuthProvider
import os
from dotenv import load_dotenv
load_dotenv()


def main(page: ft.Page):
    page.title = "Dashboard"
    page.bgcolor = ft.Colors.BLACK
    sidebar_expanded = True
    title = "Home"


# =============AZURE AUTH===================
    azure_provider = AzureOAuthProvider(
        client_id=os.getenv("AZURE_CLIENT_ID"),
        client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        redirect_url="http://localhost:8550/oauth_callback",
    )

    def on_login(e):
        if e.error:
            print("Login failed:", e.error)
        else:
            print("Login successful!")
            if page.auth and page.auth.token:
                print("Access token:", page.auth.token.access_token)
            if page.auth and page.auth.user:
                print("User ID:", page.auth.user.id)
                print("User details:", page.auth.user)
                profile_view.controls = [
                    ft.Text("👤 Profile", size=24, weight="bold"),
                    ft.Text(f"Username: {page.auth.user.name}", size=16),
                    ft.Text(f"Role: {page.auth.user.role}", size=16),
                    ft.Text(f"Email: {page.auth.user.email}", size=16),
                    logout_button
                ]
                page.update()

    def on_logout(e):
        print("User logged out")
        profile_view.controls = [login_button]
        page.update()

    def on_route_change(e):
        print("Route changed to:", page.route)
        if page.route.startswith("/oauth_callback"):
            print("Handling OAuth callback...")
            page.login(azure_provider)


    login_button = ft.ElevatedButton("Login with Azure", on_click=lambda e: page.login(azure_provider))
    logout_button = ft.ElevatedButton("Logout", on_click=lambda e: page.logout())

    page.on_login = on_login
    page.on_logout = on_logout
    page.on_route_change = on_route_change

# =============CHurn & Fraud Tables===================
    #generate_fraud_report()    #fraud_report
    #generate_customer_report() #report

# =============FUNCTIONS===================
    header_title = ft.Text(title, size=20, weight="bold", expand=True, color="grey")
    def update_view(selected_index: int):
        titles = ["Home", "Fraud Detection", "Customer Prediction", "Cloud Database", "Profile", "Settings"]
        nonlocal title
        header_title.value = titles[selected_index]

        if selected_index == 4:  # Profile view
            if selected_index == 4:  # Profile view
                if page.auth and page.auth.user:
                    content_area.controls = [profile_view]
                else:
                    content_area.controls = [ft.Column(controls=[login_button])]

        elif selected_index == 5:  # Settings view
            content_area.controls = [settings_view]
        else:
            content_area.controls = [views[selected_index]]

        page.update()

# =============SIDEBAR===================
    def get_sidebar():
        profile_section = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Row(
                        controls=[
                            ft.IconButton(ft.Icons.PERSON, icon_size=30, on_click=lambda _: update_view(4)),
                            ft.Column([
                                ft.Text("PBL-I", size=14, color=ft.Colors.WHITE),
                                ft.Text("Admin", size=10, color=ft.Colors.GREY_400),
                            ], spacing=2)
                            if sidebar_expanded else ft.Container(),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    ft.IconButton(icon=ft.Icons.SETTINGS, icon_size=30, on_click=lambda _: update_view(5))
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=10,
            bgcolor="pink"
        )


        nav_rail = ft.Container(
            content=ft.NavigationRail(
                selected_index=0,
                label_type=ft.NavigationRailLabelType.ALL,
                extended=sidebar_expanded,
                destinations=[
                    ft.NavigationRailDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label="Home"),
                    ft.NavigationRailDestination(icon=ft.Icons.SEARCH, label="Fraud Detection"),
                    ft.NavigationRailDestination(icon=ft.Icons.PIE_CHART, label="Customer Prediction"),
                    ft.NavigationRailDestination(icon=ft.Icons.FILE_PRESENT, label="Cloud Database"),
                ],
                on_change=lambda e: update_view(e.control.selected_index)
            ),
            expand=True
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    profile_section,
                    nav_rail
                ],
                expand=True,
                spacing=5
            ),
            width=250 if sidebar_expanded else 72,
            border_radius=15,
            bgcolor=ft.Colors.BLACK,
        )
    # Initially render sidebar
    sidebar = get_sidebar()

# =============VIEWS===================

    home_view = ft.Column(
        controls=[
            ft.Text("Welcome to the Dashboard", size=30, weight="bold", color=ft.Colors.WHITE),
            ft.Text("Explore the features and functionalities.", size=20, color=ft.Colors.WHITE),
            
            # Fraud and Churn - side by side
            ft.ResponsiveRow(
                controls=[
                    create_card(
                        "Real-Time Fraud Detection AI system",
                        "Develop a Real-Time Fraud Detection AI system also leveraging the Knowledge Distillation Process of a fine-tuned Transformer Model to identify suspicious transactions and anomalies such as unusual logins or high-value transactions, ensuring real-time alerts for fraud prevention.",
                        ft.Colors.BLUE_100,
                        ft.Colors.BLUE_200
                    ),
                    create_card(
                        "AI-Powered Customer Behaviour Prediction system",
                        "Develop an AI-Powered Customer Behaviour Prediction system using Transformer LLMs such as LLaMA-3 and TabNet (Self-Attention Neural Network) Model fine-tuned on our domain-specific datasets for accurate, computationally efficient predictions  with Knowledge Distillation to create a smaller, efficient and faster student model for predicting customer churn and optimizing personalized marketing strategies.",
                        ft.Colors.RED_100,
                        ft.Colors.RED_200
                    )
                ]
            ),
            ft.ResponsiveRow(
                controls=[
                    create_card(
                        "Knowledge Distillation for Efficient Models",
                        " Apply knowledge distillation to transfer knowledge from a large pre-trained teacher model to a compact student model, optimizing model performance with reduced inference time and lower computational cost.",
                        ft.Colors.BLUE_100,
                        ft.Colors.BLUE_200
                    ),
                    create_card(
                        "Zero-Trust Security Model",
                        "Integrate a zero-trust architecture to ensure strict access control, minimizing security risks and ensuring maximum data protection.",
                        ft.Colors.RED_100,
                        ft.Colors.RED_200
                    )
                ]
            ),

            # Cloud section - full width
            ft.ResponsiveRow(
                controls=[
                    create_card(
                        "Cloud Threat Analysis",
                        "Utilize Azure SQL Database, Azure Functions, Azure Event Hub and Identity and Access Management for scalable, cost-effective deployment capable of processing large data volumes in real-time. ",
                        ft.Colors.GREEN_100,
                        ft.Colors.GREEN_200
                    ),
                    create_card(
                        "Roles and Permissions",
                        "Implement Azure Active Directory for secure user authentication and authorization. Use Azure Resource Management for efficient resource allocation and management. \n1. AI Department. \n2. Cyber Security Department. \n3. Finance Analyst Department. \n4. Customer Behaviour Analyst Department.",
                        ft.Colors.GREEN_100,
                        ft.Colors.GREEN_200
                    )
                ]
            )
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

    fraud_report=generate_fraud_report()
    fraud_detection_view = ft.Column(
        controls=[
            ft.Container(
                content=fraud_report,
                border_radius=15,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK54)
            )
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

    report=generate_customer_report()
    customer_prediction_view = ft.Column(
        controls=[
            ft.Container(
                content=report,
                border_radius=15,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK54)
            )
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

    cloud_connection_view = ft.Column(
        controls=[
            ft.Text("Azure Features: ", size=30),
            ft.ResponsiveRow(
                controls=[
                    create_content_block(
                        "Azure Active Directory (Azure AD)",
                        "", 
                        ft.Colors.BLUE_100, ft.Colors.BLUE_200),
                    create_content_block(
                        "Azure Resource Management",
                        " ", 
                        ft.Colors.RED_100, ft.Colors.RED_200),
                ]
            ),
            ft.ResponsiveRow(
                controls=[
                    create_content_block(
                        "Azure SQL Database",
                        " ", 
                        ft.Colors.BLUE_100, ft.Colors.BLUE_200),
                    create_content_block(
                        "Azure Event Hub",
                        " ", 
                        ft.Colors.RED_100, ft.Colors.RED_200),
                    create_content_block(
                        "Azure Functions",
                        " ", 
                        ft.Colors.GREEN_100, ft.Colors.GREEN_200),
                ]
            ),
            ft.ResponsiveRow(
                controls=[
                    create_content_block(
                        "Azure RBAC for Resource Access",
                        " ", 
                        ft.Colors.BLUE_100, ft.Colors.BLUE_200),
                    create_content_block(
                        " Azure Key Vault",
                        " ", 
                        ft.Colors.RED_100, ft.Colors.RED_200),
                    create_content_block(
                        "Azure IAM",
                        " ", 
                        ft.Colors.GREEN_100, ft.Colors.GREEN_200),
                ]
            ),
            # ft.Text("Top 5 Customers from ChurnTable", size=24, weight='bold'),
            # ft.Container(
            #     content=ft.Row(
            #         controls=[
            #             ft.Column(
            #                 controls=[churn_table],
            #                 scroll=ft.ScrollMode.AUTO,
            #                 expand=True
            #             )
            #         ],
            #         scroll=ft.ScrollMode.AUTO,
            #     ),
            #     width=1500,
            #     height=500,
            # ),

            # ft.Text("Top 5 Customers from FraudTable", size=24, weight='bold'),
            # ft.Container(
            #     content=ft.Row(
            #         controls=[
            #             ft.Column(
            #                 controls=[fruad_table],
            #                 scroll=ft.ScrollMode.AUTO,
            #                 expand=True
            #             )
            #         ],
            #         scroll=ft.ScrollMode.AUTO,
            #     ),
            #     width=1500,
            #     height=500,
            # )
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

    profile_view = ft.Column(
        width=500,
        controls=[login_button],  # Initially show login button
        scroll=ft.ScrollMode.AUTO,
        spacing=10,
        alignment=ft.MainAxisAlignment.START
    )

    settings_view = ft.Column(
        controls=[
            ft.ResponsiveRow(
                controls=[

                ]
            )
        ]
    )

    cloud_connected = connection_check()
    cloud_status = ft.Container(
     
        content=ft.Text(
            "Cloud Connected" if cloud_connected else "Cloud Disconnected",
            color=ft.Colors.WHITE,
            size=12,
            weight="bold"
        ),
        padding=ft.padding.symmetric(horizontal=10, vertical=5),
        bgcolor=ft.Colors.GREEN_400 if cloud_connected else ft.Colors.RED_400,
        border_radius=10
    )


# =============MAIN LAYOUT===================
    views = [home_view, fraud_detection_view, customer_prediction_view, cloud_connection_view, profile_view, settings_view]

    # Header with rounded corners and profile/settings buttons
    header_title = ft.Text(title, size=20, weight="bold", expand=True, color="grey")
    header = ft.Container(
        content=ft.Row(
            controls=[
                ft.IconButton(icon=ft.Icons.MENU, icon_size=30),
                header_title,
                cloud_status
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            expand=True
        ),
        bgcolor=ft.Colors.BLUE_50,
        padding=10,
        border_radius=15  
    )

    content_area = ft.Column(
        controls=[home_view],   
        expand=True
    )


    #page.on_login = on_login
    #page.on_logout = on_logout
    page.add(
        ft.Row(
            controls=[
                sidebar,
                ft.Column(controls=[header, content_area], expand=True)  # The content area will change dynamically
            ],
            expand=True
        )
    )
    if page.route.startswith("/oauth_callback"):
        page.go(page.route)

    page.update()  

# =============Running the Functions===================
ft.app(target=main, port=8550, view=ft.WEB_BROWSER)


