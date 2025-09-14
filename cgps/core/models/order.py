from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from cgps.core.models.car import Car
from cgps.core.models.customer import Customer
from cgps.core.models.db_model import DBModel, to_decimal, to_dt
from cgps.core.models.invoice import Invoice


@dataclass
class Order(DBModel):
    id: int
    customer_id: int
    car_plate_license: str
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    receive_at: Optional[datetime] = None
    return_at: Optional[datetime] = None
    total_day: Optional[int] = None
    total_weekday_amount: Optional[Decimal] = None
    total_weekend_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    customer: Optional["Customer"] = None
    car: Optional["Car"] = None
    invoice: Optional["Invoice"] = None
    _converters = {
        "started_at": to_dt,
        "ended_at": to_dt,
        "receive_at": to_dt,
        "return_at": to_dt,
        "total_weekday_amount": to_decimal,
        "total_weekend_amount": to_decimal,
        "total_amount": to_decimal,
        "created_at": to_dt,
        "updated_at": to_dt,
    }
