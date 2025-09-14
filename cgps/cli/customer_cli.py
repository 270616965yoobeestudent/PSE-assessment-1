from argparse import _SubParsersAction, ArgumentParser
from typing import Any, Mapping
from cgps.cli.guards.guest_guard import guest
from cgps.cli.guards.login_guard import logged_in
from cgps.cli.user_cli import UserCli
from cgps.core.services.customer.customer_auth_service import CustomerAuthService
from cgps.core.services.customer.customer_car_service import CustomerCarService
from cgps.core.services.customer.customer_info_service import CustomerInfoService
from cgps.core.services.customer.customer_order_service import CustomerOrderService
from cgps.ui.customer_info_form_ui import CustomerInfoFormUi
from cgps.ui.customer_register_ui import CustomerRegisterUi
from cgps.ui.info_ui import InfoUi
from cgps.ui.login_ui import LoginUi


class CustomerCli(UserCli):
    def __init__(
        self,
        auth_service: CustomerAuthService,
        info_service: CustomerInfoService,
        order_service: CustomerOrderService,  # Assuming order_service is defined elsewhere
        car_service: CustomerCarService,    # Assuming car_service is defined elsewhere
        login_ui: LoginUi,
        register_ui: CustomerRegisterUi,
        info_form_ui: CustomerInfoFormUi,
        info_ui: InfoUi,
    ):
        super().__init__(auth_service, login_ui)
        self._register_ui = register_ui
        self._info_ui = info_ui
        self._info_form_ui = info_form_ui
        self._info_service = info_service
        self._order_service = order_service
        self._car_service = car_service

    def run(self, role: _SubParsersAction):
        customer: ArgumentParser = role.add_parser("customer", help="customer commands")
        customer.set_defaults(func=lambda _: customer.print_help())
        cmd = customer.add_subparsers(
            dest="cmd", title="Usage", metavar="customer <command>"
        )

        register = cmd.add_parser("register", help="register a new customer")
        register.set_defaults(func=lambda _: self._register())

        login = cmd.add_parser("login", help="login as customer")
        login.set_defaults(func=lambda _: self._login())

        logout = cmd.add_parser("logout", help="logout from system")
        logout.set_defaults(func=lambda _: self._logout())

        info = cmd.add_parser("info", help="view, update customer information")
        info.set_defaults(func=lambda _: info.print_help())
        info_cmd = info.add_subparsers(
            dest="cmd", title="Usage", metavar="info <command>"
        )
        info_view = info_cmd.add_parser("view", help="view customer information")
        info_view.set_defaults(func=lambda _: self._info_view())
        info_update = info_cmd.add_parser("update", help="update general information")
        info_update.set_defaults(func=lambda _: self._info_update())

        car = cmd.add_parser("car", help="rent, return a car")
        car.set_defaults(func=lambda _: car.print_help())
        car_cmd = car.add_subparsers(dest="cmd", title="Usage", metavar="car <command>")
        car_cmd.add_parser("rent", help="rent a car")
        car_cmd.add_parser("return", help="return a car")

        order = cmd.add_parser("order", help="list, update orders")
        order.set_defaults(func=lambda _: order.print_help())
        order_cmd = order.add_subparsers(
            dest="cmd", title="Usage", metavar="order <command>"
        )
        order_cmd.add_parser("list", help="view all rent orders")

    @guest()
    def _register(self):
        data = self._register_ui.run()
        if data is None:
            return
        if not self._auth_service.register(data):
            print("Register failed")
            return
        print("Register successful")

    @logged_in()
    def _info_view(self, user_id: int):
        data = self._get_info(user_id)
        self._info_ui.with_data(data).run()
    
    @logged_in()
    def _info_update(self, user_id: int):
        data = self._get_info(user_id)
        result = self._info_form_ui.with_data(data).run()
        if not self._info_service.update_info(result):
            print("Update info failed")
            return
        print("Update info successful")

    def _get_info(self, user_id: int) -> Mapping[str, Any]:
        info = self._info_service.get_info(user_id)
        passport = info.passport
        license = info.driver_license
        info_data = info.to_db()
        info_data.pop('password')
        info_data['passport'] = passport.to_db()
        info_data['driver_license'] = license.to_db()
        return info_data
