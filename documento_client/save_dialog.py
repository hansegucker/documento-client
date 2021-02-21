import sys

from api_manager import AuthException
from PySide2.QtCore import QFile, QIODevice, QObject, Signal
from PySide2.QtUiTools import QUiLoader
from requests import RequestException


class SaveDialog(QObject):
    save_succeeded = Signal()
    error_network = Signal()
    error_auth = Signal()

    def __init__(self, api, manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = api
        self.manager = manager

        ui_file_name = "save.ui"
        ui_file = QFile(ui_file_name)

        if not ui_file.open(QIODevice.ReadOnly):
            print("Cannot open {}: {}".format(ui_file_name, ui_file.errorString()))
            sys.exit(-1)

        loader = QUiLoader()
        self.dialog = loader.load(ui_file)
        self.dialog.save_button.clicked.connect(self.save_document)

        self.dialog.pages_count.setText(str(self.manager.scanned_count))

        # Load categories
        self.categories = []
        try:
            self.categories = self.api.get_categories()
        except (RequestException, KeyError):
            self.error_network.emit()
        except AuthException:
            self.error_auth.emit()

        self.dialog.category.addItem("---")
        for category in self.categories:
            self.dialog.category.addItem(category["name"])

    def show(self):
        self.dialog.exec_()

    def save_document(self):
        category_idx = self.dialog.category.currentIndex()
        category = self.categories[category_idx - 1] if category_idx != 0 else None
        title = self.dialog.title.text()
        print_label = self.dialog.print_label.checkState()
        print_info = self.dialog.print_info.checkState()

        if not title:
            return

        self.dialog.save_button.setEnabled(False)

        path = self.manager.save()

        res = None
        try:
            res = self.api.upload_document(path, title, category["id"] if category else None)
            print(res)
            if res and print_info:
                res1 = self.api.print_report(res["id"], "info_page")
            if res and print_label:
                res2 = self.api.print_report(res["id"], "barcode_label")
        except (RequestException, KeyError):
            self.error_network.emit()
        except AuthException:
            self.error_auth.emit()

        if not res:
            self.dialog.save_button.setEnabled(True)
            return
        self.save_succeeded.emit()
