from tempfile import mkstemp
from threading import Thread
from typing import Optional, Tuple

import sane
from PyPDF2 import PdfFileMerger

from scan_object import Scan, ScanList


class ScanManager:
    def __init__(self):
        self.sane_init = False
        self.scanners = []
        self.merger = PdfFileMerger()
        self.scans = ScanList()
        self.local_only = True

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

    def _scan(self, callback=None):
        temp_file, temp_filename = mkstemp(".pdf")
        scan = Scan()
        scan.size = self.size
        print(self.scanner.area)
        self.scans.append(scan)
        img = self.scanner.scan()
        scan.set_image(img)
        # pdf = pytesseract.image_to_pdf_or_hocr(img, extension="pdf", lang="deu")
        # with open(temp_filename, "wb") as f:
        #     f.write(pdf)
        # scan.set_filename(temp_filename)
        # Add PDF file to merger
        # self.merger.append(fileobj=open(temp_filename, "rb"))

        if callback:
            callback()

    def scan(self, callback=None):
        thread = Thread(target=self._scan, args=[callback])
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
