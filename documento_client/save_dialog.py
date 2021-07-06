import os

from PyQt5 import uic
from PyQt5.QtCore import QObject, pyqtSignal
from requests import RequestException

from documento_client.api_manager import AuthException
from documento_client.constants import BASE_DIR


class SaveDialog(QObject):
    save_succeeded = pyqtSignal()
    error_network = pyqtSignal()
    error_auth = pyqtSignal()

    def __init__(self, api, manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = api
        self.manager = manager

        ui_file_name = os.path.join(BASE_DIR, "save.ui")
        self.dialog = uic.loadUi(ui_file_name)

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

        categories = {category["id"]: category for category in self.categories}

        self.dialog.category.addItem("---")

        for category in self.categories:
            current_category = category
            cat_list = [current_category]

            while current_category["parent"]:
                cat_list.insert(0, categories[current_category["parent"]])
                current_category = categories[current_category["parent"]]

            cat_name = " / ".join([cat["name"] for cat in cat_list])
            self.dialog.category.addItem(cat_name)

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
