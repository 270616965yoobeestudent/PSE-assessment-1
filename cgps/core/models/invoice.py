from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sympy import Order

from cgps.core.models.db_model import DBModel
from cgps.core.utils import to_decimal, to_dt


@dataclass
class Invoice(DBModel):
    id: int
    order_id: int
    amount: Decimal
    paid_amount: Optional[Decimal] = None
    paid_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    order: Optional["Order"] = None
    _converters = {
        "amount": to_decimal,
        "paid_amount": to_decimal,
        "paid_at": to_dt,
        "created_at": to_dt,
        "updated_at": to_dt,
    }
