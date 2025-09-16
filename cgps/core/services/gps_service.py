from datetime import datetime
from typing import Optional
import uuid
from cgps.core.database import Database
from cgps.core.models.tracking_device import TrackingDevice
from cgps.core.utils import ISO_DT, only_keys, to_insert_column, to_update_column


class GpsService:
    def __init__(
        self,
        database: Database,
    ):
        self._database = database

    def all(self) -> list[TrackingDevice]:
        data = self._database.fetchall("SELECT * FROM tracking_devices")
        return [TrackingDevice.from_row(d) for d in data]

    def get_available(self, car_id: Optional[int]) -> list[TrackingDevice]:
        where_clause = "WHERE tracking_device_id IS NOT NULL"
        params = {}

        if car_id is not None:
            where_clause += " AND id != :car_id"
            params["car_id"] = car_id

        query = f"""
            SELECT *
            FROM tracking_devices
            WHERE id NOT IN (
                SELECT tracking_device_id
                FROM cars
                {where_clause}
            )
        """
        rows = self._database.fetchall(query, params)
        return [TrackingDevice.from_row(d) for d in rows]

    def register(self, device: TrackingDevice):
        now = datetime.now().strftime(ISO_DT)

        device_data = device.to_db()
        device_data = only_keys(
            device_data,
            [
                "gsm_provider",
                "gsm_no",
                "created_at",
                "updated_at",
            ],
        )
        device_data.update(created_at=now, updated_at=now)
        device_sql = f"INSERT INTO tracking_devices {to_insert_column(device_data)}"
        self._database.begin()
        self._database.execute(device_sql, device_data)
        self._database.commit()
        return True

    def update(self, device: TrackingDevice) -> bool:
        now = datetime.now().strftime(ISO_DT)
        device_data = device.to_db()
        device_data = only_keys(
            device_data,
            [
                "id",
                "gsm_provider",
                "gsm_no",
                "updated_at",
            ],
        )
        device_data.update(updated_at=now)
        device_sql = (
            f"UPDATE tracking_devices SET {to_update_column(device_data)} WHERE id=:id"
        )
        self._database.begin()
        self._database.execute(device_sql, device_data)
        self._database.commit()
        return True
