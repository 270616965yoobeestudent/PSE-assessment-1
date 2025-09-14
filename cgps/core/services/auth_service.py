import keyring
import jwt
import base64, hashlib
from cgps.core.database import Database


class AuthService:
    def __init__(
        self,
        database: Database,
        service_name: str,
        table_name: str,
        role: str,
        password_salt: str,
        jwt_secret_key: str,
    ):
        self.database = database
        self.service_name = service_name
        self.table_name = table_name
        self.role = role
        self.password_salt = password_salt
        self.jwt_secret_key = jwt_secret_key

    def verify_login(self) -> bool:
        access_token = keyring.get_password(self.service_name, self.role)
        if access_token is None:
            return False
        try:
            data = jwt.decode(
                access_token,
                self.jwt_secret_key,
                algorithms=["HS256"],
                options={"require": ["sub", "name", "role"]},
            )
            self.id = data["sub"]
            self.username = data["name"]
        except jwt.exceptions.InvalidSignatureError:
            return False
        return True

    def logout(self):
        keyring.delete_password(self.service_name, self.role)

    def login(self, username: str, password: str) -> bool:
        password = self._encrypt_password(password)
        data = self.database.fetchone(
            f"SELECT id, username FROM {self.table_name} WHERE username = ? AND password = ?",
            (username, password),
        )
        if data is None:
            return False
        access_token = jwt.encode(
            {"sub": str(data['id']), "name": data['username'], "role": self.role},
            self.jwt_secret_key,
            algorithm="HS256",
        )
        keyring.set_password(self.service_name, self.role, access_token)
        return True

    def _encrypt_password(self, password: str) -> str:
        return hashlib.sha256(
            (self.password_salt + password).encode("utf-8")
        ).hexdigest()
