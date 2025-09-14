from dataclasses import dataclass

from cgps.core.models.db_model import DBModel


@dataclass
class Admin(DBModel):
    id: int
    username: str
    password: str