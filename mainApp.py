import flet as ft
import pyotp


def generateToken(secret_key):
    totp = pyotp.TOTP(secret_key)
    token = totp.now()
    return token


class Error(ft.UserControl):
    def __init__(self, message):
        self.message = message
        super().__init__(self)

        self.errorMessage = ft.AlertDialog(
            content=ft.Text(f"{self.message}", text_align="center"),
            actions_alignment="center",
            open=True,
        )

    def build(self):
        return self.errorMessage


class Style(ft.UserControl):
    def __init__(self):
        super().__init__()

        self.inputStyle = ft.TextStyle(weight="bold")
        self.placeholder_Style = ft.TextStyle(weight="regular")


style = Style()


def main(page: ft.Page):
    ##### Setup #####
    page.fonts = {}
    page.title = "ToTPZ - Time-Based One-Time Password Generator"
    page.theme_mode = "dark"
    page.horizontal_alignment = "center"
    add = page.add
    text = ft.Text
    container = ft.Container
    text_input = ft.TextField
    padding = ft.padding.Padding
    p_bottom = padding(top=0, left=0, right=0, bottom=40)
    ##### Start Here #####
    app_title = container(text(value="ToTPZ", weight="w700", size=40), padding=padding(top=0, left=0, right=0, bottom=40))
    secret_input = text_input(text_align="center", text_style=style.inputStyle, hint_text="Secret Key here", hint_style=style.placeholder_Style, width=300)
    contained_input = container(secret_input, padding=p_bottom)

    def displayToken(e):
        generated_token = generateToken(secret_input.value)
        tokenText = text(value=f"Your code is: {generated_token}", weight="w700", size=20, selectable=True)
        copyToken_btn = ft.TextButton(text="Copy to Clipboard", on_click=lambda e: e.page.set_clipboard(generated_token))
        container_x = container(ft.Column([ft.Row([tokenText], alignment="center"), ft.Row([copyToken_btn], alignment="center")]))
        if len(page.controls) > 3:
            e.page.controls.pop()
            e.page.controls.append(container_x)
            e.page.update()
        else:
            e.page.controls.append(container_x)
            e.page.update()

    generateToken_btn = ft.Container(ft.TextButton(text="Generate TOTP", on_click=displayToken), padding=p_bottom)

    add(app_title, contained_input, generateToken_btn)


## initialize app  ##
ft.app(target=main, assets_dir="assets")
