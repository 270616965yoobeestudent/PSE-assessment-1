from dataclasses import dataclass
from typing import Optional

from cgps.core.models.db_model import DBModel


@dataclass
class TrackingDevice(DBModel):
    no: str
    gsm_provider: Optional[str] = None
    gsm_no: Optional[str] = None
