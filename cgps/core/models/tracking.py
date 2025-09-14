from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from cgps.core.models.db_model import DBModel
from cgps.core.utils import to_bool, to_dt


@dataclass
class Tracking(DBModel):
    id: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    fuel_level: Optional[float] = None
    fuel_litre: Optional[float] = None
    fuel_kwh: Optional[float] = None
    speed_kmh: Optional[float] = None
    engine_status: Optional[bool] = None
    gps_signal_level: Optional[float] = None
    gsm_signal_level: Optional[float] = None
    car_plate_license: str = ""
    tracking_device_no: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    _converters = {
        "engine_status": to_bool,
        "created_at": to_dt,
        "updated_at": to_dt,
    }
