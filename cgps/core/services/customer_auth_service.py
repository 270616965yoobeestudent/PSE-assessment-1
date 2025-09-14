from datetime import datetime
from cgps.core.database import Database
from cgps.core.models.customer import Customer
from cgps.core.services.auth_service import AuthService
from cgps.core.utils import ISO_DT, only_keys


class CustomerAuthService(AuthService):
    def __init__(
        self,
        database: Database,
        service_name: str,
        password_salt: str,
        jwt_secret_key: str,
    ):
        super().__init__(
            database=database,
            service_name=service_name,
            role="customer",
            table_name="customers",
            password_salt=password_salt,
            jwt_secret_key=jwt_secret_key,
        )

    def _verify_driver_license_existing(self, no):
        data = self._database.fetchone(
            f"SELECT no FROM driver_licenses WHERE no = ?",
            (no,),
        )
        return data is not None

    def _verify_passport_existing(self, no):
        data = self._database.fetchone(
            f"SELECT no FROM passports WHERE no = ?",
            (no,),
        )
        return data is not None

    def _verify_username_existing(self, username):
        data = self._database.fetchone(
            f"SELECT username FROM customers WHERE username = ?",
            (username,),
        )
        return data is not None

    def register(self, data: Customer):
        if self._verify_username_existing(data.username):
            return False
        if self._verify_driver_license_existing(data.driver_license.no):
            return False
        if self._verify_passport_existing(data.passport.no):
            return False

        now = datetime.now().strftime(ISO_DT)

        self._database.begin()
        passport_data = data.passport.to_db()
        passport_data = only_keys(
            passport_data,
            [
                "no",
                "country_code",
                "gender",
                "first_name",
                "last_name",
                "expired_at",
            ],
        )
        passport_data.update(created_at=now, updated_at=now)
        passport_cols = list(passport_data.keys())
        passport_sql = f"INSERT INTO passports ({','.join(passport_cols)}) VALUES ({','.join(':'+c for c in passport_cols)})"
        passport_id = self._database.execute(passport_sql, passport_data)

        license_data = data.driver_license.to_db()
        license_data = only_keys(
            license_data,
            [
                "no",
                "country_code",
                "expired_at",
            ],
        )
        license_data.update(created_at=now, updated_at=now)
        license_cols = list(license_data.keys())
        license_sql = f"INSERT INTO driver_licenses ({','.join(license_cols)}) VALUES ({','.join(':'+c for c in license_cols)})"
        license_id = self._database.execute(license_sql, license_data)

        customer_data = data.to_db()
        customer_data.update(
            password=self._encrypt_password(data.password),
            created_at=now,
            updated_at=now,
            passport_id=passport_id,
            driver_license_id=license_id,
        )
        customer_data = only_keys(
            customer_data,
            [
                "username",
                "password",
                "email_address",
                "address",
                "birthdate",
                "mobile_no",
                "passport_id",
                "driver_license_id",
                "created_at",
                "updated_at",
            ],
        )
        customer_cols = list(customer_data.keys())
        customer_sql = f"INSERT INTO customers ({','.join(customer_cols)}) VALUES ({','.join(':'+c for c in customer_cols)})"
        self._database.execute(customer_sql, customer_data)
        self._database.commit()
        return True
