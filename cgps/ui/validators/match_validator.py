from textual.widgets import Input
from textual.validation import Validator, ValidationResult


class MatchesInput(Validator):
    def __init__(self, other: Input, message: str = "Passwords do not match"):
        self.other = other
        self.message = message

    def validate(self, value: str) -> ValidationResult:
        return (
            self.success()
            if value == (self.other.value or "")
            else self.failure(self.message)
        )
