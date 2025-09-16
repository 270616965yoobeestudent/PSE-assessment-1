from datetime import datetime
from typing import Optional
from cgps.core.database import Database
from cgps.core.models.customer import Customer
from cgps.core.models.driver_license import DriverLicense
from cgps.core.models.passport import Passport
from cgps.core.utils import ISO_DT, only_keys, strip_prefix, to_update_column


class CustomerService:
    def __init__(self, database: Database):
        self._database = database

    def get_info(self, customer_id: int) -> Customer:
        customer_data = self._database.fetchone(
            "SELECT * FROM customers WHERE id = ?", (customer_id,)
        )
        customer: Customer = Customer.from_row(customer_data)
        passport_data = self._database.fetchone(
            "SELECT * FROM passports WHERE id = ?", (customer.passport_id,)
        )
        license_data = self._database.fetchone(
            "SELECT * FROM driver_licenses WHERE id = ?", (customer.driver_license_id,)
        )
        passport: Passport = Passport.from_row(passport_data)
        license: DriverLicense = DriverLicense.from_row(license_data)
        customer.password = ""
        customer.passport = passport
        customer.driver_license = license
        return customer

    def search_users(
        self,
        passport_no: Optional[str],
        first_name: Optional[str],
        last_name: Optional[str],
    ) -> list[Customer]:
        filters = []
        params = {}

        if passport_no and passport_no != "":
            filters.append("p.no LIKE :passport_no")
            params["passport_no"] = f"%{passport_no}%"

        if first_name and first_name != "":
            filters.append("p.first_name LIKE :first_name")
            params["first_name"] = f"%{first_name}%"

        if last_name and last_name != "":
            filters.append("p.last_name LIKE :last_name")
            params["last_name"] = f"%{last_name}%"

        where_clause = " AND ".join(filters)
        if where_clause:
            where_clause = "WHERE " + where_clause

        query = f"""
            SELECT customers.*,
                p.id AS passport__id,
                p.no AS passport__no,
                p.country_code AS passport__country_code,
                p.gender AS passport__gender,
                p.first_name AS passport__first_name,
                p.last_name AS passport__last_name,
                p.expired_at AS passport__expired_at,
                p.created_at AS passport__created_at,
                p.updated_at AS passport__updated_at
            FROM customers
            JOIN passports p ON customers.passport_id = p.id
            {where_clause}
        """

        rows = self._database.fetchall(query, params)

        invoices: list[Customer] = []
        for row in rows:
            passport_data = strip_prefix(row, "passport__")
            customer: Customer = Customer.from_row(row)
            passport: Passport = Passport.from_row(passport_data)
            customer.passport = passport
            invoices.append(customer)
        return invoices

    def update_info(self, customer: Customer) -> Customer:
        now = datetime.now().strftime(ISO_DT)

        self._database.begin()
        passport_data = customer.passport.to_db()
        passport_data = only_keys(
            passport_data,
            [
                "id",
                "no",
                "country_code",
                "gender",
                "first_name",
                "last_name",
                "expired_at",
                "updated_at",
            ],
        )
        passport_data.update(updated_at=now)
        passport_sql = (
            f"UPDATE passports SET {to_update_column(passport_data)} WHERE id=:id"
        )
        self._database.execute(passport_sql, passport_data)

        license_data = customer.driver_license.to_db()
        license_data = only_keys(
            license_data,
            [
                "id",
                "no",
                "country_code",
                "expired_at",
                "updated_at",
            ],
        )
        license_data.update(updated_at=now)
        license_sql = (
            f"UPDATE driver_licenses SET {to_update_column(license_data)} WHERE id=:id"
        )
        self._database.execute(license_sql, license_data)

        customer_data = customer.to_db()
        customer_data.update(updated_at=now)
        customer_data = only_keys(
            customer_data,
            [
                "id",
                "username",
                "email_address",
                "address",
                "birthdate",
                "mobile_no",
                "passport_id",
                "driver_license_id",
                "updated_at",
            ],
        )
        customer_sql = (
            f"UPDATE customers SET {to_update_column(customer_data)} WHERE id=:id"
        )
        self._database.execute(customer_sql, customer_data)
        self._database.commit()

        return True
