import flet as ft

def profile_view():
    return ft.Column(
        width=500,
        controls=[
            ft.Text("👤 Profile", size=24, weight="bold"),
            ft.Container(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.CircleAvatar(
                            foreground_image_url="https://i.pravatar.cc/150?img=3",
                            radius=50
                        ),
                        ft.IconButton(
                            icon=ft.icons.EDIT,
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
                prefix_icon=ft.icons.PERSON,
                read_only=False,
                border_radius=10
            ),
            ft.TextField(
                label="Role",
                value="AI Cyber Lab Analyst",
                prefix_icon=ft.icons.BADGE,
                read_only=True,
                border_radius=10
            ),
            ft.TextField(
                label="Email",
                value="reeti.sharma@company.com",
                prefix_icon=ft.icons.EMAIL,
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
                    icon=ft.icons.SAVE,
                    on_click=lambda _: print("Save clicked"),
                    bgcolor="blue",
                    color="white",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
                ),
                padding=10
            )
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.START
    )
