from cgps.core.database import Database


class CarService:
    def __init__(self, database: Database):
        self._database = database