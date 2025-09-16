from importlib.resources import files
from cgps.cli.admin_cli import AdminCli
from cgps.cli.app_cli import AppCli
from cgps.cli.customer_cli import CustomerCli
from cgps.cli.database_cli import DatabaseCli
from cgps.core.database import Database
from cgps.core.services.admin_auth_service import AdminAuthService
from cgps.core.services.customer_auth_service import CustomerAuthService
from cgps.core.services.car_service import CarService
from cgps.core.services.customer_service import CustomerService
from cgps.core.services.gps_service import GpsService
from cgps.core.services.order_service import OrderService
from cgps.core.services.tracking_service import TrackingService
from cgps.ui.car_list_ui import CarListUi
from cgps.ui.customer_search_ui import CustomerSearchUi
from cgps.ui.gps_list_ui import GpsListUi
from cgps.ui.gps_register_ui import GpsRegisterUi
from cgps.ui.info_form_ui import InfoFormUi
from cgps.ui.register_ui import RegisterUi
from cgps.ui.login_ui import LoginUi
from cgps.ui.order_list_ui import OrderListUi
from cgps.ui.rent_ui import RentUi
from cgps.ui.tracking_report_ui import TrackingReportUi
from dependency_injector.providers import Factory, Configuration, ThreadSafeSingleton
from dependency_injector.containers import DeclarativeContainer


class Container(DeclarativeContainer):
    config = Configuration()

    database = ThreadSafeSingleton(
        Database,
        db_path=config.database.path,
    )

    # Service Factory
    admin_auth_service = Factory(
        AdminAuthService,
        database=database,
        service_name=config.app.keychain_service,
        password_salt=config.admin.password_salt,
        jwt_secret_key=config.admin.jwt_secret_key,
    )
    customer_auth_service = Factory(
        CustomerAuthService,
        database=database,
        service_name=config.app.keychain_service,
        password_salt=config.customer.password_salt,
        jwt_secret_key=config.customer.jwt_secret_key,
    )
    customer_service = Factory(
        CustomerService,
        database=database,
    )
    order_service = Factory(
        OrderService,
        database=database,
    )
    car_service = Factory(
        CarService,
        database=database,
    )
    gps_service = Factory(
        GpsService,
        database=database,
    )
    tracking_service = Factory(
        TrackingService,
        database=database,
    )

    # UI Factory
    login_ui = Factory(LoginUi)
    register_ui = Factory(RegisterUi)
    info_form_ui = Factory(InfoFormUi)
    order_list_ui = Factory(OrderListUi)
    rent_ui = Factory(RentUi, car_service=car_service)
    gps_list_ui = Factory(GpsListUi)
    gps_register_ui = Factory(GpsRegisterUi)
    tracking_report_ui = Factory(TrackingReportUi, tracking_service=tracking_service)
    customer_search_ui = Factory(CustomerSearchUi, customer_service=customer_service)
    car_list_ui = Factory(
        CarListUi,
        gps_service=gps_service,
    )

    # CLI Factory
    admin_cli = Factory(
        AdminCli,
        auth_service=admin_auth_service,
        login_ui=login_ui,
        order_list_ui=order_list_ui,
        gps_list_ui=gps_list_ui,
        gps_register_ui=gps_register_ui,
        customer_search_ui=customer_search_ui,
        car_list_ui=car_list_ui,
        order_service=order_service,
        car_service=car_service,
        gps_service=gps_service,
        tracking_service=tracking_service,
        tracking_report_ui=tracking_report_ui,
    )
    customer_cli = Factory(
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
    database_cli = Factory(
        DatabaseCli,
        database=database,
    )
    app_cli = Factory(
        AppCli,
        admin=admin_cli,
        customer=customer_cli,
        database=database_cli
    )
