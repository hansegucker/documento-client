import sys

from PySide2.QtCore import QFile, QIODevice
from PySide2.QtUiTools import QUiLoader

ui_file_name = "progress.ui"
ui_file = QFile(ui_file_name)
if not ui_file.open(QIODevice.ReadOnly):
    print("Cannot open {}: {}".format(ui_file_name, ui_file.errorString()))
    sys.exit(-1)
loader = QUiLoader()
progress_dialog = loader.load(ui_file)
