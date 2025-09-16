import re
from datetime import date
from textual.validation import Validator, ValidationResult


class ISODateValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value or ""):
            return self.failure("Format must be YYYY-MM-DD")
        try:
            date.fromisoformat(value)
        except ValueError:
            return self.failure("Invalid date")
        return self.success()
