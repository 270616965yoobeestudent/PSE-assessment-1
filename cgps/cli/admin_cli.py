from argparse import _SubParsersAction, ArgumentParser

import questionary
from cgps.cli.guards.login_guard import logged_in
from cgps.cli.user_cli import UserCli
from cgps.core.services.admin_auth_service import AdminAuthService
from cgps.core.services.car_service import CarService
from cgps.core.services.gps_service import GpsService
from cgps.core.services.order_service import OrderService
from cgps.ui.login_ui import LoginUi
from cgps.ui.order_list_ui import OrderListUi


class AdminCli(UserCli):
    def __init__(
        self,
        auth_service: AdminAuthService,
        login_ui: LoginUi,
        order_list_ui: OrderListUi,
        order_service: OrderService,
        car_service: CarService,
        gps_service: GpsService,
    ):
        super().__init__(auth_service, login_ui)
        self._order_service = order_service
        self._car_service = car_service
        self._gps_service = gps_service
        self._order_list_ui = order_list_ui

    def run(self, role: _SubParsersAction):
        admin: ArgumentParser = role.add_parser("admin", help="admin commands")
        admin.set_defaults(func=lambda _: admin.print_help())

        cmd = admin.add_subparsers(dest="cmd", title="Usage", metavar="admin <command>")

        login = cmd.add_parser("login", help="login as admin")
        login.set_defaults(func=lambda _: self._login())

        logout = cmd.add_parser("logout", help="logout from system")
        logout.set_defaults(func=lambda _: self._logout())

        gps = cmd.add_parser("gps", help="view all and update gps devices")
        gps.set_defaults(func=lambda _: self._gps_list())
        gps_cmd = gps.add_subparsers(dest="cmd", title="Usage", metavar="gps <command>")
        gps_register = gps_cmd.add_parser("register", help="register a new gps device")
        gps_register.set_defaults(func=lambda _: self._gps_register())

        car = cmd.add_parser("car", help="view all and update cars")
        car.set_defaults(func=lambda _: self._car_list())
        car_cmd = car.add_subparsers(dest="cmd", title="Usage", metavar="car <command>")
        car_register = car_cmd.add_parser("register", help="register a new car")
        car_register.set_defaults(func=lambda _: self._car_register())
        car_update = car_cmd.add_parser(
            "update", help="update general information of a car"
        )
        car_update.set_defaults(func=lambda _: self._car_update())
        car_return = car_cmd.add_parser(
            "return", help="make a car available for renting"
        )
        car_return.set_defaults(func=lambda _: self._car_return())
        car_report = car_cmd.add_parser(
            "report", help="view cars tracking report in realtime"
        )
        car_report.set_defaults(func=lambda _: self._car_report())

        order = cmd.add_parser("order", help="view all and update rent orders")
        order.set_defaults(func=lambda _: self._order_list())

    @logged_in()
    def _gps_list(self, user_id: int):
        data = self._gps_service.list()
        pass

    @logged_in()
    def _gps_register(self, user_id: int):
        pass

    @logged_in()
    def _car_list(self, user_id: int):
        pass

    @logged_in()
    def _car_register(self, user_id: int):
        pass

    @logged_in()
    def _car_update(self, user_id: int):
        pass

    @logged_in()
    def _car_return(self, user_id: int):
        pass

    @logged_in()
    def _car_report(self, user_id: int):
        pass

    @logged_in()
    def _order_list(self, user_id: int):
        invoices = self._order_service.list()
        data = self._order_list_ui.with_data(invoices, can_update=True).run()
        if data is None:
            return
        confirm = questionary.path("Are you sure to delete this order? (y/N)").ask()
        if confirm != 'y':
            return
        if not self._order_service.soft_delete(data.order.id):
            print("Delete order failed")
            return
        print("Delete order successful")



