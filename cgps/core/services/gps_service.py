from cgps.core.database import Database
from cgps.core.models.tracking_device import TrackingDevice
from cgps.core.services.auth_service import AuthService


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
        pass
