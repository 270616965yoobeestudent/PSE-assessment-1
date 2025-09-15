import math
from typing import Any
from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Pretty, DataTable
from textual.events import Key
from textual.screen import Screen
from datetime import datetime

from cgps.core.utils import ISO_DT, to_decimal


class OrderListUi(App):
    def with_data(self, data: list[dict[str, Any]]):
        self._data = data
        return self

    def on_mount(self) -> None:
        self.push_screen(_OrderListTableScren(self._data))


class _OrderListTableScren(Screen):
    def __init__(self, data: list[dict[str, Any]]):
        super().__init__()
        self._data = data

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
            "Status",
            "Issue date",
        )
        rows = []
        for item in self._data:
            no = item["order"]["id"]
            pick_up = item["order"]["started_at"]
            drop_off = item["order"]["ended_at"]
            t1 = datetime.strptime(pick_up, ISO_DT)
            t2 = datetime.strptime(drop_off, ISO_DT)
            delta = t2 - t1
            days = math.ceil(delta.total_seconds() / 86400)
            duration = days
            car = f"{item['order']['car']['make']} {item['order']['car']['model']}"
            total_price = f"${to_decimal(item['order']['total_amount']):.2f}"
            status = "Paid" if item["paid_at"] else "Unpaid"
            issue_date = item["created_at"]
            rows.append(
                (
                    no,
                    pick_up,
                    drop_off,
                    duration,
                    car,
                    total_price,
                    status,
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
        self.app.push_screen(_OrderListDetailScren(self._data[row_index]))


class _OrderListDetailScren(Screen):
    def __init__(self, data: dict[str, Any]):
        super().__init__()
        self._data = data

    def compose(self) -> ComposeResult:
        yield Pretty(self._data)

    @on(Key)
    def _on_key(self, event: Key) -> None:
        if event.key == "escape" or event.key == "q":
            self.app.pop_screen()
