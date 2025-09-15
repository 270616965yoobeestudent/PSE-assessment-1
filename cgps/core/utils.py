from datetime import date, datetime, timedelta
from decimal import Decimal
import math
from typing import Mapping, Optional

ISO_DT = "%Y-%m-%d %H:%M:%S"


def to_bool(v) -> Optional[bool]:
    if v is None:
        return None
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    if s in {"1", "true", "t", "yes", "y"}:
        return True
    if s in {"0", "false", "f", "no", "n", ""}:
        return False
    return bool(v)


def to_date(v) -> Optional[date]:
    if v in (None, ""):
        return None
    if isinstance(v, date) and not isinstance(v, datetime):
        return v
    return date.fromisoformat(str(v)[:10])


def to_dt(v) -> Optional[datetime]:
    if v in (None, ""):
        return None
    if isinstance(v, datetime):
        return v
    s = str(v).replace("T", " ").split(".")[0]
    # expect "YYYY-MM-DD HH:MM:SS" or "YYYY-MM-DD"
    if " " in s:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    return datetime.combine(date.fromisoformat(s), datetime.min.time())


def to_decimal(v) -> Optional[Decimal]:
    if v in (None, ""):
        return None
    return v if isinstance(v, Decimal) else Decimal(str(v))


def only_keys(d: dict, keys: list[str]) -> dict:
    return {k: d.get(k) for k in keys}


def strip_prefix(d: dict, prefix: str) -> dict:
    return {k[len(prefix) :]: v for k, v in d.items() if k.startswith(prefix)}


def to_update_column(data: dict[str, any]) -> str:
    cols = list(data.keys())
    return ", ".join(f"{c}=:{c}" for c in cols)


def to_insert_column(data: dict[str, any]) -> str:
    cols = list(data.keys())
    return f"({','.join(cols)}) VALUES ({','.join(':'+c for c in cols)})"

def to_days(start: datetime, end: datetime) -> int:
    return math.ceil((end - start).total_seconds() / 86400)

def count_days(start: datetime, end: datetime) -> Mapping[str, int]:
    total_days = to_days(start, end)
    weekdays = 0
    weekends = 0
    for i in range(total_days):
        current_day = start + timedelta(days=i)
        if current_day.weekday() >= 5:  # 5 = Sat, 6 = Sun
            weekends += 1
        else:
            weekdays += 1
    return {"weekdays": weekdays, "weekends": weekends}
