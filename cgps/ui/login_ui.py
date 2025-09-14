from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Input, Label, Button
from textual.containers import Horizontal
from textual.events import Key
from cgps.ui.validators.require_validator import RequireValidator


class LoginUi(App):
    CSS = """
    Label.header { color: white; text-style: bold; }
    Horizontal { height: auto; }
    """

    def compose(self) -> ComposeResult:
        yield Label("Car Rental Management CLI with GPS tracking", classes="header")
        yield Label("\n")
        with Horizontal():
            yield Label("Username: ")
            yield Input(
                id="username",
                placeholder="Enter username",
                type="text",
                validators=[RequireValidator()],
                compact=True,
            )
        with Horizontal():
            yield Label("Password: ")
            yield Input(
                id="password",
                placeholder="Enter password",
                type="text",
                password=True,
                validators=[RequireValidator()],
                compact=True,
            )
        yield Label("\n")
        yield Button("Login", id="login", compact=True)

    @on(Input.Submitted)
    def _any_input_submitted(self, event: Input.Submitted) -> None:
        event.stop()
        self.action_focus_next()

    @on(Button.Pressed, "#login")
    def _submitted(self, event: Input.Submitted) -> None:
        self._login()

    @on(Key)
    def _on_key(self, event: Key) -> None:
        if event.key == "escape":
            self.exit()

    def _login(self):
        username = self.query_one("#username", Input).value
        password = self.query_one("#password", Input).value
        self.exit({"username": username, "password": password})
