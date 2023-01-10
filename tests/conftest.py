# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Fixtures for pytest."""

import os
import logging
import urllib.request

import pytest

from vimiv.imutils import metadata
# from vimiv.plugins import metadata_pyexiv2, metadata_piexif
from vimiv.plugins import metadata_piexif


CI = "CI" in os.environ

# fmt: off
PLATFORM_MARKERS = (
    ("ci", CI, "Only run on ci"),
    ("ci_skip", not CI, "Skipped on ci"),
)

METADATA_MARKERS = (
    ("metadata", metadata.has_metadata_support(), "Only run with metadata support"),
    ("nometadata", not metadata.has_metadata_support(), "Only run without metadata support"),
    ("piexif", metadata_piexif.piexif is not None, "Only run with piexif"),
    # ("pyexiv2", metadata_pyexiv2.pyexiv2 is not None, "Only run with pyexiv2"),
    ("pyexiv2", False, "Only run with pyexiv2"),
)
# fmt: on


def apply_platform_markers(item):
    """Apply markers that skip tests depending on the current platform."""
    apply_markers_helper(item, PLATFORM_MARKERS)


def apply_metadata_markers(item):
    """Apply markers that skip tests depending on specific metadata support."""
    if os.path.basename(item.fspath) in ("test_exif.py",):
        for marker_name in "metadata", "pyexiv2", "piexif":
            marker = getattr(pytest.mark, marker_name)
            item.add_marker(marker)
    apply_markers_helper(item, METADATA_MARKERS)


def apply_markers_helper(item, markers):
    """Helper function to apply an iterable of markers to a test item."""
    for marker_name, fulfilled, reason in markers:
        marker = item.get_closest_marker(marker_name)
        if marker is not None:
            skipif = pytest.mark.skipif(
                not fulfilled, *marker.args, reason=reason, **marker.kwargs
            )
            item.add_marker(skipif)


def pytest_collection_modifyitems(items):
    """Handle custom markers via pytest hook."""
    for item in items:
        apply_platform_markers(item)
        apply_metadata_markers(item)


@pytest.fixture
def cleanup_helper():
    """Fixture to keep vimiv registries clean.

    Returns a contextmanager that resets the state of a dictionary to the initial state
    before running tests.
    """

    def cleanup(init_dict):
        init_content = {key: dict(value) for key, value in init_dict.items()}
        yield
        new_content = {key: dict(value) for key, value in init_dict.items()}
        for key, valuedict in new_content.items():
            for elem in valuedict:
                if elem not in init_content[key]:
                    del init_dict[key][elem]

    return cleanup


class StubStream:
    """Dummy stream class that does nothing on write and friends."""

    def stub(self, *args, **kwargs):
        """Method that accepts anything and does nothing."""

    write = writelines = close = stub


class DevNullLogHandler(logging.StreamHandler):
    """Stub log handler that redirects everything to the black hole."""

    def __init__(self, *args, **kwargs):
        self.devnull = StubStream()
        super().__init__(self.devnull)


@pytest.fixture(autouse=True)
def mock_file_handler(monkeypatch):
    """Fixture to monkeypatch the logging file handler.

    It is not required in any testing here and we do not want to write the test log
    statements to file.
    """
    monkeypatch.setattr(logging, "FileHandler", DevNullLogHandler)


@pytest.fixture()
def datadir():
    """Fixture to retrieve the path to the data directory."""
    testdir = os.path.dirname(__file__)
    datadir = os.path.join(testdir, "data")
    if not os.path.isdir(datadir):
        os.makedirs(datadir, mode=0o700)
    return datadir


@pytest.fixture()
def gif(datadir):
    """Fixture to retrieve the path to a gif file.

    We retrieve the file from the web if it does not exist. This should only happen once
    per developing environment.
    """
    path = os.path.join(datadir, "vimiv.gif")
    if not os.path.exists(path):
        url = "https://i.postimg.cc/VkcPgcbR/vimiv.gif"
        _retrieve_file_from_web(url, path)
    return path


@pytest.fixture()
def svg(datadir):
    """Fixture to retrieve the path to a svg file.

    We retrieve the file from the web if it does not exist. This should only happen once
    per developing environment.
    """
    path = os.path.join(datadir, "vimiv.svg")
    if not os.path.exists(path):
        url = "https://raw.githubusercontent.com/karlch/vimiv-qt/master/icons/vimiv.svg"
        _retrieve_file_from_web(url, path)
    return path


def _retrieve_file_from_web(url: str, path: str) -> None:
    """Helper function to write url byte data to path."""
    print(f"Retrieving {path} from {url}")
    with urllib.request.urlopen(url) as f:
        data = f.read()
    with open(path, "wb") as f:
        f.write(data)
    print("... success")


@pytest.fixture()
def tmpdir():
    """Override tmpdir to raise a ValueError."""
    raise ValueError("Use the 'tmp_path' fixture instead of 'tmpdir'")


@pytest.fixture()
def reset_metadata_registration():
    """Fixture to ensure everything is reset to default after testing."""
    initial_content = metadata._registry.copy()
    yield
    metadata._registry = initial_content


@pytest.fixture()
def metadata_support(reset_metadata_registration):
    """Pytest fixture to ensure piexif and pyexiv2 based metadata plugins are registered."""
    from vimiv.plugins.metadata_piexif import MetadataPiexif
    from vimiv.plugins.metadata_pyexiv2 import MetadataPyexiv2

    metadata._registry = []
    metadata.register(MetadataPiexif)
    metadata.register(MetadataPyexiv2)


@pytest.fixture()
def piexif(reset_metadata_registration):
    """Pytest fixture to ensure only piexif based metadata plugin is registered."""
    from vimiv.plugins.metadata_piexif import MetadataPiexif

    metadata._registry = []
    metadata.register(MetadataPiexif)


@pytest.fixture()
def pyexiv2(reset_metadata_registration):
    """Pytest fixture to ensure only pyexiv2 based metadata plugin is registered."""
    from vimiv.plugins.metadata_pyexiv2 import MetadataPyexiv2

    metadata._registry = []
    metadata.register(MetadataPyexiv2)


@pytest.fixture()
def no_metadata_support(reset_metadata_registration):
    """Pytest fixture to ensure no metadata plugin is registered."""
    metadata._registry = {}


@pytest.fixture()
def add_exif_information():
    """Fixture to retrieve a helper function that adds exif content to an image."""

    def add_exif_information_impl(path: str, content):
        import piexif

        exif_dict = piexif.load(path)
        for ifd, ifd_dict in content.items():
            for key, value in ifd_dict.items():
                exif_dict[ifd][key] = value
        piexif.insert(piexif.dump(exif_dict), path)

    return add_exif_information_impl
