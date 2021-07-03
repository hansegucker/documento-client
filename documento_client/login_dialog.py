import os

from PyQt5 import uic
from PyQt5.QtCore import QObject, pyqtSignal
from requests import RequestException

from documento_client.api_manager import AuthException
from documento_client.constants import BASE_DIR


class LoginDialog(QObject):
    login_succeeded = pyqtSignal()
    error_network = pyqtSignal()
    error_auth = pyqtSignal()

    def __init__(self, api, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = api

        ui_file_name = os.path.join(BASE_DIR, "login.ui")
        self.dialog = uic.loadUi(ui_file_name)

        self.dialog.login_button.clicked.connect(self.check_login)

    def show(self):
        self.dialog.exec_()

    def check_login(self):
        self.dialog.login_button.setEnabled(False)
        username = self.dialog.username_edit.text()
        password = self.dialog.password_edit.text()

        res = None
        try:
            res = self.api.login(username, password)
        except (RequestException, KeyError):
            self.error_network.emit()
        except AuthException:
            self.error_auth.emit()

        if not res:
            self.dialog.login_button.setEnabled(True)
            return
        self.login_succeeded.emit()
