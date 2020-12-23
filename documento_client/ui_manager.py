import sys

from PySide2.QtCore import QFile, QIODevice, Qt
from PySide2.QtUiTools import QUiLoader

from delegate import ImageableStyledItemDelegate
from scan_manager import ScanManager


class MainWindowManager:
    def __init__(self, manager: ScanManager):
        self.manager = manager

        # Load UI file from QtDesigner
        ui_file_name = "main.ui"
        ui_file = QFile(ui_file_name)
        if not ui_file.open(QIODevice.ReadOnly):
            print("Cannot open {}: {}".format(ui_file_name, ui_file.errorString()))
            sys.exit(-1)
        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()
        if not self.window:
            print(loader.errorString())
            sys.exit(-1)

        # Connect listview for scans with model and delegate
        self.window.scan_list.setModel(self.manager.scans)
        self.window.scan_list.setItemDelegate(
            ImageableStyledItemDelegate(parent=manager.scans)
        )

        # Connect other events
        self.window.scanner_select.currentIndexChanged.connect(self.on_scanner_selected)
        self.window.scan_button.clicked.connect(self.start_scan)
        self.manager.scan_status_updated.connect(self.on_scan_status_updated)
        self.window.clear_all_button.clicked.connect(self.manager.clear_all)

    def show(self):
        self.window.show()

        # Get all scanners
        self.scanner_progress = self.show_progress("Scanners are loading …")
        self.manager.get_scanners(self.on_scanners_loaded)

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
        self.window.status_bar.showMessage(
            f"OCR of page {index + 1} has been finished.", 2000
        )

    def start_scan(self):
        # progress = show_progress("Scan page …")
        page_number = self.manager.next_page_number
        self.window.scan_button.setEnabled(False)
        self.window.save_button.setEnabled(False)
        self.window.clear_all_button.setEnabled(False)
        self.window.status_bar.showMessage(
            f"Scan of page {page_number} is in progress …"
        )

        # progress.close()
        self.manager.scan(self.on_scan_finished, self.on_ocr_finished)
