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


class RegisterUi(App):
    CSS = """
    Label.header { text-style: bold; }
    Horizontal { height: auto; }
    """

    def compose(self) -> ComposeResult:
        password = Input(
            id="password",
            placeholder="Enter password",
            type="text",
            password=True,
            validators=[RequireValidator()],
            compact=True
        )
        yield Label("Login information:", classes="header")
        with Horizontal():
            yield Label("Username: ")
            yield Input(
                id="username",
                placeholder="Enter username",
                type="text",
                validators=[RequireValidator()],
                compact=True
            )
        with Horizontal():
            yield Label("Password: ")
            yield password
        with Horizontal():
            yield Label("Re-password: ")
            yield Input(
                id="password-confirm",
                placeholder="Enter confirm password",
                type="text",
                password=True,
                validators=[MatchesInput(password)],
                compact=True
        )
        yield Label("\n")
        yield Label("General information:", classes="header")
        with Horizontal():
            yield Label("Email: ")
            yield Input(
                id="email",
                placeholder="Enter email e.g. example@gmail.com",
                type="text",
                validators=[EmailValidator()],
                compact=True
            )
        with Horizontal():
            yield Label("Address: ")
            yield Input(
                id="address",
                placeholder="Enter address",
                type="text",
                validators=[RequireValidator()],
                compact=True
            )
        with Horizontal():
            yield Label("Birthdate: ")
            yield MaskedInput(
                id="birthdate",
                template="0000-00-00",
                placeholder="YYYY-MM-DD",
                validators=[ISODateValidator()],
                compact=True
            )
        with Horizontal():
            yield Label("Mobile: ")
            yield Input(
                id="mobile",
                placeholder="Enter mobile e.g. +642-155-500",
                type="text",
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
                validators=[RequireValidator()],
                compact=True
            )
        with Horizontal():
            yield Label("Country code: ")
            yield Select(
                [("New Zealand", "NZ"), ("Australia", "AU")],
                value="NZ",
                id="passport-country",
                allow_blank=False,
                compact=True
            )
        with Horizontal():
            yield Label("Gender: ")
            yield Select(
                [("Female", "F"), ("Male", "M")],
                value="M",
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
                validators=[RequireValidator()],
                compact=True
            )
        with Horizontal():
            yield Label("Last name: ")
            yield Input(
                id="passport-last-name",
                placeholder="Enter passport last name",
                type="text",
                validators=[RequireValidator()],
                compact=True
            )
        with Horizontal():
            yield Label("Expire date: ")
            yield MaskedInput(
                id="passport-expired-at",
                template="0000-00-00",
                placeholder="YYYY-MM-DD",
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
                validators=[RequireValidator()],
                compact=True
            )
        with Horizontal():
            yield Label("Country code: ")
            yield Select(
                [("New Zealand", "NZ"), ("Australia", "AU")],
                id="driver-license-country",
                value="NZ",
                allow_blank=False,
                compact=True
            )
        with Horizontal():
            yield Label("Expire date: ")
            yield MaskedInput(
                id="driver-license-expired-at",
                template="0000-00-00",
                placeholder="YYYY-MM-DD",
                validators=[ISODateValidator()],
                compact=True
            )
        yield Label("\n")
        yield Button("Register", id="register", compact=True)

    @on(Input.Submitted)
    def _any_input_submitted(self, event: Input.Submitted) -> None:
        event.stop()
        self.action_focus_next()

    @on(Key)
    def _on_key(self, event: Key) -> None:
        if event.key == "escape":
            self.exit()

    @on(Button.Pressed, "#register")
    async def _action(self):
        inputs = list(self.query(Input))
        results = [w.validate(w.value) for w in inputs]

        if not all(r.is_valid for r in results):
            bad = next(w for w, r in zip(inputs, results) if not r.is_valid)
            bad.focus()
            self.notify("Please correct the errors above", severity="error", timeout=3)
            return

        data = Customer(
            id=0,
            username=self.query_one("#username", Input).value,
            password=self.query_one("#password", Input).value,
            email_address=self.query_one("#email", Input).value,
            address=self.query_one("#address", Input).value,
            birthdate=self.query_one("#birthdate", Input).value,
            mobile_no=self.query_one("#mobile", Input).value,
            passport_id=0,
            driver_license_id=0,
            passport=Passport(
                id=0,
                no=self.query_one("#passport-no", Input).value,
                country_code=self.query_one("#passport-country", Select).value,
                gender=self.query_one("#passport-gender", Select).value,
                first_name=self.query_one("#passport-first-name", Input).value,
                last_name=self.query_one("#passport-last-name", Input).value,
                expired_at=self.query_one("#passport-expired-at", Input).value,
            ),
            driver_license=DriverLicense(
                id=0,
                no=self.query_one("#driver-license-no", Input).value,
                country_code=self.query_one("#driver-license-country", Select).value,
                expired_at=self.query_one("#driver-license-expired-at", Input).value,
            ),
        )
        self.exit(data)
