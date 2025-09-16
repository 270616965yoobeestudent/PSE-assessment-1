import os
from importlib.resources import files

import yaml

from cgps.cli.app_cli import AppCli
from cgps.container import Container
from cgps.core.database import Database
from dependency_injector.wiring import Provide, inject


@inject
def run(
    app: AppCli = Provide[Container.app_cli],
    database: Database = Provide[Container.database],
):
    app.run()
    database.close()


def main():
    container = Container()
    config = (files("cgps") / "config.yml").read_text()
    container.config.from_dict(yaml.safe_load(config))
    container.wire(packages=["cgps"])
    run()
