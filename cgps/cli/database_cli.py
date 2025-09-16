from argparse import _SubParsersAction, ArgumentParser
from importlib.resources import files
from pathlib import Path
from cgps.core.database import Database


class DatabaseCli:
    def __init__(self, database: Database):
        self._database = database

    def run(self, role: _SubParsersAction):
        db: ArgumentParser = role.add_parser("db", help="Database management")
        db.set_defaults(func=lambda _: db.print_help())

        cmd = db.add_subparsers(dest="cmd", title="Usage", metavar="db <command>")
        db_init = cmd.add_parser("init", help="initialize database")
        db_init.set_defaults(
            func=lambda _: (
                self._database.migrate_from_file(Path(files("cgps") / "db.sql")),
                self._database.migrate_from_file(Path(files("cgps") / "seed.sql")),
                print("Database initialized successfully"),
            )
        )
