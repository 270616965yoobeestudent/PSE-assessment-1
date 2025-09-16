from __future__ import annotations

from textual import on
from textual.app import App, ComposeResult
from textual.widgets import DataTable
from textual.events import Key
from textual.screen import Screen
from textual.timer import Timer

from cgps.core.models.tracking import Tracking
from cgps.core.models.car import Car
from cgps.core.services.tracking_service import TrackingService
from cgps.core.mock_tracking import trackings_iter
from cgps.core.utils import ISO_DT
from datetime import datetime


class TrackingReportUi(App):
    CSS = """
    Label.header { text-style: bold; }
    """

    def __init__(self, tracking_service: TrackingService) -> None:
        super().__init__()
        self._tracking_service = tracking_service
        self._data: list[tuple[Tracking, Car]] = []
        self._stream_cars: list[Car]
        self._stream_interval: float = 1.0

    def with_data(self, data: list[tuple[Tracking, Car]]):
        self._data = data
        return self

    def with_stream(
        self,
        *,
        cars: list[Car],
        interval_sec: float = 1.0,
    ):
        self._stream_cars = [car for car in cars if car.tracking_device_id is not None]
        self._stream_interval = interval_sec
        return self

    def on_mount(self) -> None:
        self.push_screen(
            _TrackingReportTableScreen(
                self._data,
                self._tracking_service,
                self._stream_cars,
                self._stream_interval,
            )
        )


class _TrackingReportTableScreen(Screen):
    def __init__(
        self,
        data: list[tuple[Tracking, Car]],
        tracking_service: TrackingService,
        stream_cars: list[Car],
        interval_sec: float,
    ):
        super().__init__()
        self._data = data
        self._timer: Timer
        self._iter = None
        self._car_map: dict[int, Car] = {}
        self._tracking_service = tracking_service
        self._stream_cars = stream_cars
        self._interval_sec = interval_sec
        self._rows_cache: list[tuple] = []

    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns(
            "Tracking ID",
            "Time",
            "Car ID",
            "Plate",
            "Make",
            "Model",
            "Year",
            "Fuel Type",
            "Lat",
            "Lng",
            "Speed (km/h)",
            "Engine",
            "Fuel %",
            "Fuel (L)",
            "Battery (kWh)",
            "GPS Sig",
            "GSM Sig",
        )
        rows = []
        for (t, car) in self._data:
            self._car_map[car.id] = car
            ts = t.created_at.strftime(ISO_DT) if isinstance(t.created_at, datetime) else t.created_at
            rows.append(
                (
                    t.id,
                    ts,
                    car.id,
                    car.plate_license,
                    car.make,
                    car.model,
                    car.year,
                    car.fuel_type,
                    t.latitude,
                    t.longitude,
                    t.speed_kmh,
                    "ON" if t.engine_status else "OFF",
                    t.fuel_level,
                    t.fuel_litre,
                    t.fuel_kwh,
                    t.gps_signal_level,
                    t.gsm_signal_level,
                )
            )
        table.add_rows(rows)
        self._rows_cache = list(rows)
        cars = self._stream_cars
        if cars:
            for car in cars:
                self._car_map[car.id] = car
            self._iter = trackings_iter(cars=cars)
            self._timer = self.set_interval(self._interval_sec, self._tick_stream)

    def _tick_stream(self) -> None:
        if self._iter is None:
            return
        try:
            batch = next(self._iter)
        except StopIteration:
            if self._timer:
                self._timer.stop()
            return
        self._tracking_service.insert_batch(batch)
        self._append_rows(batch)
        

    @on(Key)
    def _on_key(self, event: Key) -> None:
        if event.key == "escape" or event.key == "q":
            if self._timer:
                self._timer.stop()
            self.app.exit()

    def _append_rows(self, batch: list[Tracking]) -> None:
        table = self.query_one(DataTable)
        new_rows = []
        for t in batch:
            car = self._car_map.get(t.car_id)
            if not car:
                continue
            ts = t.created_at.strftime(ISO_DT) if isinstance(t.created_at, datetime) else t.created_at
            new_rows.append(
                (
                    t.id,
                    ts,
                    car.id,
                    car.plate_license,
                    car.make,
                    car.model,
                    car.year,
                    car.fuel_type,
                    t.latitude,
                    t.longitude,
                    t.speed_kmh,
                    "ON" if t.engine_status else "OFF",
                    t.fuel_level,
                    t.fuel_litre,
                    t.fuel_kwh,
                    t.gps_signal_level,
                    t.gsm_signal_level,
                )
            )
        table.clear(columns=False)
        for row in reversed(new_rows):
            table.add_row(*row)
        for row in self._rows_cache:
            table.add_row(*row)
        self._rows_cache = list(reversed(new_rows)) + self._rows_cache

    def _append_and_insert(self, batch: list[Tracking]) -> None:
        self._tracking_service.insert_batch(batch)
        self._append_rows(batch)
