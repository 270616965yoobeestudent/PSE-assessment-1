from dependency_injector import containers, providers

from cgps.cli.admin_cli import AdminCli
from cgps.cli.app_cli import AppCli
from cgps.cli.customer_cli import CustomerCli
from cgps.core.database import Database
from cgps.core.services.admin_auth_service import AdminAuthService
from cgps.core.services.customer_auth_service import CustomerAuthService
from cgps.core.services.car_service import CarService
from cgps.core.services.customer_service import CustomerService
from cgps.core.services.gps_service import GpsService
from cgps.core.services.order_service import OrderService
from cgps.ui.gps_list_ui import GpsListUi
from cgps.ui.gps_register_ui import GpsRegisterUi
from cgps.ui.info_form_ui import InfoFormUi
from cgps.ui.register_ui import RegisterUi
from cgps.ui.login_ui import LoginUi
from cgps.ui.order_list_ui import OrderListUi
from cgps.ui.rent_ui import RentUi


class Container(containers.DeclarativeContainer):
    config = providers.Configuration(yaml_files=["config.yml"])

    database = providers.ThreadSafeSingleton(
        Database,
        db_path=config.database.path,
    )

    # Service Factory
    admin_auth_service = providers.Factory(
        AdminAuthService,
        database=database,
        service_name=config.app.keychain_service,
        password_salt=config.admin.password_salt,
        jwt_secret_key=config.admin.jwt_secret_key,
    )
    customer_auth_service = providers.Factory(
        CustomerAuthService,
        database=database,
        service_name=config.app.keychain_service,
        password_salt=config.customer.password_salt,
        jwt_secret_key=config.customer.jwt_secret_key,
    )
    customer_service = providers.Factory(
        CustomerService,
        database=database,
    )
    order_service = providers.Factory(
        OrderService,
        database=database,
    )
    car_service = providers.Factory(
        CarService,
        database=database,
    )
    gps_service = providers.Factory(
        GpsService,
        database=database,
    )

    # UI Factory
    login_ui = providers.Factory(LoginUi)
    register_ui = providers.Factory(RegisterUi)
    info_form_ui = providers.Factory(InfoFormUi)
    order_list_ui = providers.Factory(OrderListUi)
    rent_ui = providers.Factory(RentUi, car_service=car_service)
    gps_list_ui = providers.Factory(GpsListUi)
    gps_register_ui = providers.Factory(GpsRegisterUi)

    # CLI Factory
    admin_cli = providers.Factory(
        AdminCli,
        auth_service=admin_auth_service,
        login_ui=login_ui,
        order_list_ui=order_list_ui,
        gps_list_ui=gps_list_ui,
        gps_register_ui=gps_register_ui,
        order_service=order_service,
        car_service=car_service,
        gps_service=gps_service,
    )
    customer_cli = providers.Factory(
        CustomerCli,
        auth_service=customer_auth_service,
        customer_service=customer_service,
        order_service=order_service,
        car_service=car_service,
        login_ui=login_ui,
        register_ui=register_ui,
        info_form_ui=info_form_ui,
        order_list_ui=order_list_ui,
        rent_ui=rent_ui,
    )
    app_cli = providers.Factory(
        AppCli,
        admin=admin_cli,
        customer=customer_cli,
    )
