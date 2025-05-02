import flet as ft

def main(page: ft.Page):
    teacher_img = ft.Image(
        src="teacher.png",  # No folder prefix needed
        width=400,
        height=300,
        fit=ft.ImageFit.CONTAIN
    )
    page.add(teacher_img)

# Note: Correct the folder name to 'Images' (not 'Imgaes')
ft.app(target=main)
