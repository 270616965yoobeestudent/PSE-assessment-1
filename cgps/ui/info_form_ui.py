from typing import Any
from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Input, Label, Select, Button, MaskedInput
from textual.events import Key
from textual.containers import Horizontal

from cgps.core.models.customer import Customer
from cgps.core.models.passport import Passport
from cgps.core.models.driver_license import DriverLicense
from cgps.ui.validators.match_validator import MatchesInput
from cgps.ui.validators.email_validator import EmailValidator
from cgps.ui.validators.iso_date_validator import ISODateValidator
from cgps.ui.validators.phone_validator import PhoneValidator
from cgps.ui.validators.require_validator import RequireValidator


class InfoFormUi(App):
    CSS = """
    Label.header { text-style: bold; }
    Label { color: grey; }
    Horizontal { height: auto; }
    """
    
    def with_data(self, data: Any, can_update: bool):
        self._data = data
        self._can_update = can_update
        return self
    
    def compose(self) -> ComposeResult:
        yield Label("General information:", classes="header")
        with Horizontal():
            yield Label("Email: ")
            yield Input(
                id="email",
                placeholder="Enter email e.g. example@gmail.com",
                type="text",
                value=self._data['email_address'],
                validators=[EmailValidator()],
                compact=True,
            )
        with Horizontal():
            yield Label("Address: ")
            yield Input(
                id="address",
                placeholder="Enter address",
                type="text",
                value=self._data['address'],
                validators=[RequireValidator()],
                compact=True
            )
        with Horizontal():
            yield Label("Birthdate: ")
            yield MaskedInput(
                id="birthdate",
                template="0000-00-00",
                placeholder="YYYY-MM-DD",
                value=self._data['birthdate'],
                validators=[ISODateValidator()],
                compact=True
            )
        with Horizontal():
            yield Label("Mobile: ")
            yield Input(
                id="mobile",
                placeholder="Enter mobile e.g. +64-21-555-1001",
                type="text",
                value=self._data['mobile_no'],
                validators=[PhoneValidator()],
                compact=True
            )
        yield Label("\n")
        yield Label("Passport information:", classes="header")
        with Horizontal():
            yield Label("passport no: ")
            yield Input(
                id="passport-no",
                placeholder="Enter passport no",
                type="text",
                value=self._data['passport']['no'],
                validators=[RequireValidator()],
                compact=True
            )
        with Horizontal():
            yield Label("Country code: ")
            yield Select(
                [("New Zealand", "NZ"), ("Australia", "AU")],
                value=self._data['passport']['country_code'],
                id="passport-country",
                allow_blank=False,
                compact=True
            )
        with Horizontal():
            yield Label("Gender: ")
            yield Select(
                [("Female", "F"), ("Male", "M")],
                value=self._data['passport']['gender'],
                id="passport-gender",
                allow_blank=False,
                compact=True
            )
        with Horizontal():
            yield Label("First name: ")
            yield Input(
                id="passport-first-name",
                placeholder="Enter passport first name",
                type="text",
                value=self._data['passport']['first_name'],
                validators=[RequireValidator()],
                compact=True
            )
        with Horizontal():
            yield Label("Last name: ")
            yield Input(
                id="passport-last-name",
                placeholder="Enter passport last name",
                type="text",
                value=self._data['passport']['last_name'],
                validators=[RequireValidator()],
                compact=True
            )
        with Horizontal():
            yield Label("Expire date: ")
            yield MaskedInput(
                id="passport-expired-at",
                template="0000-00-00",
                placeholder="YYYY-MM-DD",
                value=self._data['passport']['expired_at'],
                validators=[ISODateValidator()],
                compact=True
            )

        yield Label("\n")
        yield Label("Driver license information:", classes="header")
        with Horizontal():
            yield Label("Driver license no: ")
            yield Input(
                id="driver-license-no",
                placeholder="Enter driver license no",
                type="text",
                value=self._data['driver_license']['no'],
                validators=[RequireValidator()],
                compact=True
            )
        with Horizontal():
            yield Label("Country code: ")
            yield Select(
                [("New Zealand", "NZ"), ("Australia", "AU")],
                value=self._data['driver_license']['country_code'],
                id="driver-license-country",
                allow_blank=False,
                compact=True
            )
        with Horizontal():
            yield Label("Expire date: ")
            yield MaskedInput(
                id="driver-license-expired-at",
                template="0000-00-00",
                placeholder="YYYY-MM-DD",
                value=self._data['driver_license']['expired_at'],
                validators=[ISODateValidator()],
                compact=True
            )
        yield Label("\n")
        if self._can_update:
            yield Button("Update", id="update", compact=True)

    @on(Input.Submitted)
    def _any_input_submitted(self, event: Input.Submitted) -> None:
        event.stop()
        self.action_focus_next()

    @on(Key)
    def _on_key(self, event: Key) -> None:
        if event.key == "escape":
            self.exit()

    @on(Button.Pressed, "#update")
    async def _action(self):
        inputs = list(self.query(Input))
        results = [w.validate(w.value) for w in inputs]

        if not all(r.is_valid for r in results):
            bad = next(w for w, r in zip(inputs, results) if not r.is_valid)
            bad.focus()
            self.notify("Please correct the errors above", severity="error", timeout=3)
            return

        data = Customer(
            id=self._data['id'],
            username=self._data['username'],
            password='',
            email_address=self.query_one("#email", Input).value,
            address=self.query_one("#address", Input).value,
            birthdate=self.query_one("#birthdate", Input).value,
            mobile_no=self.query_one("#mobile", Input).value,
            passport_id=self._data['passport']['id'],
            driver_license_id=self._data['driver_license']['id'],
            created_at=self._data['created_at'],
            passport=Passport(
                id=self._data['passport']['id'],
                no=self.query_one("#passport-no", Input).value,
                country_code=self.query_one("#passport-country", Select).value,
                gender=self.query_one("#passport-gender", Select).value,
                first_name=self.query_one("#passport-first-name", Input).value,
                last_name=self.query_one("#passport-last-name", Input).value,
                expired_at=self.query_one("#passport-expired-at", Input).value,
                created_at=self._data['passport']['created_at'],
            ),
            driver_license=DriverLicense(
                id=self._data['driver_license']['id'],
                no=self.query_one("#driver-license-no", Input).value,
                country_code=self.query_one("#driver-license-country", Select).value,
                expired_at=self.query_one("#driver-license-expired-at", Input).value,
                created_at=self._data['driver_license']['created_at'],
            ),
        )
        self.exit(data)
