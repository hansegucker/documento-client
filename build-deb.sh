#!/bin/bash
poetry export --without-hashes > requirements.txt
sed -i '/^pyqt5.*$/d' requirements.txt
sed -i '/^python-sane.*$/d' requirements.txt
sed -i '/^pillow.*$/d' requirements.txt
dpkg-buildpackage -us -uc -b
