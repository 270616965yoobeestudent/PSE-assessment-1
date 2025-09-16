from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Label, DataTable, Input, Button
from textual.events import Key
from textual.screen import Screen
from textual.containers import Horizontal

from cgps.core.models.customer import Customer
from cgps.core.services.customer_service import CustomerService
from cgps.core.utils import calculate_age
from cgps.ui.validators.require_validator import RequireValidator


class CustomerSearchUi(App):
    CSS = """
    Label.header { text-style: bold; }
    Horizontal { height: auto; }
    """

    def __init__(self, customer_service: CustomerService):
        super().__init__()
        self._customer_service = customer_service

    def on_mount(self) -> None:
        self.push_screen(_CustomerSearchScren(self._customer_service))


class _CustomerSearchScren(Screen):
    def __init__(self, customer_service: CustomerService):
        super().__init__()
        self._customer_service = customer_service

    def compose(self) -> ComposeResult:
        yield Label("Search customer", classes="header")
        with Horizontal():
            yield Label("Passport no: ")
            yield Input(
                id="passport_no",
                placeholder="Search by passport no",
                type="text",
                compact=True,
            )
        with Horizontal():
            yield Label("First name: ")
            yield Input(
                id="first_name",
                placeholder="Search by first name",
                type="text",
                compact=True,
            )
        with Horizontal():
            yield Label("Last name: ")
            yield Input(
                id="last_name",
                placeholder="Search by last name",
                type="text",
                compact=True,
            )
        yield Label("\n")
        yield Button("Search", id="search", compact=True)

    @on(Input.Submitted)
    def _any_input_submitted(self, event: Input.Submitted) -> None:
        event.stop()
        self.app.action_focus_next()

    @on(Key)
    def _on_key(self, event: Key) -> None:
        if event.key == "escape" or event.key == "q":
            self.app.exit()

    @on(Button.Pressed, "#search")
    def _search(self):
        inputs = list(self.query(Input))

        if all(i.value.strip() == "" for i in inputs):
            self.notify("There is empty search field", severity="error", timeout=3)
            return

        passport_no = self.query_one("#passport_no", Input).value.strip()
        first_name = self.query_one("#first_name", Input).value.strip()
        last_name = self.query_one("#last_name", Input).value.strip()
        customers = self._customer_service.search_users(
            passport_no, first_name, last_name
        )
        self.app.push_screen(_CustomerListTableScren(customers))


class _CustomerListTableScren(Screen):
    def __init__(self, data: list[Customer]):
        super().__init__()
        self._data = data

    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns(
            "Passport no",
            "First name",
            "Last name",
            "Gender",
            "Age",
            "Country",
            "Mobile",
            "Address",
            "Registerd at",
        )

        rows = []
        for item in self._data:
            passport_no = item.passport.no
            first_name = item.passport.first_name
            last_name = item.passport.last_name
            gender = item.passport.gender
            age = calculate_age(item.birthdate)
            country = item.passport.country_code
            mobile = item.mobile_no
            address = item.address
            created_at = item.created_at
            rows.append(
                (
                    passport_no,
                    first_name,
                    last_name,
                    gender,
                    age,
                    country,
                    mobile,
                    address,
                    created_at,
                )
            )
        table.add_rows(rows)

    @on(Key)
    def _on_key(self, event: Key) -> None:
        if event.key == "escape" or event.key == "q":
            self.app.pop_screen()

    @on(DataTable.RowSelected)
    def handle_row_selected(self, ev: DataTable.RowSelected) -> None:
        row_index = ev.cursor_row
        self.app.exit(self._data[row_index])
