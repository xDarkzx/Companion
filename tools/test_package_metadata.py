"""Licence metadata must agree everywhere a package declares it."""
from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ElementTree

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / 'ros2_ws' / 'src'
LICENSE_ID = 'Apache-2.0'


def companion_packages() -> list[Path]:
    """Return every first-party package directory."""
    return sorted(p for p in SRC.glob('companion_*') if (p / 'package.xml').is_file())


def test_repository_ships_the_apache_licence_text():
    text = (REPO / 'LICENSE').read_text(encoding='utf-8')
    assert 'Apache License' in text
    assert 'Version 2.0, January 2004' in text


def test_every_package_xml_declares_the_repository_licence():
    for package in companion_packages():
        root = ElementTree.parse(package / 'package.xml').getroot()
        licences = [node.text for node in root.findall('license')]
        assert licences == [LICENSE_ID], f'{package.name}: {licences}'


def test_every_setup_py_declares_the_repository_licence():
    for package in companion_packages():
        setup = package / 'setup.py'
        if setup.is_file():
            assert f"license='{LICENSE_ID}'" in setup.read_text(encoding='utf-8'), package.name
