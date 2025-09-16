from argparse import _SubParsersAction, ArgumentParser
from typing import Any, Mapping
from cgps.cli.guards.guest_guard import guest
from cgps.cli.guards.login_guard import logged_in
from cgps.cli.user_cli import UserCli
from cgps.core.models.invoice import Invoice
from cgps.core.services.customer_auth_service import CustomerAuthService
from cgps.core.services.car_service import CarService
from cgps.core.services.customer_service import CustomerService
from cgps.core.services.order_service import OrderService
from cgps.ui.info_form_ui import InfoFormUi
from cgps.ui.register_ui import RegisterUi
from cgps.ui.login_ui import LoginUi
from cgps.ui.order_list_ui import OrderListUi
from cgps.ui.rent_ui import RentUi


class CustomerCli(UserCli):
    def __init__(
        self,
        auth_service: CustomerAuthService,
        customer_service: CustomerService,
        order_service: OrderService,
        car_service: CarService,
        login_ui: LoginUi,
        register_ui: RegisterUi,
        info_form_ui: InfoFormUi,
        order_list_ui: OrderListUi,
        rent_ui: RentUi,
    ):
        super().__init__(auth_service, login_ui)
        self._register_ui = register_ui
        self._info_form_ui = info_form_ui
        self._order_list_ui = order_list_ui
        self._rent_ui = rent_ui
        self._customer_service = customer_service
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

        info = cmd.add_parser("info", help="view customer information")
        info.set_defaults(func=lambda _: self._info_update())

        car_rent = cmd.add_parser("rent", help="rent a car")
        car_rent.set_defaults(func=lambda _: self._rent_car())

        order = cmd.add_parser("order", help="view all rent orders")
        order.set_defaults(func=lambda _: self._list_orders())

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
    def _info_update(self, user_id: int):
        data = self._get_info(user_id)
        result = self._info_form_ui.with_data(data, can_update=True).run()
        if result is None:
            return
        if not self._customer_service.update_info(result):
            print("Update info failed")
            return
        print("Update info successful")

    def _get_info(self, user_id: int) -> Mapping[str, Any]:
        info = self._customer_service.get_info(user_id)
        passport = info.passport
        license = info.driver_license
        info_data = info.to_db()
        info_data.pop("password")
        info_data["passport"] = passport.to_db()
        info_data["driver_license"] = license.to_db()
        return info_data

    @logged_in()
    def _list_orders(self, user_id: int):
        invoices = self._order_service.list(user_id)
        self._order_list_ui.with_data(invoices, flow="customer").run()

    @logged_in()
    def _rent_car(self, user_id: int):
        result: Invoice = self._rent_ui.with_data(user_id=user_id).run()
        if result is None:
            return
        if not self._order_service.rent_and_pay(user_id, result):
            print("Rent failed")
            return
        print("Rent successful")
