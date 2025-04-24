import flet as ft
import matplotlib.pyplot as plt



def main(page: ft.Page):
    page.title = "Dashboard"
    page.bgcolor = ft.Colors.BLACK

    sidebar_expanded = True
    title = ""

    

     

    # Function to update the content dynamically based on the sidebar selection
    def update_view(selected_index: int):
        titles = ["Home", "Fraud Detection", "Customer Prediction", "Cloud Database", "Profile", "Settings"]
        nonlocal title
        header_title.value = titles[selected_index]
        content_area.controls = [views[selected_index]]
        page.update()
        if not sidebar_expanded and page.window_width < 600:
            toggle_sidebar(None)

    def toggle_sidebar(e):
        nonlocal sidebar_expanded
        sidebar_expanded = not sidebar_expanded
        sidebar.extended = sidebar_expanded
        page.update()

    # Sidebar (NavigationRail) with rounded corners
    def get_sidebar():
        profile_section = ft.Container(
        content=ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.IconButton(ft.Icons.PERSON, icon_size=30),
                        ft.Column([
                            ft.Text("John Doe", size=14, color=ft.Colors.WHITE),
                            ft.Text("AI Analyst", size=10, color=ft.Colors.GREY_400),
                        ], spacing=2)
                        if sidebar_expanded else ft.Container(),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.IconButton(icon=ft.Icons.SETTINGS, icon_size=30)
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

    # Helper function to create content blocks for views
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

    # Define different views (content areas)
    home_view = ft.Column(
        controls=[
            #ft.Text("CP", size=30),
            ft.ResponsiveRow(
                controls=[
                    create_content_block("Fraud Detection in Transactions", "Features evaluted to predict anomaly", ft.Colors.BLUE_100, ft.Colors.BLUE_200),
                    create_content_block("Customer Behaviour Prediction", "Features evaluted to predict their behaviour", ft.Colors.RED_100, ft.Colors.RED_200)
                ]
            ),
            ft.ResponsiveRow(
                controls=[
                    create_content_block("Features: ", "Features evaluted to predict their behaviour", ft.Colors.BLUE_100, ft.Colors.BLUE_200),
                    create_content_block("Features: ", "", ft.Colors.RED_100, ft.Colors.RED_200)
                ]
            )
        ],
        expand=True
    )

    fraud_detection_view = ft.Column(
        controls=[
            #ft.Text("FD", size=30),
            ft.ResponsiveRow(
                controls=[
                    create_content_block("Live Monitoring", "Real-time analysis of transactions.", ft.Colors.BLUE_100, ft.Colors.BLUE_200),
                    create_content_block("Anomaly Detection", "Detect unusual behavior automatically.", ft.Colors.RED_100, ft.Colors.RED_200),
                    create_content_block("Reports", "View fraud detection statistics.", ft.Colors.GREEN_100, ft.Colors.GREEN_200),
                ]
            )
        ],
        expand=True
    )

    customer_prediction_view = ft.Column(
        controls=[
            #ft.Text("CP", size=30),
            ft.ResponsiveRow(
                controls=[
                    create_content_block("Number of Customer", "Real-time analysis of transactions.", ft.Colors.BLUE_100, ft.Colors.BLUE_200),
                    create_content_block("Prediction Modeln", "Detect unusual behavior automatically.", ft.Colors.RED_100, ft.Colors.RED_200),
                    create_content_block("Reports", "View fraud detection statistics.", ft.Colors.GREEN_100, ft.Colors.GREEN_200),
                ]
            )
        ],
        expand=True
    )

    file_uploaded_view = ft.Column(
        controls=[
            #ft.Text("CP", size=30),
            ft.ResponsiveRow(
                controls=[
                    create_content_block("Search Bar", "Real-time analysis of transactions.", ft.Colors.BLUE_100, ft.Colors.BLUE_200),
                ]
            ),
            ft.ResponsiveRow(
                controls=[
                    create_content_block("Search Bar", "Real-time analysis of transactions.", ft.Colors.BLUE_100, ft.Colors.BLUE_200),
                ]
            )
        ],
        expand=True
    )

    profile_view = ft.Column(
        controls=[
            ft.ResponsiveRow(
                controls=[

                ]
            )
        ]
    )

    settings_view = ft.Column(
        controls=[
            ft.ResponsiveRow(
                controls=[

                ]
            )
        ]
    )

    cloud_connected = False

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

    views = [home_view, fraud_detection_view, customer_prediction_view, file_uploaded_view, profile_view, settings_view]

    # Header with rounded corners and profile/settings buttons
    header_title = ft.Text(title, size=20, weight="bold", expand=True, color="grey")
    header = ft.Container(
        content=ft.Row(
            controls=[
                ft.IconButton(icon=ft.Icons.MENU, icon_size=30, on_click=toggle_sidebar),
                header_title,
                cloud_status
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            expand=True
        ),
        bgcolor=ft.Colors.BLUE_50,
        padding=10,
        border_radius=15  # Rounded corners for header
    )

    # Main content area to hold dynamic content
    content_area = ft.Column(
        controls=[home_view],  # Start with the home view
        expand=True
    )

    # Main layout with sidebar and content area
    page.add(
        ft.Row(
            controls=[
                sidebar,
                ft.Column(controls=[header, content_area], expand=True)  # The content area will change dynamically
            ],
            expand=True
        )
    )

    page.update()

# Run the app
ft.app(target=main)
