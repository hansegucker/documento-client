if [ ! -f "flatpak-pip-generator" ]; then
    wget https://raw.githubusercontent.com/flatpak/flatpak-builder-tools/master/pip/flatpak-pip-generator
fi

poetry export --without-hashes > requirements.txt
python3 flatpak-pip-generator --requirements-file=requirements.txt