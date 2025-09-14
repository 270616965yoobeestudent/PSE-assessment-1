from cgps.core.database import Database
from cgps.core.services.auth_service import AuthService


class AdminAuthService(AuthService):
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
            role="admin",
            table_name="admins",
            password_salt=password_salt,
            jwt_secret_key=jwt_secret_key,
        )



