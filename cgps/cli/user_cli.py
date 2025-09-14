from cgps.core.guards.guest_guard import guest
from cgps.core.guards.login_guard import logged_in
from cgps.core.services.auth_service import AuthService
from cgps.ui.login_ui import LoginUi


class UserCli:
    def __init__(
        self,
        auth_service: AuthService,
        login_ui: LoginUi,
    ):
        self._auth_service = auth_service
        self._login_ui = login_ui

    @guest()
    def _login(self):
        result = self._login_ui.run()
        if result is None:
            return
        username = result["username"]
        password = result["password"]
        if self._auth_service.login(username, password):
            print("Login successful")
            print(f"You are now logged in as {username}")
        else:
            print("Login failed")

    @logged_in()
    def _logout(self):
        self._auth_service.logout()
        print("Logout successful")
