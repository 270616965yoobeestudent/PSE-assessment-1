from __future__ import annotations

import random
from datetime import datetime
from typing import Iterable, List

from cgps.core.models.car import Car
from cgps.core.models.tracking import Tracking


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


class _TrackingsIter:
    def __init__(
        self,
        *,
        cars: List[Car],
        center_lat: float,
        center_lng: float,
    ) -> None:
        self._cars = [car for car in cars if car.tracking_device_id is not None]
        self._center_lat = center_lat
        self._center_lng = center_lng
        self._rnd = random.Random(42)

    def __iter__(self):
        return self

    def __next__(self) -> List[Tracking]:
        now = datetime.now()
        batch: List[Tracking] = []
        for car in self._cars:
            lat = self._center_lat + self._rnd.uniform(-0.1, 0.1)
            lng = self._center_lng + self._rnd.uniform(-0.1, 0.1)
            engine_on = self._rnd.random() < 0.85
            speed = (
                _clamp(self._rnd.gauss(50.0, 25.0), 0.0, 120.0) if engine_on else 0.0
            )
            fuel_pct = _clamp(self._rnd.gauss(60.0, 25.0), 0.0, 100.0)
            tank_capacity_l = 60.0
            pack_kwh = 75.0
            fuel_type = (car.fuel_type or "").lower()
            is_ev = (
                fuel_type in {"ev", "electric", "bev", "phev"}
                or self._rnd.random() < 0.05
            )
            fuel_litre = None
            fuel_kwh = None
            if is_ev:
                fuel_kwh = round(
                    _clamp(pack_kwh * (fuel_pct / 100.0), 0.0, pack_kwh), 1
                )
            else:
                fuel_litre = round(
                    _clamp(tank_capacity_l * (fuel_pct / 100.0), 0.0, tank_capacity_l),
                    1,
                )
            gps_signal = round(_clamp(self._rnd.gauss(3.0, 1.2), 0.0, 5.0), 2)
            gsm_signal = round(_clamp(self._rnd.gauss(3.0, 1.2), 0.0, 5.0), 2)
            batch.append(
                Tracking(
                    id=0,
                    latitude=round(lat, 6),
                    longitude=round(lng, 6),
                    fuel_level=round(fuel_pct, 1),
                    fuel_litre=fuel_litre,
                    fuel_kwh=fuel_kwh,
                    speed_kmh=round(speed, 1),
                    engine_status=engine_on,
                    gps_signal_level=gps_signal,
                    gsm_signal_level=gsm_signal,
                    car_id=car.id,
                    tracking_device_id=car.tracking_device_id,
                    created_at=now,
                    updated_at=now,
                )
            )
        return batch


def trackings_iter(
    *,
    cars: Iterable[Car],
    center_lat: float = -36.8485,
    center_lng: float = 174.7633,
) -> _TrackingsIter:
    return _TrackingsIter(
        cars=list(cars),
        center_lat=center_lat,
        center_lng=center_lng,
    )
