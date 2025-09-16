from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Label, DataTable, Input, Button
from textual.events import Key
from textual.screen import Screen
from textual.containers import Horizontal

from cgps.core.models.tracking_device import TrackingDevice
from cgps.ui.validators.phone_validator import PhoneValidator
from cgps.ui.validators.require_validator import RequireValidator


class GpsListUi(App):
    CSS = """
    Label.header { text-style: bold; }
    Horizontal { height: auto; }
    """

    def with_data(self, data: TrackingDevice):
        self._data = data
        return self

    def on_mount(self) -> None:
        self.push_screen(_GpsListTableScren(self._data))


class _GpsListTableScren(Screen):
    def __init__(self, data: TrackingDevice):
        super().__init__()
        self._data = data

    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns(
            "No",
            "GSM Provider",
            "GSM number",
        )
        rows = []
        for item in self._data:
            id = item.id
            gsm_provider = item.gsm_provider
            gsm_no = item.gsm_no
            rows.append(
                (
                    id,
                    gsm_provider,
                    gsm_no,
                )
            )
        table.add_rows(rows)

    @on(Key)
    def _on_key(self, event: Key) -> None:
        if event.key == "escape" or event.key == "q":
            self.app.exit()

    @on(DataTable.RowSelected)
    def handle_row_selected(self, ev: DataTable.RowSelected) -> None:
        row_index = ev.cursor_row
        self.app.push_screen(_GpsListDetailScren(data=self._data[row_index]))


class _GpsListDetailScren(Screen):
    def __init__(self, data: TrackingDevice):
        super().__init__()
        self._data = data

    def compose(self) -> ComposeResult:
        yield Label("Tracking device", classes="header")
        with Horizontal():
            yield Label("GSM provider: ")
            yield Input(
                id="gsm_provider",
                placeholder="Enter gsm provider name",
                type="text",
                value=self._data.gsm_provider,
                validators=[RequireValidator()],
                compact=True
            )
        with Horizontal():
            yield Label("GSM number: ")
            yield Input(
                id="gsm_number",
                placeholder="Enter mobile e.g. +642-155-500",
                type="text",
                value=self._data.gsm_no,
                validators=[PhoneValidator()],
                compact=True
            )
        yield Label("\n")
        yield Button("Update", id="update", compact=True)

    @on(Input.Submitted)
    def _any_input_submitted(self, event: Input.Submitted) -> None:
        event.stop()
        self.app.action_focus_next()

    @on(Key)
    def _on_key(self, event: Key) -> None:
        if event.key == "escape" or event.key == "q":
            self.app.pop_screen()

    @on(Button.Pressed, "#update")
    def _update(self):
        inputs = list(self.query(Input))
        results = [w.validate(w.value) for w in inputs]

        if not all(r.is_valid for r in results):
            bad = next(w for w, r in zip(inputs, results) if not r.is_valid)
            bad.focus()
            self.notify("Please correct the errors above", severity="error", timeout=3)
            return
        
        self._data.gsm_no = self.query_one("#gsm_number", Input).value
        self._data.gsm_provider = self.query_one("#gsm_provider", Input).value
        self.app.exit(self._data)
