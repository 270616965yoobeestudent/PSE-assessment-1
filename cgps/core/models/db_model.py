from __future__ import annotations
from dataclasses import dataclass, fields
from datetime import date, datetime
from decimal import Decimal
from typing import ClassVar, Optional, Dict, Any

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


@dataclass
class DBModel:
    """Base for SQLite rows."""

    _converters: ClassVar[Dict[str, Any]] = {}

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "DBModel":
        conv = getattr(cls, "_converters", {}) or {}
        kw = {}
        for f in fields(cls):
            if f.name.startswith("_"): 
                continue
            v = row.get(f.name)
            if v is not None and f.name in conv:
                v = conv[f.name](v)
            kw[f.name] = v
        return cls(**kw)

    def to_db(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for f in fields(self):
            if f.name.startswith("_"): 
                continue
            v = getattr(self, f.name)
            if v is None:
                out[f.name] = None
                continue
            if isinstance(v, bool):
                out[f.name] = 1 if v else 0
            elif isinstance(v, datetime):
                out[f.name] = v.strftime(ISO_DT)
            elif isinstance(v, date):
                out[f.name] = v.isoformat()
            elif isinstance(v, Decimal):
                out[f.name] = str(v) 
            else:
                out[f.name] = v
        return out
