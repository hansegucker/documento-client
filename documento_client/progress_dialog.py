import os

from PyQt5 import uic

from documento_client.constants import BASE_DIR

ui_file_name = os.path.join(BASE_DIR, "progress.ui")
progress_dialog = uic.loadUi(ui_file_name)
