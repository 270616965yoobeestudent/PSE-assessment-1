from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from cgps.core.models.db_model import DBModel, to_date, to_dt


@dataclass
class Passport(DBModel):
    id: int
    no: str
    country_code: str
    gender: Optional[str] = None
    first_name: str = ""
    last_name: str = ""
    expired_at: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    _converters = {
        "expired_at": to_date,
        "created_at": to_dt,
        "updated_at": to_dt,
    }
