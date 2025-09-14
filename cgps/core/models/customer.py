from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from cgps.core.models.db_model import DBModel, to_date, to_dt
from cgps.core.models.driver_license import DriverLicense
from cgps.core.models.passport import Passport


@dataclass
class Customer(DBModel):
    id: int
    username: str
    password: str
    email_address: Optional[str] = None
    address: Optional[str] = None
    birthdate: Optional[date] = None
    mobile_no: Optional[str] = None
    passport_id: Optional[int] = None
    driver_license_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    passport: Optional["Passport"] = None
    driver_license: Optional["DriverLicense"] = None
    _converters = {
        "birthdate": to_date,
        "created_at": to_dt,
        "updated_at": to_dt,
    }
