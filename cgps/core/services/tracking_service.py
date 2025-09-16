from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Optional

from cgps.core.database import Database
from cgps.core.models.tracking import Tracking
from cgps.core.models.car import Car
from cgps.core.utils import ISO_DT, only_keys, to_insert_column, strip_prefix


class TrackingService:
    def __init__(self, database: Database):
        self._database = database

    def insert_batch(self, batch: Iterable[Tracking]) -> int:
        now = datetime.now().strftime(ISO_DT)
        inserted = 0
        self._database.begin()
        for t in batch:
            data = t.to_db()
            data = only_keys(
                data,
                [
                    "latitude",
                    "longitude",
                    "fuel_level",
                    "fuel_litre",
                    "fuel_kwh",
                    "speed_kmh",
                    "engine_status",
                    "gps_signal_level",
                    "gsm_signal_level",
                    "car_id",
                    "tracking_device_id",
                    "created_at",
                    "updated_at",
                ],
            )
            if data.get("created_at") is None:
                data.update(created_at=now)
            if data.get("updated_at") is None:
                data.update(updated_at=now)
            sql = f"INSERT INTO trackings {to_insert_column(data)}"
            new_id = self._database.execute(sql, data)
            try:
                t.id = int(new_id)
            except Exception:
                pass
            inserted += 1
        self._database.commit()
        return inserted

    def insert(self, batches: Iterable[List[Tracking]], max_rows: Optional[int] = None) -> int:
        total = 0
        for batch in batches:
            if not batch:
                continue
            count = self.insert_batch(batch)
            total += count
            if max_rows is not None and total >= max_rows:
                break
        return total

    def list_with_car(
        self, car_id: Optional[int] = None, limit: Optional[int] = None
    ) -> list[tuple[Tracking, Car]]:
        where = ""
        params: dict[str, object] = {}
        if car_id is not None:
            where = " WHERE t.car_id = :car_id"
            params["car_id"] = car_id
        extra = ""
        if limit is not None:
            extra = " LIMIT :limit"
            params["limit"] = limit
        rows = self._database.fetchall(
            f"""
            SELECT
                t.*,
                c.id              AS car__id,
                c.plate_license   AS car__plate_license,
                c.engine_number   AS car__engine_number,
                c.fuel_type       AS car__fuel_type,
                c.make            AS car__make,
                c.model           AS car__model,
                c.year            AS car__year,
                c.color           AS car__color,
                c.type            AS car__type,
                c.seat            AS car__seat,
                c.mileage         AS car__mileage,
                c.minimum_rent    AS car__minimum_rent,
                c.maximum_rent    AS car__maximum_rent,
                c.factory_date    AS car__factory_date,
                c.weekday_rate    AS car__weekday_rate,
                c.weekend_rate    AS car__weekend_rate,
                c.available       AS car__available,
                c.tracking_device_id AS car__tracking_device_id,
                c.created_at      AS car__created_at,
                c.updated_at      AS car__updated_at
            FROM trackings t
            JOIN cars c ON c.id = t.car_id
            {where}
            ORDER BY t.id DESC{extra}
            """,
            params,
        )
        out: list[tuple[Tracking, Car]] = []
        for row in rows:
            car_data = strip_prefix(row, "car__")
            t = Tracking.from_row(row)
            c = Car.from_row(car_data)
            out.append((t, c))
        return out
