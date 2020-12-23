from tempfile import mkstemp
from threading import Thread
from typing import Optional, Tuple

import sane
from PyPDF2 import PdfFileMerger
from PySide2.QtCore import QObject, Signal

from scan_object import Scan, ScanList


class ScanManager(QObject):
    scan_status_updated = Signal()

    def __init__(self):
        super().__init__()
        self.sane_init = False
        self.scanners = []
        self.merger = PdfFileMerger()
        self.scans = ScanList()
        self.local_only = True
        self.scans_in_progress = False
        self.ready_to_save = False

    def update_scan_status(self):
        scans_in_progress = False
        for scan in self.scans.list:
            if not scan.get_filename():
                scans_in_progress = True
        self.scans_in_progress = scans_in_progress
        if not self.scans_in_progress and len(self.scans.list) > 0:
            self.ready_to_save = True
        self.scan_status_updated.emit()

    @property
    def scanned_count(self):
        return self.scans.rowCount(True)

    @property
    def next_page_number(self):
        return self.scanned_count + 1

    @property
    def size(self) -> Optional[Tuple[int, int]]:
        return (
            (self.scanner.area[1][1], self.scanner.area[1][0]) if self.scanner else None
        )

    def _scan(self, callback=None, callback_ocr=None):
        scan = Scan()
        scan.size = self.size
        self.scans.append(scan)
        img = self.scanner.scan()
        scan.set_image(img)

        if callback:
            callback()

        index = self.scanned_count - 1

        def on_ocr_finished():
            callback_ocr(index)
            self.merger.append(fileobj=open(scan.filename, "rb"))
            self.update_scan_status()

        scan.do_ocr(on_ocr_finished)

    def scan(self, callback=None, callback_ocr=None):
        thread = Thread(target=self._scan, args=[callback, callback_ocr])
        thread.start()
        return thread

    def scanners_loaded(self):
        pass

    def init_sane(self):
        if not self.sane_init:
            sane.init()
            self.sane_init = True

    def _get_scanners(self, callback=None):
        self.init_sane()
        self.scanners = sane.get_devices(self.local_only)
        self.scanners_loaded()
        if callback:
            callback()

    def get_scanners(self, callback=None):
        load_scanner_thread = Thread(target=self._get_scanners, args=[callback])
        load_scanner_thread.start()
        return load_scanner_thread

    def open_scanner(self, index):
        print("Open scanner", index)
        self.scanner = sane.open(self.scanners[index][0])
        self.scanner.depth = 16
        self.scanner.mode = "color"
        self.scanner.resolution = 300
        return self.scanner
