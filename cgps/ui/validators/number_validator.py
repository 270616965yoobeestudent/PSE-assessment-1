from textual.validation import Validator, ValidationResult


class NumberValidator(Validator):
    def __init__(self, message: str = "This field should be a whole number"):
        self.message = message

    def validate(self, value: str) -> ValidationResult:
        value = (value or "").strip()
        if value.isdigit():
            return self.success()
        return self.failure(self.message)
