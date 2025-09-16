import argparse
from cgps.cli.admin_cli import AdminCli
from cgps.cli.customer_cli import CustomerCli
from cgps.cli.database_cli import DatabaseCli
from cgps.cli.help_message import HelpMessage


class AppCli:
    def __init__(self, admin: AdminCli, customer: CustomerCli, database: DatabaseCli):
        self._admin = admin
        self._customer = customer
        self._database = database

    def run(self):
        parser = argparse.ArgumentParser(
            prog="cgps",
            description="Car Rental Management CLI with GPS tracking",
            add_help=False,
        )
        parser.add_argument(
            "-h",
            "--help",
            action=HelpMessage,
            message=lambda _: "\n".join(
                [
                    "Car Rental Management CLI with GPS tracking",
                    "\n" "cgps <command>",
                    "\n" "options",
                    "  -h, --help                         show this help message and exit",
                    "\n" "Usage:",
                    "    cgps customer <command>          Most customer commands require customer authentication",
                    "    cgps customer register           register a new customer. [no authentication required]",
                    "    cgps customer login              login as customer",
                    "    cgps customer logout             logout from system",
                    "    cgps customer info               view and update customer information",
                    "    cgps customer rent               rent a car",
                    "    cgps customer order              view all rent orders",
                    "\n"
                    "    cgps admin <command>             all admin commands require admin authentication",
                    "    cgps admin login                 login as admin",
                    "    cgps admin logout                logout from system",
                    "    cgps admin customer              view all and update customers",
                    "    cgps admin gps                   view all and update gps devices",
                    "    cgps admin gps register          register a new gps device",
                    "    cgps admin car                   view all and update cars",
                    "    cgps admin car register          register a new car",
                    "    cgps admin car report            view cars tracking report in realtime",
                    "    cgps admin order                 view all and update rent orders",
                    "    cgps admin order search          search customer orders",
                    "\n"
                    "    cgps db init                     initialize database"
                ]
            ),
        )
        parser.set_defaults(func=lambda _: parser.print_help())

        role = parser.add_subparsers(
            dest="role", title="Usage", metavar="cgps <command>"
        )
        self._admin.run(role)
        self._customer.run(role)
        self._database.run(role)

        args = parser.parse_args()
        args.func(args)
