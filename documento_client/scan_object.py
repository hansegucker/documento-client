from PIL.ImageQt import ImageQt
from PySide2.QtCore import QAbstractListModel, QObject, Qt, Signal
from PySide2.QtGui import QImage

from constants import THUMBNAIL_WIDTH


class ScanList(QAbstractListModel):
    def __init__(self, *args):
        super().__init__(*args)
        self.list = []

    def __iter__(self):
        return iter(self.list)

    def rowCount(self, parent=None, *args, **kwargs):
        if parent:
            return len(self.list)

    def data(self, index, role=None):
        return self.list[index.row()]

    def data_by_int_index(self, index):
        return self.list[index]

    def append(self, item):
        item.data_changed.connect(self.data_changed)
        self.list.append(item)
        new_index = self.createIndex(len(self.list), 0, item)
        self.dataChanged.emit(new_index, new_index, [Qt.EditRole])

    def pop(self, index):
        self.list.pop(index)
        i = min(index, len(self.list) - 1)
        new_index = self.createIndex(i, 0, self.list[i])
        self.dataChanged.emit(new_index, new_index, [Qt.EditRole])

    def data_changed(self, item):
        model_index = self.createIndex(self.list.index(item), 0, item)
        self.setData(model_index, item)

    def setData(self, model_index, data, role=Qt.EditRole):
        super().setData(model_index, data, role=role)
        self.dataChanged.emit(model_index, model_index, [role])

    def reset_whole_list(self):
        for item in self.list:
            item.reset()

    def clear(self):
        self.list = []

    def is_empty(self):
        return len(self.list) <= 0


class Scan(QObject):
    data_changed = Signal(QObject)

    def __init__(self, *args):
        super().__init__(*args)
        self.img = None
        self.thumb = None
        self.filename = None
        self.height = 0
        self.width = 0

    @property
    def thumb_height(self):
        return self.height / (self.width / THUMBNAIL_WIDTH)

    @property
    def size(self):
        return (self.width, self.height)

    @size.setter
    def size(self, size):
        self.height, self.width = size

    def set_image(self, image):
        self.img = ImageQt(image)
        self.create_thumb()
        self.data_changed.emit(self)

    def set_filename(self, filename):
        self.filename = filename
        self.data_changed.emit(self)

    def set_image_from_filename(self, filename):
        self.filename = filename
        self.img = QImage(filename)
        self.create_thumb()
        self.data_changed.emit(self)

    def create_thumb(self):
        self.thumb = self.img.scaledToWidth(
            THUMBNAIL_WIDTH, mode=Qt.SmoothTransformation
        )

    def get_thumb(self):
        return self.thumb

    def get_image(self):
        return self.img
