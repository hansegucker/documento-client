import os

from PySide2.QtCore import QRectF, QSize
from PySide2.QtGui import QImage, QPainter, QPainterPath, QPen, Qt
from PySide2.QtWidgets import QStyledItemDelegate

from documento_client.constants import BASE_DIR, THUMBNAIL_MARGIN, THUMBNAIL_WIDTH
from documento_client.scan_object import Scan

scan_image = QImage(os.path.join(BASE_DIR, "scanner.png"))
progress_image = QImage(os.path.join(BASE_DIR, "progress.png"))
check_image = QImage(os.path.join(BASE_DIR, "check.png"))


class ImageableStyledItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, *args):
        super().__init__(*args)
        self.setParent(parent)

    def paint(self, qp, style_option_view_item, model_index):
        mid = model_index.data()
        if type(mid) is Scan:
            qp.save()
            background_path = QPainterPath()
            background_path.addRect(
                QRectF(
                    style_option_view_item.rect.left() + THUMBNAIL_MARGIN,
                    style_option_view_item.rect.top() + THUMBNAIL_MARGIN,
                    THUMBNAIL_WIDTH,
                    mid.thumb_height,
                )
            )
            qp.setPen(QPen(Qt.lightGray, 0))
            qp.fillPath(background_path, Qt.lightGray)
            qp.drawPath(background_path)

            if mid.get_thumb():
                # Show scanned image
                qp.drawImage(
                    style_option_view_item.rect.left() + THUMBNAIL_MARGIN,
                    style_option_view_item.rect.top() + THUMBNAIL_MARGIN,
                    mid.get_thumb(),
                )
                qp.drawImage(
                    style_option_view_item.rect.left()
                    + THUMBNAIL_WIDTH
                    - THUMBNAIL_MARGIN
                    - check_image.width(),
                    style_option_view_item.rect.top()
                    + mid.thumb_height
                    - THUMBNAIL_MARGIN
                    - check_image.height(),
                    check_image if mid.get_filename() else progress_image,
                )
            else:
                # Show scanner icon
                left = ((THUMBNAIL_WIDTH + 2 * THUMBNAIL_MARGIN) - scan_image.width()) / 2
                top = ((mid.thumb_height + 2 * THUMBNAIL_MARGIN) - scan_image.height()) / 2
                qp.drawImage(
                    style_option_view_item.rect.left() + left,
                    style_option_view_item.rect.top() + top,
                    scan_image,
                )

            qp.setRenderHint(QPainter.Antialiasing)
            qp.setRenderHint(QPainter.HighQualityAntialiasing)
            qp.restore()
        else:
            super().paint(qp, style_option_view_item, model_index)

    def sizeHint(self, style_option_view_item, model_index):
        mid = model_index.data()
        if type(mid) is Scan:
            if mid.get_thumb():
                return QSize(
                    mid.get_thumb().width() + 2 * THUMBNAIL_MARGIN,
                    mid.get_thumb().height() + 2 * THUMBNAIL_MARGIN,
                )
            else:
                return QSize(
                    THUMBNAIL_WIDTH + 2 * THUMBNAIL_MARGIN, mid.thumb_height + 2 * THUMBNAIL_MARGIN,
                )
        else:
            return super().sizeHint(style_option_view_item, model_index)
