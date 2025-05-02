import flet as ft
import matplotlib.pyplot as plt 
from uploadingTable.churnTables.checkingChurn import checkingChurnTable 
from uploadingTable.fraudTables.checkingFraud import checkingFraudTable
from UI.Utilities import create_content_block, create_card, connection_check, generate_customer_report, generate_fraud_report, return_flet_table
from flet.auth.providers import AzureOAuthProvider
import os
from dotenv import load_dotenv
load_dotenv()




def main(page: ft.Page):
    page.title = "Dashboard"
    page.bgcolor = ft.Colors.BLACK
    sidebar_expanded = True
    title = "Home"


    churn_table, fruad_table = return_flet_table()   
    

    header_title = ft.Text(title, size=20, weight="bold", expand=True, color="grey")
  
    def update_view(selected_index: int):
        titles = ["Home", "Fraud Detection", "Customer Prediction", "Cloud Database", "Profile", "Settings"]
        nonlocal title
        header_title.value = titles[selected_index]

        if selected_index == 4:
            content_area.controls = [profile_view]
        elif selected_index == 5:
            content_area.controls = [settings_view]
        elif selected_index == 3:  # Cloud Database
            churn_table, fruad_table = return_flet_table()  # <- Fetch only now
            updated_view = generate_cloud_database_view(churn_table, fruad_table)
            content_area.controls = [updated_view]
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

    teacher_img = ft.Image(
        src="teacher.png",  
        width=350,
        height=300,
        fit=ft.ImageFit.CONTAIN
    )

    zero_img = ft.Image(
        src="zeroTrust.png",   
        width=350,
        height=300,
        fit=ft.ImageFit.CONTAIN
    )

    objectives_img = ft.Image(
        src="objectives.png",   
        width=500,
        height=300,
        fit=ft.ImageFit.CONTAIN
    )

    roles_img = ft.Image(
        src="roles.png",   
        width=500,
        height=300,
        fit=ft.ImageFit.CONTAIN
    )

    home_view = ft.Column(
        controls=[
            ft.Text("Welcome to the Dashboard", size=30, weight="bold", color=ft.Colors.WHITE),
            ft.Text("Explore the features and functionalities.", size=20, color=ft.Colors.WHITE),
            
            ft.Row(
                controls=[
                    ft.Container(
                        content=create_card(
                            "Real-Time Fraud Detection AI system",
                            "Develop a Real-Time Fraud Detection AI system also leveraging the Knowledge Distillation Process of a fine-tuned Transformer Model to identify suspicious transactions and anomalies such as unusual logins or high-value transactions, ensuring real-time alerts for fraud prevention.",
                            ft.Colors.BLUE_100,
                            ft.Colors.BLUE_200
                        ),
                        expand=1
                    ),
                    ft.Container(
                        content=teacher_img,
                        expand=1
                    )
                ],
                spacing=50,
                alignment=ft.MainAxisAlignment.START
            ),

            ft.Row(
                controls=[
                    ft.Container(
                        content=teacher_img,
                        expand=1
                    ),
                    ft.Container(
                        content=create_card(
                            "AI-Powered Customer Behaviour Prediction system",
                            "Develop an AI-Powered Customer Behaviour Prediction system using Transformer LLMs such as LLaMA-3 and TabNet (Self-Attention Neural Network) Model fine-tuned on our domain-specific datasets for accurate, computationally efficient predictions  with Knowledge Distillation to create a smaller, efficient and faster student model for predicting customer churn and optimizing personalized marketing strategies.",
                            ft.Colors.RED_100,
                            ft.Colors.RED_200
                        ),
                        expand=1
                    ),
                    
                ],
                spacing=50,
                alignment=ft.MainAxisAlignment.START
            ),

            
            ft.Row(
                controls=[
                    ft.Container(
                        content=create_card(
                            "Knowledge Distillation for Efficient Models",
                            "Apply knowledge distillation to transfer knowledge from a large pre-trained teacher model to a compact student model, optimizing model performance with reduced inference time and lower computational cost.",
                            ft.Colors.BLUE_100,
                            ft.Colors.BLUE_200
                        ),
                        expand=1
                    ),
                    ft.Container(
                        content=teacher_img,
                        expand=1
                    )
                ],
                spacing=50,
                alignment=ft.MainAxisAlignment.START
            ),

            ft.Row(
                controls=[
                    ft.Container(
                        content=zero_img,
                        expand=1
                    ),
                    ft.Container(
                        content=create_card(
                            "Zero-Trust Security Model",
                            "Integrate a zero-trust architecture to ensure strict access control, minimizing security risks and ensuring maximum data protection.",
                            ft.Colors.RED_100,
                            ft.Colors.RED_200
                        ),
                        expand=1
                    ),
                ],
                spacing=50,
                alignment=ft.MainAxisAlignment.START
            ),

            ft.Row(
                controls=[
                    
                    ft.Container(
                        content=create_card(
                            "Cloud Threat Analysis",
                            "Utilize Azure SQL Database, Azure Functions, Azure Event Hub and Identity and Access Management for scalable, cost-effective deployment capable of processing large data volumes in real-time. ",
                            ft.Colors.GREEN_100,
                            ft.Colors.GREEN_200
                        ),
                        expand=1
                    ),
                    ft.Container(
                        content=zero_img,
                        expand=1
                    ),
                ],
                spacing=50,
                alignment=ft.MainAxisAlignment.START
            ),

            ft.Row(
                controls=[
                    ft.Container(
                        content=roles_img,
                        expand=1
                    ),
                    ft.Container(
                        content=create_card(
                            "Roles and Permissions",
                            "Implement Azure Active Directory for secure user authentication and authorization. Use Azure Resource Management for efficient resource allocation and management. \n1. AI Department. \n2. Cyber Security Department. \n3. Finance Analyst Department. \n4. Customer Behaviour Analyst Department.",
                            ft.Colors.GREEN_100,
                            ft.Colors.GREEN_200
                        ),
                        expand=1
                    ),
                ],
                spacing=50,
                alignment=ft.MainAxisAlignment.START
            ),

            objectives_img
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

    churn_report=generate_customer_report()
    customer_prediction_view = ft.Column(
        controls=[
            ft.Container(
                content=churn_report,
                border_radius=15,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK54)
            )
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

    def generate_cloud_database_view(churn_table, fruad_table):
        return ft.Column(
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
                ft.Text("Top 5 Customers from ChurnTable", size=24, weight='bold'),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=[churn_table],
                                scroll=ft.ScrollMode.AUTO,
                                expand=True
                            )
                        ],
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    width=1500,
                    height=500,
                ),

                ft.Text("Top 5 Customers from FraudTable", size=24, weight='bold'),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=[fruad_table],
                                scroll=ft.ScrollMode.AUTO,
                                expand=True
                            )
                        ],
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    width=1500,
                    height=500,
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

    cloud_connection_view = ft.Column(
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

    # profile_view = ft.Column(
    #     width=500,
    #     controls=[login_button],  # Initially show login button
    #     scroll=ft.ScrollMode.AUTO,
    #     spacing=10,
    #     alignment=ft.MainAxisAlignment.START
    # )

    profile_view = ft.Column(
        width=500,
        controls=[
            ft.Text("👤 Profile", size=24, weight="bold"),
            ft.Container(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.CircleAvatar(
                            #foreground_image_url="",
                            radius=50
                        ),
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            tooltip="Change profile picture",
                            icon_color="blue",
                            on_click=lambda _: print("Change profile pic clicked"),
                        )
                    ]
                ),
                padding=10
            ),
            ft.TextField(
                label="Username",
                value="reeti.sharma",
                prefix_icon=ft.Icons.PERSON,
                read_only=False,
                border_radius=10
            ),
            ft.TextField(
                label="Role",
                value="AI Cyber Lab Analyst",
                prefix_icon=ft.Icons.BADGE,
                read_only=True,
                border_radius=10
            ),
            ft.TextField(
                label="Email",
                value="reeti.sharma@company.com",
                prefix_icon=ft.Icons.EMAIL,
                read_only=True,
                border_radius=10
            ),
            ft.Divider(),

            ft.Text("🔒 Change Password", size=18, weight="bold"),
            ft.TextField(
                label="Current Password",
                password=True,
                can_reveal_password=True,
                border_radius=10
            ),
            ft.TextField(
                label="New Password",
                password=True,
                can_reveal_password=True,
                border_radius=10
            ),
            ft.TextField(
                label="Confirm New Password",
                password=True,
                can_reveal_password=True,
                border_radius=10
            ),
            ft.Container(
                content=ft.ElevatedButton(
                    text="Save Changes",
                    icon=ft.Icons.SAVE,
                    on_click=lambda _: print("Save clicked"),
                    bgcolor="blue",
                    color="white",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
                ),
                padding=10
            )
        ],
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
    # if page.route.startswith("/oauth_callback"):
    #     page.go(page.route)

    page.update()  

ft.app(target=main)


