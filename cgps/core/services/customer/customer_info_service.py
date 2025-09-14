from datetime import datetime
from cgps.core.database import Database
from cgps.core.models.customer import Customer
from cgps.core.models.db_model import ISO_DT, only_keys
from cgps.core.models.driver_license import DriverLicense
from cgps.core.models.passport import Passport


class CustomerInfoService:
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
        customer.password = ''
        customer.passport = passport
        customer.driver_license = license
        return customer

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
        passport_cols = list(passport_data.keys())
        passport_sql = f"UPDATE passports SET {", ".join(f"{c}=:{c}" for c in passport_cols)} WHERE id=:id"
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
        license_cols = list(license_data.keys())
        license_sql = f"UPDATE driver_licenses SET {", ".join(f"{c}=:{c}" for c in license_cols)} WHERE id=:id"
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
        customer_cols = list(customer_data.keys())
        customer_sql = f"UPDATE customers SET {", ".join(f"{c}=:{c}" for c in customer_cols)} WHERE id=:id"
        self._database.execute(customer_sql, customer_data)
        self._database.commit()

        return customer
