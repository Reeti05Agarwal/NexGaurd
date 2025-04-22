import flet as ft

def main(page: ft.Page):
    page.title = "Dashboard"
    page.bgcolor = ft.Colors.WHITE

    # Function to update the content dynamically based on the sidebar selection
    def update_view(selected_index: int):
        if selected_index == 0:
            # Home View
            content_area.controls = [home_view]
        elif selected_index == 1:
            # Fraud Detection View
            content_area.controls = [fraud_detection_view]
        elif selected_index == 2:
            # Customer Prediction View
            content_area.controls = [customer_prediction_view]
        elif selected_index == 3:
            # File Uploaded View
            content_area.controls = [file_uploaded_view]
        page.update()

    # Sidebar (NavigationRail)
    sidebar = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        extended=True,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label="Home"),
            ft.NavigationRailDestination(icon=ft.Icons.SEARCH, label="Fraud Detection"),
            ft.NavigationRailDestination(icon=ft.Icons.PIE_CHART, label="Customer Prediction"),
            ft.NavigationRailDestination(icon=ft.Icons.FILE_PRESENT, label="File Uploaded"),
        ],
        on_change=lambda e: update_view(e.control.selected_index)  # Trigger the view change
    )

    # Define different views (content areas)
    home_view = ft.Column(
        controls=[
            ft.Text("Welcome to the Home Page!", size=30),
            # Add more content for the home page here
        ],
        expand=True
    )

    fraud_detection_view = ft.Column(
        controls=[
            ft.Text("Fraud Detection Page", size=30),
            # Add fraud detection content here
        ],
        expand=True
    )

    customer_prediction_view = ft.Column(
        controls=[
            ft.Text("Customer Prediction Page", size=30),
            # Add customer prediction content here
        ],
        expand=True
    )

    file_uploaded_view = ft.Column(
        controls=[
            ft.Text("File Uploaded Page", size=30),
            # Add file uploaded content here
        ],
        expand=True
    )

    # Header with profile and settings buttons
    header = ft.Container(
        content=ft.Row(
            controls=[
                ft.IconButton(icon=ft.Icons.PERSON, icon_size=30),
                ft.IconButton(icon=ft.Icons.SETTINGS, icon_size=30)
            ],
            alignment=ft.MainAxisAlignment.END,
            expand=True
        ),
        bgcolor=ft.Colors.BLUE_50,
        padding=10
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
                ft.VerticalDivider(),
                ft.Column(controls=[header, content_area], expand=True)  # The content area will change dynamically
            ],
            expand=True
        )
    )

    page.update()

# Run the app
ft.app(target=main)
