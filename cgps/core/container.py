from dependency_injector import containers, providers

from cgps.cli.admin_cli import AdminCli
from cgps.cli.app_cli import AppCli
from cgps.cli.customer_cli import CustomerCli
from cgps.core.database import Database
from cgps.core.services.admin.admin_auth_service import AdminAuthService
from cgps.core.services.customer.customer_auth_service import CustomerAuthService
from cgps.core.services.customer.customer_info_service import CustomeInfoService
from cgps.ui.customer_info_form_ui import CustomerInfoFormUi
from cgps.ui.customer_register_ui import CustomerRegisterUi
from cgps.ui.info_ui import InfoUi
from cgps.ui.login_ui import LoginUi


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
    customer_info_service = providers.Factory(
        CustomeInfoService,
        database=database,
    )


    # UI Factory
    login_ui = providers.Factory(LoginUi)
    info_ui = providers.Factory(InfoUi)
    customer_register_ui = providers.Factory(CustomerRegisterUi)
    customer_info_form_ui = providers.Factory(CustomerInfoFormUi)

    # CLI Factory
    admin_cli = providers.Factory(
        AdminCli,
        auth_service=admin_auth_service,
        login_ui=login_ui,
    )
    customer_cli = providers.Factory(
        CustomerCli,
        auth_service=customer_auth_service,
        info_service=customer_info_service,
        login_ui=login_ui,
        register_ui=customer_register_ui,
        info_ui=info_ui,
        info_form_ui=customer_info_form_ui
    )
    app_cli = providers.Factory(
        AppCli,
        admin=admin_cli,
        customer=customer_cli,
    )
