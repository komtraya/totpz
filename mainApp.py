import flet as ft
import os
import sqlite3
import pyotp
import time


def generateToken(secret_key):
    totp = pyotp.TOTP(secret_key)
    token = totp.now()
    return token


class Main(ft.UserControl):
    def __init__(self):
        super().__init__()

        self.account_input = ft.TextField(
            text_align="center",
            hint_text="Name of the account",
            width=300,
        )
        self.secret_input = ft.TextField(
            text_align="center",
            hint_text="Secret Key here",
            width=300,
        )
        self.key_selector = ft.Dropdown(
            width=500,
            options=[],
            focused_border_color="green",
        )
        self.add_account_btn = ft.ElevatedButton(
            text="Store in db", height=50, on_click=self.storeAccount
        )
        self.delete_lbl = ft.Text(
            f"Are you sure you want to permanently delete account:\n{self.key_selector.value} ?",
            size=20,
        )
        self.really_delete_btn = ft.ElevatedButton(
            "Yes, Delete Account!",
            color="#141414",
            bgcolor="red",
            on_click=self.deleteAccount,
        )

        def open_banner(e):
            if self.key_selector.value:
                self.delete_account_banner.open = True
                self.delete_lbl.value = f"Are you sure you want to permanently delete account:\n{self.key_selector.value}?"
                self.really_delete_btn.visible = True
                self.cancel_delete_btn.visible = True
                e.page.overlay.append(self.delete_account_banner)
                e.page.update()

        self.delete_account_btn = ft.ElevatedButton(
            text="Delete Selected Account",
            height=50,
            on_click=open_banner,
            color="#141414",
            bgcolor="red",
        )

        def close_banner(e):
            self.delete_account_banner.open = False
            e.page.update()

        self.cancel_delete_btn = ft.ElevatedButton(
            "Cancel",
            color="#141414",
            bgcolor="green",
            on_click=close_banner,
        )
        self.delete_account_banner = ft.BottomSheet(
            ft.Container(
                ft.Column(
                    [
                        ft.Row([self.delete_lbl], alignment="center"),
                        ft.Row(
                            [self.really_delete_btn, self.cancel_delete_btn],
                            alignment="center",
                        ),
                    ],
                    tight=True,
                    alignment="center",
                    spacing=28,
                ),
                padding=20,
            ),
            open=True,
            on_dismiss=close_banner,
        )
        self.add_account_error_message = ft.Text(
            "", size=20, selectable=False, color="red", text_align="center"
        )
        self.generate_password = ft.ElevatedButton(
            text="Generate Password", height=50, on_click=self.genPass
        )
        self.your_password = ft.Text("", size=30, selectable=True)

    def storeAccount(self, e):
        if self.secret_input.value and self.account_input.value:
            profile_name = self.account_input.value.strip()
            secret_key = self.secret_input.value
            # Connect to the database
            conn = sqlite3.connect("ToTPZ.db")
            cursor = conn.cursor()

            # Check if the profile already exists
            cursor.execute(
                "SELECT COUNT(*) FROM TOTP WHERE Profile = ?", (profile_name,)
            )
            exists = cursor.fetchone()[0] > 0

            if exists:
                # Update the existing profile's secret_key
                cursor.execute(
                    "UPDATE TOTP SET Value = ? WHERE Profile = ?",
                    (secret_key, profile_name),
                )
            else:
                # Insert a new profile
                cursor.execute(
                    "INSERT INTO TOTP (Profile, Value) VALUES (?, ?)",
                    (profile_name, secret_key),
                )
            conn.commit()  # Commit the transaction
            conn.close()  # Close the database connection
            self.account_input.value = ""
            self.secret_input.value = ""
            self.add_account_error_message.color = "green"
            self.add_account_error_message.value = (
                "Account successfully stored in ToTPZ.db."
            )
            e.page.update()
            time.sleep(3)
            self.add_account_error_message.value = ""
            e.page.update()
        else:
            self.add_account_error_message.color = "red"
            self.add_account_error_message.value = "Fields cannot be empty."
            self.add_account_error_message.update()
            time.sleep(3)
            self.add_account_error_message.value = ""
            self.add_account_error_message.update()
        self.refresh_account_list()

        e.page.update()

    def refresh_account_list(self):
        # Connect to the SQLite database
        conn = sqlite3.connect("ToTPZ.db")
        # Create a cursor object
        cursor = conn.cursor()
        # Populate the account list
        cursor.execute("SELECT DISTINCT Profile FROM TOTP")
        all_profiles = cursor.fetchall()
        self.key_selector.options.clear()
        for profile in all_profiles:
            self.key_selector.options.append(ft.dropdown.Option(profile[0]))
        # Close the database connection
        conn.close()

    def genPass(self, e):
        if self.key_selector.value:
            try:
                your_password = generateToken(
                    self.return_secretKey_fromProfile(self.key_selector.value)
                )
                self.your_password.value = f"{your_password}"
                e.page.update()
            except Exception as error:
                self.your_password.value = error
                e.page.update()
        else:
            self.your_password.value = "Select an account first."
            self.your_password.update()
            time.sleep(2)
            self.your_password.value = ""
            self.your_password.update()

    def return_secretKey_fromProfile(self, profile):
        conn = sqlite3.connect("ToTPZ.db")
        cursor = conn.cursor()

        cursor.execute("SELECT Value FROM TOTP WHERE Profile=?", (profile,))

        result = (
            cursor.fetchone()
        )  # fetchone() since there's only one entry per profile

        conn.close()

        return result[0] if result else None

    def deleteAccount(self, e):
        profile_name = self.key_selector.value  # Get selected profile name
        conn = sqlite3.connect("ToTPZ.db")  # Connect to the database
        cursor = conn.cursor()
        # Delete the profile
        cursor.execute("DELETE FROM TOTP WHERE Profile = ?", (profile_name,))
        conn.commit()  # Commit the delete transaction
        conn.close()  # Close the database connection

        # Refresh the accounts list
        self.refresh_account_list()
        self.delete_lbl.value = f"{self.key_selector.value} account deleted."
        self.really_delete_btn.visible = False
        self.cancel_delete_btn.visible = False

        e.page.update()


def main(page: ft.Page):
    page.fonts = {}
    page.title = "ToTPZ - Time-Based One-Time Password Generator"
    page.theme_mode = "dark"
    page.horizontal_alignment = "center"
    stuff = Main()

    # Main Page
    def route_change(e: ft.RouteChangeEvent):
        page.views.clear()
        page.views.append(
            ft.View(
                route="/",
                controls=[
                    ft.AppBar(
                        title=ft.Text("Time-Based One-Time Password Generator"),
                        color="#e6e6e6",
                        center_title=True,
                        toolbar_height=70,
                        bgcolor="#111111",
                    ),
                    ft.Row(height=30),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                text="Add New Account",
                                height=50,
                                on_click=lambda _: page.go("/add_account"),
                            ),
                            stuff.delete_account_btn,
                        ],
                        alignment="center",
                    ),
                    ft.Text("Select Account", size=30),
                    stuff.key_selector,
                    stuff.generate_password,
                    stuff.your_password,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=38,
            )
        )
        # Add Account Page
        if page.route == "/add_account":
            page.views.clear()
            page.views.append(
                ft.View(
                    route="/add_account",
                    controls=[
                        ft.AppBar(title=ft.Text("Add Account"), bgcolor="#111111"),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    text="Home",
                                    height=50,
                                    on_click=lambda _: page.go("/"),
                                )
                            ],
                            alignment="left",
                        ),
                        ft.Row(
                            [ft.Text("New Account", size=30)],
                            width=750,
                            alignment="center",
                        ),
                        ft.Row(
                            [
                                stuff.account_input,
                                stuff.secret_input,
                                stuff.add_account_btn,
                            ],
                            alignment="center",
                            width=750,
                        ),
                        stuff.add_account_error_message,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=28,
                )
            )

    # Create ToTPZ.db if it doesn't exist, or populate the list with existing data
    def init_totpz_db():
        # Initialize Settings File(db)
        db_file = "ToTPZ.db"
        if not os.path.isfile(db_file):
            # Create and Connect to the SQLite database
            conn = sqlite3.connect("ToTPZ.db")
            # Create a cursor object
            cursor = conn.cursor()
            # Create TOTPZ table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS TOTP (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Profile TEXT NOT NULL,
                    Value TEXT
                );
                """
            )
            conn.commit()  # Commit the creation of the table
        elif os.path.isfile(db_file):
            stuff.refresh_account_list()

    init_totpz_db()
    page.on_route_change = route_change
    page.go(route=page.route)


## initialize app  ##
ft.app(target=main)
