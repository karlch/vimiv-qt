# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

"""Fixtures for pytest."""

import os
import logging
import urllib.request

import pytest

from vimiv.plugins import metadata_pyexiv2, metadata_piexif


CI = "CI" in os.environ

HAS_PIEXIF = metadata_piexif.piexif is not None
HAS_PYEXIV2 = metadata_pyexiv2.pyexiv2 is not None
HAS_METADATA = HAS_PIEXIF or HAS_PYEXIV2

# fmt: off
PLATFORM_MARKERS = (
    ("ci", CI, "Only run on ci"),
    ("ci_skip", not CI, "Skipped on ci"),
)

METADATA_MARKERS = (
    ("metadata", HAS_METADATA, "Only run with metadata support"),
    ("nometadata", not HAS_METADATA, "Only run without metadata support"),
    ("piexif", HAS_PIEXIF, "Only run with piexif"),
    ("pyexiv2", HAS_PYEXIV2, "Only run with pyexiv2"),
)
# fmt: on


def apply_fixture_markers(item, *names):
    """Helper function to mark all tests using specific fixtures with that mark."""
    for name in names:
        marker = getattr(pytest.mark, name)
        if name in item.fixturenames:
            item.add_marker(marker)


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
        apply_fixture_markers(item, "piexif", "pyexiv2")
        apply_markers_helper(item, PLATFORM_MARKERS)
        apply_markers_helper(item, METADATA_MARKERS)


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
