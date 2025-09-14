from argparse import _SubParsersAction, ArgumentParser
from cgps.cli.user_cli import UserCli
from cgps.core.services.admin.admin_auth_service import AdminAuthService
from cgps.ui.login_ui import LoginUi


class AdminCli(UserCli):
    def __init__(
        self,
        auth_service: AdminAuthService,
        login_ui: LoginUi,
    ):
        super().__init__(auth_service, login_ui)

    def run(self, role: _SubParsersAction):
        admin: ArgumentParser = role.add_parser("admin", help="admin commands")
        admin.set_defaults(func=lambda _: admin.print_help())

        cmd = admin.add_subparsers(dest="cmd", title="Usage", metavar="admin <command>")

        login = cmd.add_parser("login", help="login as admin")
        login.set_defaults(func=lambda _: self._login())

        logout = cmd.add_parser("logout", help="logout from system")
        logout.set_defaults(func=lambda _: self._logout())

        gps = cmd.add_parser("gps", help="list, regiser, remove gps devices")
        gps.set_defaults(func=lambda _: gps.print_help())
        gps_cmd = gps.add_subparsers(dest="cmd", title="Usage", metavar="gps <command>")
        gps_cmd.add_parser("list", help="list all gps devices")
        gps_cmd.add_parser("register", help="register a new gps device")
        gps_cmd.add_parser("remove", help="remove a gps device")

        car = cmd.add_parser("car", help="list, register, update, remove cars")
        car.set_defaults(func=lambda _: car.print_help())
        car_cmd = car.add_subparsers(dest="cmd", title="Usage", metavar="car <command>")
        car_cmd.add_parser("list", help="list all cars")
        car_cmd.add_parser("register", help="register a new car")
        car_cmd.add_parser("remove", help="remove a car")
        car_cmd.add_parser("report", help="view cars tracking report in realtime")

        order = cmd.add_parser("order", help="list, update orders")
        order.set_defaults(func=lambda _: order.print_help())
        order_cmd = order.add_subparsers(
            dest="cmd", title="Usage", metavar="order <command>"
        )
        order_cmd.add_parser("list", help="view all rent orders")
