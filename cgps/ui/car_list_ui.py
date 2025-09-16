from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Label, DataTable, Input, Button, Select, MaskedInput
from textual.events import Key
from textual.screen import Screen
from textual.containers import Horizontal

from cgps.core.models.car import Car
from cgps.core.services.gps_service import GpsService
from cgps.core.utils import to_decimal
from cgps.ui.validators.iso_date_validator import ISODateValidator
from cgps.ui.validators.number_validator import NumberValidator
from cgps.ui.validators.require_validator import RequireValidator


class CarListUi(App):
    CSS = """
    Label.header { text-style: bold; }
    Horizontal { height: auto; }
    """

    def __init__(self, gps_service: GpsService):
        super().__init__()
        self._gps_service = gps_service

    def with_data(self, data: list[Car], flow: str):
        self._data = data
        self._flow = flow
        return self

    def on_mount(self) -> None:
        if self._flow == "register":
            self.push_screen(
                _CarListDetailScren(
                    Car(id=0),
                    self._gps_service,
                    self._flow,
                )
            )
        else:
            self.push_screen(
                _CarListTableScren(
                    self._data,
                    self._gps_service,
                    self._flow,
                )
            )


class _CarListTableScren(Screen):
    def __init__(self, data: list[Car], gps_service: GpsService, flow: str):
        super().__init__()
        self._data = data
        self._gps_service = gps_service
        self._flow = flow

    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns(
            "Plate license",
            "Make",
            "Model",
            "Year",
            "Fuel type",
            "Seat",
            "Mileage",
            "Weekday rate",
            "Weekend rate",
            "Gps ID",
            "Status",
            "created_at",
        )
        rows = []
        for item in self._data:
            plate_license = item.plate_license
            make = item.make
            model = item.model
            year = item.year
            fuel_type = item.fuel_type
            seat = item.seat
            mileage = item.mileage
            weekday_rate = item.weekday_rate
            weekend_rate = item.weekend_rate
            gps_id = item.tracking_device_id if item.tracking_device_id else "None"
            created_at = item.created_at
            status = "Available" if item.available else "Unavailable"
            rows.append(
                (
                    plate_license,
                    make,
                    model,
                    year,
                    fuel_type,
                    seat,
                    mileage,
                    weekday_rate,
                    weekend_rate,
                    gps_id,
                    status,
                    created_at,
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
        self.app.push_screen(
            _CarListDetailScren(
                data=self._data[row_index],
                gps_service=self._gps_service,
                flow=self._flow,
            )
        )


class _CarListDetailScren(Screen):
    def __init__(self, data: Car, gps_service: GpsService, flow: str):
        super().__init__()
        self._data = data
        self._flow = flow
        if flow == "register":
            self._gps = gps_service.get_available(car_id=None)
        else:
            self._gps = gps_service.get_available(car_id=data.id)

    def compose(self) -> ComposeResult:
        yield Label(
            "Register new car" if self._flow == "register" else "Update car",
            classes="header",
        )
        with Horizontal():
            yield Label("Plate license: ")
            yield Input(
                id="plate_license",
                placeholder="Enter plate license",
                type="text",
                value=self._data.plate_license,
                validators=[RequireValidator()],
                compact=True,
            )
        with Horizontal():
            yield Label("Engine number: ")
            yield Input(
                id="engine_number",
                placeholder="Enter engine number",
                type="text",
                value=self._data.engine_number,
                validators=[RequireValidator()],
                compact=True,
            )
        with Horizontal():
            yield Label("Fuel type: ")
            yield Select(
                [("Petrol", "petrol"), ("Diesel", "diesel"), ("EV", "ev")],
                value=self._data.fuel_type if self._data.fuel_type else "petrol",
                id="fuel_type",
                allow_blank=False,
                compact=True,
            )
        with Horizontal():
            yield Label("Make: ")
            yield Input(
                id="make",
                placeholder="Enter make",
                type="text",
                value=self._data.make,
                validators=[RequireValidator()],
                compact=True,
            )
        with Horizontal():
            yield Label("Model: ")
            yield Input(
                id="model",
                placeholder="Enter model",
                type="text",
                value=self._data.model,
                validators=[RequireValidator()],
                compact=True,
            )
        with Horizontal():
            yield Label("Year: ")
            yield Input(
                id="year",
                placeholder="Enter year",
                type="number",
                value=str(self._data.year if self._data.year != None else ""),
                validators=[RequireValidator(), NumberValidator()],
                compact=True,
            )
        with Horizontal():
            yield Label("Color: ")
            yield Input(
                id="color",
                placeholder="Enter color",
                type="text",
                value=self._data.color,
                validators=[RequireValidator()],
                compact=True,
            )
        with Horizontal():
            yield Label("Type: ")
            yield Input(
                id="type",
                placeholder="Enter type",
                type="text",
                value=self._data.type,
                validators=[RequireValidator()],
                compact=True,
            )
        with Horizontal():
            yield Label("Seat: ")
            yield Input(
                id="seat",
                placeholder="Enter seat",
                type="number",
                value=str(self._data.seat if self._data.seat != None else ""),
                validators=[RequireValidator(), NumberValidator()],
                compact=True,
            )
        with Horizontal():
            yield Label("Mileage: ")
            yield Input(
                id="mileage",
                placeholder="Enter mileage",
                type="number",
                value=str(self._data.mileage if self._data.mileage != None else ""),
                validators=[RequireValidator(), NumberValidator()],
                compact=True,
            )
        with Horizontal():
            yield Label("Minimum rent: ")
            yield Input(
                id="minimum_rent",
                placeholder="Enter minimum rent",
                type="number",
                value=str(self._data.minimum_rent if self._data.minimum_rent != None else ""),
                validators=[RequireValidator(), NumberValidator()],
                compact=True,
            )
        with Horizontal():
            yield Label("Maximum rent: ")
            yield Input(
                id="maximum_rent",
                placeholder="Enter maximum rent",
                type="number",
                value=str(self._data.maximum_rent if self._data.maximum_rent != None else ""),
                validators=[RequireValidator(), NumberValidator()],
                compact=True,
            )
        with Horizontal():
            yield Label("Factory date: ")
            yield MaskedInput(
                id="factory_date",
                template="0000-00-00",
                placeholder="YYYY-MM-DD",
                value=(
                    self._data.factory_date.isoformat()
                    if self._data.factory_date
                    else ""
                ),
                validators=[ISODateValidator()],
                compact=True,
            )
        with Horizontal():
            yield Label("Weekday rate: ")
            yield Input(
                id="weekday_rate",
                placeholder="Enter weekday rate",
                type="number",
                value=str(self._data.weekday_rate if self._data.weekday_rate != None else ""),
                validators=[RequireValidator()],
                compact=True,
            )
        with Horizontal():
            yield Label("Weekend rate: ")
            yield Input(
                id="weekend_rate",
                placeholder="Enter weekend rate",
                type="number",
                value=str(self._data.weekend_rate if self._data.weekend_rate != None else ""),
                validators=[RequireValidator()],
                compact=True,
            )
        with Horizontal():
            yield Label("Available: ")
            yield Select(
                [("Available", True), ("Unavailable", False)],
                value=self._data.available if self._data.available else True,
                id="available",
                allow_blank=False,
                compact=True,
            )
        with Horizontal():
            yield Label("GPS ID: ")
            yield Select(
                [("None", None), *[(str(gps.id), gps.id) for gps in self._gps]],
                value=self._data.tracking_device_id,
                id="tracking_device_id",
                allow_blank=False,
                compact=True,
            )
        yield Label("\n")
        with Horizontal():
            yield Button(
                "Register" if self._flow == "register" else "Update", id="update", compact=True
            )
            yield Label(" ")
            if self._data.tracking_device_id:
                yield Button("Report", id="report", compact=True)

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

        self._data.plate_license = self.query_one("#plate_license", Input).value
        self._data.engine_number = self.query_one("#engine_number", Input).value
        self._data.fuel_type = self.query_one("#fuel_type", Select).value
        self._data.make = self.query_one("#make", Input).value
        self._data.model = self.query_one("#model", Input).value
        self._data.year = int(self.query_one("#year", Input).value)
        self._data.color = self.query_one("#color", Input).value
        self._data.type = self.query_one("#type", Input).value
        self._data.seat = int(self.query_one("#seat", Input).value)
        self._data.mileage = int(self.query_one("#mileage", Input).value)
        self._data.minimum_rent = int(self.query_one("#minimum_rent", Input).value)
        self._data.maximum_rent = int(self.query_one("#maximum_rent", Input).value)
        self._data.factory_date = self.query_one("#factory_date", MaskedInput).value
        self._data.weekday_rate = to_decimal(
            self.query_one("#weekday_rate", Input).value
        )
        self._data.weekend_rate = to_decimal(
            self.query_one("#weekend_rate", Input).value
        )
        self._data.available = self.query_one("#available", Select).value
        self._data.tracking_device_id = self.query_one(
            "#tracking_device_id", Select
        ).value
        self.app.exit(("update", self._data))

    @on(Button.Pressed, "#report")
    def _report(self):
        self.app.exit(("report", self._data))
