import os
import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QMessageBox

from documento_client.api_manager import APIManager
from documento_client.constants import BASE_DIR
from documento_client.delegate import ImageableStyledItemDelegate
from documento_client.login_dialog import LoginDialog
from documento_client.save_dialog import SaveDialog
from documento_client.scan_manager import ScanManager


class MainWindowManager:
    def __init__(self, manager: ScanManager):
        self.login_dialog = None
        self.save_dialog = None
        self.dialog = None
        self.manager = manager

        # Load UI file from QtDesigner
        ui_file_name = os.path.join(BASE_DIR, "main.ui")
        self.window = uic.loadUi(ui_file_name)
        if not self.window:
            sys.exit(-1)

        # Connect listview for scans with model and delegate
        self.window.scan_list.setModel(self.manager.scans)
        self.window.scan_list.setItemDelegate(ImageableStyledItemDelegate(parent=manager.scans))

        # Add status bar labels
        self.status_label = QLabel("No connection")
        self.status_icon_label = QLabel("XX")
        self.status_icon_online = QPixmap(os.path.join(BASE_DIR, "online.svg"))
        self.status_icon_offline = QPixmap(os.path.join(BASE_DIR, "offline.svg"))
        self.status_icon_uploading = QPixmap(os.path.join(BASE_DIR, "uploading.svg"))

        self.status_icon_label.setPixmap(self.status_icon_online)

        self.window.status_bar.addWidget(self.status_icon_label)
        self.window.status_bar.addWidget(self.status_label)

        # Init API
        self.api = APIManager()

        # Connect other events
        self.window.scanner_select.currentIndexChanged.connect(self.on_scanner_selected)
        self.window.scan_button.clicked.connect(self.start_scan)
        self.manager.scan_status_updated.connect(self.on_scan_status_updated)
        self.window.clear_all_button.clicked.connect(self.manager.clear_all)
        self.window.save_button.clicked.connect(self.show_save_dialog)

    def set_status_online(self):
        self.status_icon_label.setPixmap(self.status_icon_online)
        self.status_label.setText(f"Logged in ({self.api.base_url})")

    def set_status_uploading(self):
        self.status_icon_label.setPixmap(self.status_icon_uploading)
        self.status_label.setText(f"Uploading to ({self.api.base_url})")

    def set_status_offline(self):
        self.status_icon_label.setPixmap(self.status_icon_offline)
        self.status_label.setText("Offline")

    def show(self):
        self.window.show()

        # Get all scanners
        self.manager.get_scanners(self.on_scanners_loaded)

        self.show_login_dialog()

        if not self.manager.scanners_loaded:
            self.scanner_progress = self.show_progress("Scanners are loading …")

    def show_login_dialog(self):
        if not self.login_dialog:
            self.login_dialog = LoginDialog(self.api)
            self.login_dialog.login_succeeded.connect(self.on_login_succeeded)
            self.login_dialog.error_network.connect(self.on_api_error_network)
            self.login_dialog.error_auth.connect(self.on_api_error_auth)
            self.dialog = self.login_dialog
            self.login_dialog.show()

    def on_login_succeeded(self):
        self.login_dialog.dialog.close()
        self.login_dialog = None
        self.dialog = None
        self.set_status_online()

    def show_save_dialog(self):
        if not self.save_dialog:
            self.save_dialog = SaveDialog(self.api, self.manager)
            self.save_dialog.save_succeeded.connect(self.on_save_succeeded)
            self.save_dialog.error_network.connect(self.on_api_error_network)
            self.save_dialog.error_auth.connect(self.on_api_error_auth)
            self.dialog = self.save_dialog
            self.set_status_uploading()
            self.save_dialog.show()

    def on_save_succeeded(self):
        self.save_dialog.dialog.close()
        self.save_dialog = None
        self.dialog = None
        self.set_status_online()
        self.manager.clear_all()

    def on_api_error_network(self):
        QMessageBox.critical(
            self.window if not self.dialog else self.dialog.dialog,
            "Network error",
            "There is a problem with the server or the network connection.",
        )
        self.set_status_offline()

    def on_api_error_auth(self):
        QMessageBox.critical(
            self.window if not self.dialog else self.dialog.dialog,
            "Login error",
            "There is a problem with your credentials.",
        )
        self.set_status_offline()
        self.show_login_dialog()

    def show_progress(self, label):
        from progress_dialog import progress_dialog

        progress_dialog.setWindowFlags(Qt.FramelessWindowHint)
        progress_dialog.progress_label.setText(label)
        progress_dialog.show()

        return progress_dialog

    def on_scan_status_updated(self):
        self.window.save_button.setEnabled(self.manager.ready_to_save)
        self.window.clear_all_button.setEnabled(self.manager.ready_to_save)

    def on_scanners_loaded(self):
        print("Scanners there")
        print(self.manager.scanners)
        self.window.scanner_select.clear()
        for scanner in self.manager.scanners:
            self.window.scanner_select.addItem(scanner[1] + " " + scanner[2])

        if hasattr(self, "scanner_progress"):
            self.scanner_progress.close()

    def on_scanner_selected(self, index):
        self.manager.open_scanner(index)
        self.window.scan_button.setEnabled(True)

    def on_scan_finished(self):
        self.window.scan_button.setEnabled(True)
        self.window.status_bar.showMessage(
            f"Scan of page {self.manager.scanned_count} has been finished.", 2000
        )

    def on_ocr_finished(self, index):
        self.window.status_bar.showMessage(f"OCR of page {index + 1} has been finished.", 2000)

    def start_scan(self):
        # progress = show_progress("Scan page …")
        page_number = self.manager.next_page_number
        self.window.scan_button.setEnabled(False)
        self.window.save_button.setEnabled(False)
        self.window.clear_all_button.setEnabled(False)
        self.window.status_bar.showMessage(f"Scan of page {page_number} is in progress …")

        # progress.close()
        self.manager.scan(self.on_scan_finished, self.on_ocr_finished)
