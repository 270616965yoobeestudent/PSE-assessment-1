from datetime import datetime
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

    def list(self):
        data = self._database.fetchall("SELECT * FROM tracking_devices")
        return [TrackingDevice.from_row(d) for d in data]

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
