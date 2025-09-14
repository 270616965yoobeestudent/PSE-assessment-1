from cgps.core.database import Database


class CustomerCarService:
    def __init__(self, database: Database):
        self._database = database