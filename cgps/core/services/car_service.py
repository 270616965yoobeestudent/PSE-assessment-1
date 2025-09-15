from datetime import datetime
from math import ceil
from cgps.core.database import Database
from cgps.core.models.car import Car


class CarService:
    def __init__(self, database: Database):
        self._database = database

    def list_available(self, started_at: datetime, ended_at: datetime):
        days = ceil((ended_at - started_at).total_seconds() / 86400)
        cars_data = self._database.fetchall(
            """
            SELECT *
            FROM cars
            WHERE available = 1
            AND plate_license NOT IN (
                SELECT car_plate_license
                FROM orders
                WHERE ended_at > :started_at
                AND started_at < :ended_at
            )
            AND minimum_rent <= :days
            AND maximum_rent >= :days
            ORDER BY weekday_rate ASC;
            """,
            {"started_at": started_at, "ended_at": ended_at, "days": days},
        )
        return [Car.from_row(d) for d in cars_data]
