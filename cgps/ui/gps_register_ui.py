from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Label, Input, Button
from textual.events import Key
from textual.screen import Screen
from textual.containers import Horizontal

from cgps.core.models.tracking_device import TrackingDevice
from cgps.ui.validators.phone_validator import PhoneValidator
from cgps.ui.validators.require_validator import RequireValidator


class GpsRegisterUi(App):
    CSS = """
    Label.header { text-style: bold; }
    Horizontal { height: auto; }
    """

    def on_mount(self) -> None:
        self.push_screen(_GpsRegisterDetailScren())


class _GpsRegisterDetailScren(Screen):
    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label("Tracking device", classes="header")
        with Horizontal():
            yield Label("GSM provider: ")
            yield Input(
                id="gsm_provider",
                placeholder="Enter gsm provider name",
                type="text",
                validators=[RequireValidator()],
                compact=True,
            )
        with Horizontal():
            yield Label("GSM number: ")
            yield Input(
                id="gsm_number",
                placeholder="Enter mobile e.g. +642-155-500",
                type="text",
                validators=[PhoneValidator()],
                compact=True,
            )
        yield Label("\n")
        yield Button("Register", id="register", compact=True)

    @on(Input.Submitted)
    def _any_input_submitted(self, event: Input.Submitted) -> None:
        event.stop()
        self.app.action_focus_next()

    @on(Key)
    def _on_key(self, event: Key) -> None:
        if event.key == "escape" or event.key == "q":
            self.app.exit()

    @on(Button.Pressed, "#register")
    def _register(self):
        inputs = list(self.query(Input))
        results = [w.validate(w.value) for w in inputs]

        if not all(r.is_valid for r in results):
            bad = next(w for w, r in zip(inputs, results) if not r.is_valid)
            bad.focus()
            self.notify("Please correct the errors above", severity="error", timeout=3)
            return

        gps = TrackingDevice(
            id=0,
            gsm_provider=self.query_one("#gsm_provider", Input).value,
            gsm_no=self.query_one("#gsm_number", Input).value,
        )
        self.app.exit(gps)
