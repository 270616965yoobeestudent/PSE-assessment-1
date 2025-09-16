import re
from textual.validation import Validator, ValidationResult


class PhoneValidator(Validator):
    def __init__(self, message: str = "Invalid phone", empty_ok: bool = False):
        self.pat = re.compile(r"^\+[1-9]\d{0,2}(?:[- ]?\d{1,4}){2,4}$")
        self.message = message
        self.empty_ok = empty_ok

    def validate(self, value: str) -> ValidationResult:
        v = (value or "").strip()
        if not v:
            return self.success() if self.empty_ok else self.failure("Phone is required")
        return self.success() if self.pat.fullmatch(v) else self.failure(self.message)