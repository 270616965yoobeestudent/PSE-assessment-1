import math
from typing import Any, Dict
from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Label, MaskedInput, Button, DataTable
from cgps.core.models.car import Car
from cgps.core.models.invoice import Invoice
from cgps.core.models.order import Order
from cgps.core.services.car_service import CarService
from cgps.core.utils import count_days, to_decimal
from cgps.ui.validators.iso_date_time_validator import (
    DATE_TIME_INPUT,
    ISODateTimeValidator,
)
from cgps.ui.validators.require_validator import RequireValidator
from textual.containers import Horizontal
from textual.events import Key
from textual.screen import Screen
from datetime import datetime, timedelta


class RentUi(App):
    CSS = """
    Label.header { color: white; text-style: bold; }
    Horizontal { height: auto; }
    """

    def with_data(self, user_id: int):
        self._user_id = user_id
        return self

    def __init__(self, car_service: CarService) -> None:
        super().__init__()
        self._car_service = car_service

    def on_mount(self) -> None:
        self.push_screen(
            _RentDatePickerScreen(
                user_id=self._user_id,
                car_sercice=self._car_service,
            )
        )


class _RentDatePickerScreen(Screen):
    def __init__(self, user_id: int, car_sercice: CarService) -> None:
        super().__init__()
        self._user_id = user_id
        self._car_service = car_sercice

    def compose(self) -> ComposeResult:
        yield Label(
            "Welcome to the best car rental sercice in New Zealand", classes="header"
        )
        yield Label("\n")
        with Horizontal():
            yield Label("Pick up time: ")
            yield MaskedInput(
                id="started_at",
                template="0000-00-00 00:00",
                placeholder="YYYY-MM-DD HH:MM",
                validators=[
                    RequireValidator(),
                    ISODateTimeValidator(),
                ],
                compact=True,
            )
        with Horizontal():
            yield Label("Drop off time: ")
            yield MaskedInput(
                id="ended_at",
                template="0000-00-00 00:00",
                placeholder="YYYY-MM-DD HH:MM",
                validators=[
                    RequireValidator(),
                    ISODateTimeValidator(),
                ],
                compact=True,
            )
        yield Label("\n")
        yield Button("Fine a car", id="find", compact=True)

    @on(Key)
    def _on_key(self, event: Key) -> None:
        if event.key == "escape" or event.key == "q":
            self.app.exit()

    @on(MaskedInput.Submitted)
    def _any_input_submitted(self, event: MaskedInput.Submitted) -> None:
        event.stop()
        self.app.action_focus_next()

    @on(Button.Pressed, "#find")
    def _find_car(self):
        inputs = list(self.query(MaskedInput))
        results = [w.validate(w.value) for w in inputs]

        if not all(r.is_valid for r in results):
            bad = next(w for w, r in zip(inputs, results) if not r.is_valid)
            bad.focus()
            self.notify("Please correct the errors above", severity="error", timeout=3)
            return

        now = datetime.now()
        started_at = datetime.strptime(
            self.query_one("#started_at", MaskedInput).value,
            DATE_TIME_INPUT,
        )
        ended_at = datetime.strptime(
            self.query_one("#ended_at", MaskedInput).value,
            DATE_TIME_INPUT,
        )

        if started_at < now:
            self.notify(
                f"Pick up time should be greater than now",
                severity="error",
                timeout=3,
            )
            return

        if ended_at - started_at < timedelta(days=1):
            self.notify(
                "Minimun at least 24 hours of rental",
                severity="error",
                timeout=3,
            )
            return

        cars: list[Car] = self._car_service.list_available(
            started_at=started_at,
            ended_at=ended_at,
        )
        self.app.push_screen(
            _RentAvailableCarsScreen(
                data=cars,
                started_at=started_at,
                ended_at=ended_at,
            )
        )


class _RentAvailableCarsScreen(Screen):
    def __init__(self, data: list[Car], started_at: datetime, ended_at: datetime):
        super().__init__()
        self._data = data
        self._started_at = started_at
        self._ended_at = ended_at
        self._metadata = {}

    def compose(self) -> ComposeResult:
        yield DataTable()

    @on(Key)
    def _on_key(self, event: Key) -> None:
        if event.key == "escape" or event.key == "q":
            self.app.pop_screen()

    def _on_mount(self, event):
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns(
            "Make",
            "Model",
            "Year",
            "Fuel type",
            "Seat",
            "Mileage",
            "Total Price",
            "Price per day",
            "Duration (Days)",
        )
        rows = []
        for item in self._data:
            make = item.make
            model = item.model
            year = item.year
            fuel_type = item.fuel_type
            seat = item.seat
            mileage = item.mileage
            delta = self._ended_at - self._started_at
            days = math.ceil(delta.total_seconds() / 86400)
            duration = days
            day_type = count_days(self._started_at, self._ended_at)
            weekday_price = item.weekday_rate * day_type["weekdays"]
            weekend_price = item.weekend_rate * day_type["weekends"]
            total = weekday_price + weekend_price
            total_price = f"${to_decimal(total):.2f}"
            price_per_day = f"${to_decimal(total / days):.2f}"
            rows.append(
                (
                    make,
                    model,
                    year,
                    fuel_type,
                    seat,
                    mileage,
                    total_price,
                    price_per_day,
                    duration,
                )
            )
            self._metadata[item.plate_license] = {
                "days": duration,
                "price": total,
                "weekday_price": weekday_price,
                "weekend_price": weekend_price,
                "started_at": self._started_at,
                "ended_at": self._ended_at,
                **day_type,
            }
        table.add_rows(rows)

    @on(DataTable.RowSelected)
    def handle_row_selected(self, ev: DataTable.RowSelected) -> None:
        row_index = ev.cursor_row
        car = self._data[row_index]
        self.app.push_screen(
            _RentSummaryScreen(
                car=car,
                metadata=self._metadata[car.plate_license],
            )
        )


class _RentSummaryScreen(Screen):
    def __init__(self, car: Car, metadata: Dict[str, Any]):
        super().__init__()
        self._car = car
        self._metadata = metadata

    def compose(self) -> ComposeResult:
        yield Label("Summary", classes="header")
        yield Label("\n")
        yield Label(f"Car: {self._car.make} {self._car.model}")
        yield Label(f"Pick up at: {self._metadata['started_at']}")
        yield Label(f"Drop off at: {self._metadata['ended_at']}")
        yield Label(f"Duration: {self._metadata['days']} days")
        yield Label("\n")
        yield Label(
            f"Price: ${to_decimal(self._metadata['price']):.2f}",
            classes="header",
        )
        yield Label("\n")
        yield Button("Pay", id="pay", compact=True)

    @on(Key)
    def _on_key(self, event: Key) -> None:
        if event.key == "escape" or event.key == "q":
            self.app.pop_screen()

    @on(Button.Pressed, "#pay")
    def _pay(self):
        invoice = Invoice(
            id=0,
            order_id=0,
            amount=self._metadata["price"],
            paid_amount=self._metadata["price"],
            order=Order(
                id=0,
                customer_id=0,
                car_plate_license=self._car.plate_license,
                started_at=self._metadata["started_at"],
                ended_at=self._metadata["ended_at"],
                total_day=self._metadata["days"],
                total_weekday_amount=self._metadata["weekday_price"],
                total_weekend_amount=self._metadata["weekend_price"],
                total_amount=self._metadata["price"],
            ),
        )
        self.app.exit(invoice)
