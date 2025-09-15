import argparse
from cgps.cli.admin_cli import AdminCli
from cgps.cli.customer_cli import CustomerCli
from cgps.cli.help_message import HelpMessage


class AppCli:
    def __init__(self, admin: AdminCli, customer: CustomerCli):
        self.admin = admin
        self.customer = customer

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
                    "cgps <command>",
                    "\n"
                    "options",
                    "  -h, --help                         show this help message and exit",
                    "\n"
                    "Usage:",
                    "    cgps admin <command>             all admin commands require admin authentication",
                    "    cgps admin login                 login as admin",
                    "    cgps admin logout                logout from system",
                    "    cgps admin gps list              list all gps devices",
                    "    cgps admin gps register          register a new gps device",
                    "    cgps admin car list              list all cars",
                    "    cgps admin car register          register a new car",
                    "    cgps admin car update            update general information of a car",
                    "    cgps admin car return            make a car available for renting",
                    "    cgps admin car report            view cars tracking report in realtime",
                    "    cgps admin order list            view all rent orders",
                    "\n"
                    "    cgps customer <command>          Most customer commands require customer authentication",
                    "    cgps customer register           register a new customer. [no authentication required]",
                    "    cgps customer login              login as customer",
                    "    cgps customer logout             logout from system",
                    "    cgps customer info view          view customer information",
                    "    cgps customer info update        update general information",
                    "    cgps customer car rent           rent a car",
                    "    cgps customer order list         view all rent orders",
                ]
            ),
        )
        parser.set_defaults(func=lambda _: parser.print_help())

        role = parser.add_subparsers(dest="role", title="Usage", metavar="cgps <command>")
        self.admin.run(role)
        self.customer.run(role)

        args = parser.parse_args()
        args.func(args)
