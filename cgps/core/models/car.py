from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from cgps.core.models.db_model import DBModel
from cgps.core.models.tracking import Tracking
from cgps.core.models.tracking_device import TrackingDevice
from cgps.core.utils import to_bool, to_date, to_decimal, to_dt


@dataclass
class Car(DBModel):
    id: int
    plate_license: str
    engine_number: Optional[str] = None
    fuel_type: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    type: Optional[str] = None
    seat: Optional[int] = None
    mileage: Optional[int] = None
    minimum_rent: Optional[int] = None
    maximum_rent: Optional[int] = None
    factory_date: Optional[date] = None
    weekday_rate: Optional[Decimal] = None
    weekend_rate: Optional[Decimal] = None
    available: Optional[bool] = None
    tracking_device_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tracking_device: Optional["TrackingDevice"] = None
    trackings: Optional[List["Tracking"]] = None
    _converters = {
        "factory_date": to_date,
        "weekday_rate": to_decimal,
        "weekend_rate": to_decimal,
        "available": to_bool,
        "created_at": to_dt,
        "updated_at": to_dt,
    }
