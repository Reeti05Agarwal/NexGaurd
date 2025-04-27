import flet as ft
import matplotlib.pyplot as plt 
import pyodbc
import json
import os


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
    


cloud_connection_view = ft.Column(
        controls=[
            #ft.Text("CP", size=30),
            ft.ResponsiveRow(
                controls=[
                    create_content_block(
                        "Azure", 
                        "Azure Function \nAzure Event Hub", 
                        ft.Colors.BLUE_100, ft.Colors.BLUE_200),
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