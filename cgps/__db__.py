import argparse
from dependency_injector.wiring import Provide, inject
from pathlib import Path
from cgps.container import Container
from cgps.core.database import Database


@inject
def run(database: Database = Provide[Container.database]):
    parser = argparse.ArgumentParser(
        prog="cgps-db",
        description="Car Rental Management Database CLI",
    )
    parser.set_defaults(func=lambda _: parser.print_help())
    cmd = parser.add_subparsers(
        dest="command", title="Usage", metavar="cgps-db <command>"
    )
    migration_run = cmd.add_parser("run", help="run database migration")
    migration_run.set_defaults(
        func=lambda _: (
            database.migrate_from_file(Path(__file__).with_name("db.sql")),
            database.migrate_from_file(Path(__file__).with_name("seed.sql")),
        )
    )

    args = parser.parse_args()
    args.func(args)


def main():
    container = Container()
    container.wire(packages=["cgps"])
    run()
