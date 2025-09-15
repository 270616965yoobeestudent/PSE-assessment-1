import re
from datetime import datetime
from textual.validation import Validator, ValidationResult

DATE_TIME_INPUT = "%Y-%m-%d %H:%M"

class ISODateTimeValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", value or ""):
            return self.failure("Format must be YYYY-MM-DD HH:MM")
        try:
            datetime.strptime(value, DATE_TIME_INPUT)
        except ValueError:
            return self.failure("Invalid datetime")
        return self.success()
