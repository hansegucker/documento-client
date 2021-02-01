import sys

from PySide2.QtCore import QFile, QIODevice, QObject, Signal
from PySide2.QtUiTools import QUiLoader
from requests import RequestException

from api_manager import AuthException


class LoginDialog(QObject):
    login_succeeded = Signal()
    error_network = Signal()
    error_auth = Signal()

    def __init__(self, api, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = api

        ui_file_name = "login.ui"
        ui_file = QFile(ui_file_name)

        if not ui_file.open(QIODevice.ReadOnly):
            print("Cannot open {}: {}".format(ui_file_name, ui_file.errorString()))
            sys.exit(-1)

        loader = QUiLoader()
        self.dialog = loader.load(ui_file)
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
