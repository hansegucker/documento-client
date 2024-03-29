import sys

from PyQt5.QtCore import Qt  # noqa
from PyQt5.QtWidgets import QApplication

from documento_client.scan_manager import ScanManager
from documento_client.ui_manager import MainWindowManager


def main():
    app = QApplication(sys.argv)
    manager = ScanManager()

    ui_manager = MainWindowManager(manager)
    ui_manager.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
