from cgps.core.database import Database
from cgps.core.models.car import Car
from cgps.core.models.db_model import _strip_prefix
from cgps.core.models.invoice import Invoice
from cgps.core.models.order import Order


class CustomerOrderService:
    def __init__(self, database: Database):
        self._database = database

    def my_orders(self, customer_id) -> list[Invoice]:
        rows = self._database.fetchall(
            """
            SELECT
            o.*,
            i.id AS invoice__id,
            i.order_id AS invoice__order_id,
            i.amount AS invoice__amount,
            i.paid_amount AS invoice__paid_amount,
            i.paid_at AS invoice__paid_at,
            i.created_at AS invoice__created_at,
            i.updated_at AS invoice__updated_at,
            c.plate_license AS car__plate_license,
            c.engine_number AS car__engine_number,
            c.fuel_type AS car__fuel_type,
            c.make AS car__make,
            c.model AS car__model,
            c.year AS car__year,
            c.color AS car__color,
            c.type AS car__type,
            c.seat AS car__seat,
            c.factory_date AS car__factory_date,
            c.weekday_rate AS car__weekday_rate,
            c.weekend_rate AS car__weekend_rate,
            c.available AS car__available,
            c.tracking_device_no AS car__tracking_device_no,
            c.created_at AS car__created_at,
            c.updated_at AS car__updated_at
            FROM invoices i
            JOIN orders o ON o.id = i.order_id
            JOIN cars c ON c.plate_license = o.car_plate_license
            WHERE o.customer_id = ?
            ORDER BY o.started_at DESC
            """,
            (customer_id,),
        )
        invoices: list[Invoice] = []
        for row in rows:           
            car_data = _strip_prefix(row, "car__")
            order: Order = Order.from_row(row)  
            order.car = Car.from_row(car_data)
            invoice_data = _strip_prefix(row, "invoice__")
            invoice: Invoice = Invoice.from_row(invoice_data)
            invoice.order = order
            invoices.append(invoice)
        return invoices
