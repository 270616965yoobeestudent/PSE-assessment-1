from dependency_injector.wiring import Provide, inject
from dotenv import load_dotenv
from cgps.cli.app_cli import AppCli
from cgps.core.container import Container
from cgps.core.database import Database


@inject
def run(
    app: AppCli = Provide[Container.app_cli],
    database: Database = Provide[Container.database],
):
    app.run()
    
    database.close()


def main():
    load_dotenv()
    container = Container()
    container.wire(packages=["cgps"])
    run()
