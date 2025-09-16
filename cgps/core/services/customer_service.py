from datetime import datetime
from cgps.core.database import Database
from cgps.core.models.customer import Customer
from cgps.core.models.driver_license import DriverLicense
from cgps.core.models.passport import Passport
from cgps.core.utils import ISO_DT, only_keys, to_update_column


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

    def list(self) -> list[Customer]:
        data = self._database.fetchall("SELECT * FROM customers")
        return [Customer.from_row(d) for d in data]
    
    def get_user_by_passport(self, passport_no: str) -> Customer:
        customer_data = self._database.fetchone(
            "SELECT * FROM customers WHERE passport_no = ?", (passport_no,)
        )
        if customer_data is None:
            return None
        return Customer.from_row(customer_data)

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
