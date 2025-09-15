from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from cgps.core.models.db_model import DBModel
from cgps.core.utils import to_dt


@dataclass
class TrackingDevice(DBModel):
    no: str
    gsm_provider: Optional[str] = None
    gsm_no: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    _converters = {
        "created_at": to_dt,
        "updated_at": to_dt,
    }


