from textual.validation import Validator, ValidationResult


class RequireValidator(Validator):
    def __init__(self, message: str = "This field is required"):
        self.message = message

    def validate(self, value: str) -> ValidationResult:
        return self.success() if (value or "").strip() else self.failure(self.message)
