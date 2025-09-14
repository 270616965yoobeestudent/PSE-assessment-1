from __future__ import annotations
from dataclasses import dataclass, fields
from datetime import date, datetime
from decimal import Decimal
from typing import ClassVar, Dict, Any

from cgps.core.utils import ISO_DT

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
