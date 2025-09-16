from datetime import datetime
from math import ceil
from cgps.core.database import Database
from cgps.core.models.car import Car
from cgps.core.utils import (
    ISO_DT,
    only_keys,
    to_days,
    to_insert_column,
    to_update_column,
)


class CarService:
    def __init__(self, database: Database):
        self._database = database

    def list_available(self, started_at: datetime, ended_at: datetime):
        days = to_days(started_at, ended_at)
        cars_data = self._database.fetchall(
            """
            SELECT *
            FROM cars
            WHERE available = 1
            AND id NOT IN (
                SELECT car_id
                FROM orders
                WHERE ended_at > :started_at
                AND started_at < :ended_at
                AND rejected_at IS NULL
            )
            AND minimum_rent <= :days
            AND maximum_rent >= :days
            ORDER BY weekday_rate ASC;
            """,
            {"started_at": started_at, "ended_at": ended_at, "days": days},
        )
        return [Car.from_row(d) for d in cars_data]

    def all(self) -> list[Car]:
        data = self._database.fetchall("SELECT * FROM cars")
        return [Car.from_row(d) for d in data]

    def register(self, car: Car):
        now = datetime.now().strftime(ISO_DT)

        car_data = car.to_db()
        car_data = only_keys(
            car_data,
            [
                "plate_license",
                "engine_number",
                "fuel_type",
                "make",
                "model",
                "year",
                "color",
                "type",
                "seat",
                "factory_date",
                "weekday_rate",
                "weekend_rate",
                "available",
                "tracking_device_id",
                "created_at",
                "updated_at",
                "mileage",
                "minimum_rent",
                "maximum_rent",
            ],
        )
        car_data.update(created_at=now, updated_at=now)
        car_sql = f"INSERT INTO cars {to_insert_column(car_data)}"
        self._database.begin()
        self._database.execute(car_sql, car_data)
        self._database.commit()
        return True

    def update(self, car: Car):
        now = datetime.now().strftime(ISO_DT)
        car_data = car.to_db()
        print(car_data)
        car_data = only_keys(
            car_data,
            [
                "id",
                "plate_license",
                "engine_number",
                "fuel_type",
                "make",
                "model",
                "year",
                "color",
                "type",
                "seat",
                "factory_date",
                "weekday_rate",
                "weekend_rate",
                "available",
                "tracking_device_id",
                "updated_at",
                "mileage",
                "minimum_rent",
                "maximum_rent",
            ],
        )
        car_data.update(updated_at=now)
        car_sql = f"UPDATE cars SET {to_update_column(car_data)} WHERE id=:id"
        self._database.begin()
        self._database.execute(car_sql, car_data)
        self._database.commit()
        return True
