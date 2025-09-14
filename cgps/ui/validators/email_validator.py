import re
from textual.validation import Validator, ValidationResult


class EmailValidator(Validator):
    def __init__(self, message: str = "Invalid email", empty_ok: bool = False):
        self.pat = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]{2,}$")
        self.message = message
        self.empty_ok = empty_ok

    def validate(self, value: str) -> ValidationResult:
        v = (value or "").strip()
        if not v:
            return (
                self.success() if self.empty_ok else self.failure("Email is required")
            )
        return self.success() if self.pat.fullmatch(v) else self.failure(self.message)
