import math
from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Label, DataTable, MaskedInput, Input, Button
from textual.events import Key
from textual.screen import Screen
from textual.containers import Horizontal

from cgps.core.models.invoice import Invoice
from cgps.core.utils import to_decimal
from cgps.ui.validators.iso_date_time_validator import (
    DATE_TIME_INPUT,
)


class OrderListUi(App):
    CSS = """
    Label.header { text-style: bold; }
    Horizontal { height: auto; }
    """

    def with_data(self, data: Invoice, flow: str):
        self._data = data
        self._flow = flow
        return self

    def on_mount(self) -> None:
        self.push_screen(
            _OrderListTableScren(
                self._data,
                flow=self._flow,
            )
        )


class _OrderListTableScren(Screen):
    def __init__(self, data: Invoice, flow: str):
        super().__init__()
        self._data = data
        self._flow = flow

    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns(
            "No",
            "Pick up",
            "Drop off",
            "Duration (day)",
            "Car",
            "Total Price",
            "Payment",
            "Status",
            "Actual pick up",
            "Actual drop off",
            "Issue date",
        )
        rows = []
        for item in self._data:
            no = item.order.id
            pick_up = item.order.started_at
            drop_off = item.order.ended_at
            delta = drop_off - pick_up
            days = math.ceil(delta.total_seconds() / 86400)
            duration = days
            car = f"{item.order.car.make} {item.order.car.model}"
            total_price = f"${to_decimal(item.order.total_amount):.2f}"
            payment = "Paid" if item.paid_at else "Unpaid"
            status = (
                "Processing"
                if item.order.approved_at is None and item.order.rejected_at is None
                else "Approved" if item.order.approved_at else "Rejected"
            )
            actual_pick_up = item.order.receive_at
            actual_drop_off = item.order.return_at
            issue_date = item.created_at
            rows.append(
                (
                    no,
                    pick_up,
                    drop_off,
                    duration,
                    car,
                    total_price,
                    payment,
                    status,
                    actual_pick_up,
                    actual_drop_off,
                    issue_date,
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
            _OrderListDetailScren(
                data=self._data[row_index],
                flow=self._flow,
            )
        )


class _OrderListDetailScren(Screen):
    def __init__(self, data: Invoice, flow: str):
        super().__init__()
        self._data = data
        self._flow = flow

    def compose(self) -> ComposeResult:
        yield Label("Order", classes="header")
        with Horizontal():
            yield Label("Pick up time: ")
            yield MaskedInput(
                id="started_at",
                template="0000-00-00 00:00",
                placeholder="YYYY-MM-DD HH:MM",
                value=self._data.order.started_at.strftime(DATE_TIME_INPUT),
                compact=True,
            )
        with Horizontal():
            yield Label("Drop off time: ")
            yield MaskedInput(
                id="ended_at",
                template="0000-00-00 00:00",
                placeholder="YYYY-MM-DD HH:MM",
                value=self._data.order.ended_at.strftime(DATE_TIME_INPUT),
                compact=True,
            )
        with Horizontal():
            yield Label("Duration (day): ")
            yield Input(
                id="total_day",
                value=str(self._data.order.total_day),
                type="number",
                compact=True,
            )
        with Horizontal():
            yield Label("Price ($): ")
            yield Input(
                id="total_amount",
                value=str(self._data.order.total_amount),
                type="number",
                compact=True,
            )
        with Horizontal():
            yield Label("Actual pick up: ")
            yield Input(
                id="created_at",
                value=(
                    "-"
                    if self._data.order.receive_at == None
                    else self._data.order.receive_at.strftime(DATE_TIME_INPUT)
                ),
                compact=True,
            )
        with Horizontal():
            yield Label("Actual drop off: ")
            yield Input(
                id="created_at",
                value=(
                    "-"
                    if self._data.order.return_at == None
                    else self._data.order.return_at.strftime(DATE_TIME_INPUT)
                ),
                compact=True,
            )
        with Horizontal():
            yield Label("Issue at: ")
            yield MaskedInput(
                id="created_at",
                template="0000-00-00 00:00",
                placeholder="YYYY-MM-DD HH:MM",
                value=self._data.created_at.strftime(DATE_TIME_INPUT),
                compact=True,
            )
        yield Label("\n")
        yield Label("Car", classes="header")
        with Horizontal():
            yield Label("Plate license: ")
            yield Input(
                id="plate_license",
                value=self._data.order.car.plate_license,
                type="text",
                compact=True,
            )
        with Horizontal():
            yield Label("Fuel type: ")
            yield Input(
                id="fuel_type",
                value=self._data.order.car.fuel_type,
                type="text",
                compact=True,
            )
        with Horizontal():
            yield Label("Make: ")
            yield Input(
                id="make", value=self._data.order.car.make, type="text", compact=True
            )
        with Horizontal():
            yield Label("Model: ")
            yield Input(
                id="model", value=self._data.order.car.model, type="text", compact=True
            )
        with Horizontal():
            yield Label("Year: ")
            yield Input(
                id="year",
                value=str(self._data.order.car.year),
                type="number",
                compact=True,
            )
        with Horizontal():
            yield Label("Seat: ")
            yield Input(
                id="seat",
                value=str(self._data.order.car.seat),
                type="number",
                compact=True,
            )
        with Horizontal():
            yield Label("Mileage: ")
            yield Input(
                id="mileage",
                value=str(self._data.order.car.mileage),
                type="number",
                compact=True,
            )
        yield Label("\n")
        if self._flow == "manage" and self._data.order.return_at is None:
            with Horizontal():
                if self._data.order.approved_at is None:
                    yield Button(
                        "Approve", id="approve", compact=True, variant="success"
                    )
                    yield Label(" ")
                if self._data.paid_at is None and self._data.order.rejected_at is None:
                    yield Button(
                        "Mark Paid", id="paid", compact=True, variant="warning"
                    )
                    yield Label(" ")
                if (
                    self._data.order.receive_at is None
                    and self._data.order.rejected_at is None
                    and self._data.paid_at is not None
                    and self._data.order.approved_at is not None
                ):
                    yield Button("Pick up", id="pick-up", compact=True)
                    yield Label(" ")
                if (
                    self._data.order.return_at is None
                    and self._data.order.receive_at is not None
                ):
                    yield Button("Drop off", id="drop-off", compact=True)
                    yield Label(" ")
                if self._data.order.rejected_at is None:
                    yield Button("Reject", id="reject", compact=True, variant="error")
                    yield Label(" ")
        if self._flow == "manage" and self._data.order.return_at is not None:
            yield Label("This order has been completed", classes="header")

    @on(Key)
    def _on_key(self, event: Key) -> None:
        if event.key == "escape" or event.key == "q":
            self.app.pop_screen()

    @on(Button.Pressed, "#reject")
    def _delete(self):
        self.app.exit(("reject", self._data))

    @on(Button.Pressed, "#approve")
    def _approve(self):
        self.app.exit(("approve", self._data))

    @on(Button.Pressed, "#paid")
    def _paid(self):
        self.app.exit(("paid", self._data))

    @on(Button.Pressed, "#pick-up")
    def _pick_up(self):
        self.app.exit(("pick-up", self._data))

    @on(Button.Pressed, "#drop-off")
    def _drop_off(self):
        self.app.exit(("drop-off", self._data))
