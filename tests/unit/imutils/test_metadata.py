# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.imutils.metadata."""

from fractions import Fraction
from PyQt5.QtGui import QPixmap
import pytest

from vimiv.imutils import metadata
from vimiv.imutils.metadata import MetadataHandler

try:
    import pyexiv2
except ImportError:
    pyexiv2 = None


@pytest.fixture(
    params=[metadata.ExternalKeyHandler, metadata._ExternalKeyHandlerPiexif]
)
def external_handler(request):
    """Parametrized pytest fixture to yield the different external handlers."""
    yield request.param


def test_check_external_dependency():
    default = None
    assert metadata.check_external_dependancy(default) == default


def test_check_external_dependency_piexif(piexif):
    default = None
    assert (
        metadata.check_external_dependancy(default)
        == metadata._ExternalKeyHandlerPiexif
    )


def test_check_external_dependency_noexif(noexif):
    default = None
    assert (
        metadata.check_external_dependancy(default) == metadata._ExternalKeyHandlerBase
    )


@pytest.mark.parametrize(
    "methodname, args",
    (
        ("copy_metadata", ("dest.jpg",)),
        ("get_date_time", ()),
        ("fetch_key", ([],)),
        ("get_keys", ()),
    ),
)
def test_handler_base_raises(methodname, args):
    handler = metadata._ExternalKeyHandlerBase()
    method = getattr(handler, methodname)
    with pytest.raises(metadata.UnsupportedMetadataOperation):
        method(*args)


@pytest.mark.parametrize(
    "handler, expected_msg",
    (
        (metadata.ExternalKeyHandler, "not supported by pyexiv2"),
        (metadata._ExternalKeyHandlerPiexif, "not supported by piexif"),
        (metadata._ExternalKeyHandlerBase, "not supported. Please install"),
    ),
)
def test_handler_exception_customization(handler, expected_msg):
    with pytest.raises(metadata.UnsupportedMetadataOperation, match=expected_msg):
        handler.raise_exception("test operation")


@pytest.fixture()
def external_content():
    return {
        "Exif.Image.Copyright": pyexiv2.exif.ExifTag(
            "Exif.Image.Copyright", "vimiv-AUTHORS-2021"
        ),
        "Exif.Image.DateTime": pyexiv2.exif.ExifTag(
            "Exif.Image.DateTime", "2017-12-16 16:21:57"
        ),
        "Exif.Image.Make": pyexiv2.exif.ExifTag("Exif.Image.Make", "vimiv"),
        "Exif.Photo.ApertureValue": pyexiv2.exif.ExifTag(
            "Exif.Photo.ApertureValue", Fraction(4)
        ),
        "Exif.Photo.ExposureTime": pyexiv2.exif.ExifTag(
            "Exif.Photo.ExposureTime", Fraction(1, 25)
        ),
        "Exif.Photo.FocalLength": pyexiv2.exif.ExifTag(
            "Exif.Photo.FocalLength", Fraction(600)
        ),
        "Exif.Photo.ISOSpeedRatings": pyexiv2.exif.ExifTag(
            "Exif.Photo.ISOSpeedRatings", [320]
        ),
        "Exif.GPSInfo.GPSAltitude": pyexiv2.exif.ExifTag(
            "Exif.GPSInfo.GPSAltitude", Fraction(2964)
        )
        # TODO: ADD IPTC
    }


@pytest.fixture()
def internal_content():
    return {"Vimiv.XDimension": 300, "Vimiv.YDimension": 300, "Vimiv.FileType": "jpg"}


@pytest.fixture()
def metadata_content(external_content, internal_content):
    # Merge both dicts
    # return external_content | internal_content # Only working for Py 3.9
    external_content.update(internal_content)
    return external_content


@pytest.fixture()
def metadata_test_keys(metadata_content):
    return [
        list(metadata_content.keys()),
        ["Exif.Image.Copyright", "Exif.Image.Make"],
        ["Exif.GPSInfo.GPSAltitude", "Vimiv.XDimension", "Vimiv.YDimension"],
    ]


@pytest.fixture()
def dummy_image(qapp, tmp_path):

    path = tmp_path

    def _get_img(name="image.jpg"):
        filename = str(path / name)
        QPixmap(300, 300).save(filename)
        return filename

    return _get_img


@pytest.fixture
def metadata_handler(add_metadata_information, dummy_image, external_content):
    assert pyexiv2 is not None, "pyexiv2 required to add metadata information"
    image = dummy_image()
    add_metadata_information(image, external_content)
    return MetadataHandler(image)


@pytest.fixture
def metadata_handler_piexif(metadata_handler):
    metadata_handler._ext_handler = metadata._ExternalKeyHandlerPiexif(
        metadata_handler.filename
    )
    return metadata_handler


def value_match(required_value, actual_value):
    try:
        assert actual_value == required_value.human_value
    except AttributeError:
        try:
            assert actual_value == required_value.raw_value
        except AttributeError:
            assert actual_value == required_value


def value_match_piexif(required_value, actual_value):
    try:
        assert actual_value == required_value.raw_value
    except AttributeError:
        assert actual_value == required_value


def test_metadatahandler_fetch_key(metadata_handler, metadata_content):
    for key, value in metadata_content.items():
        fetched_key, _, fetched_value = metadata_handler.fetch_key(key)
        assert fetched_key == key
        value_match(value, fetched_value)


def test_metadatahandler_fetch_key_piexif(metadata_handler_piexif, metadata_content):
    for key, value in metadata_content.items():
        fetched_key, _, fetched_value = metadata_handler_piexif.fetch_key(key)
        short_key = key.rpartition(".")[-1]
        assert fetched_key in (key, short_key)
        value_match_piexif(value, fetched_value)


def test_metadatahandler_fetch_keys(
    metadata_handler, metadata_content, metadata_test_keys
):
    for current_keys in metadata_test_keys:
        fetched = metadata_handler.fetch_keys(current_keys)
        assert len(fetched) == len(current_keys)

        for current_key in current_keys:
            assert current_key in fetched
            value_match(metadata_content[current_key], fetched[current_key][1])


def test_metadatahandler_fetch_keys_piexif(
    metadata_handler_piexif, metadata_content, metadata_test_keys
):
    for current_keys in metadata_test_keys:
        fetched = metadata_handler_piexif.fetch_keys(current_keys)
        assert len(fetched) == len(current_keys)
        print(fetched)

        for current_key in current_keys:
            short_key = current_key.rpartition(".")[-1]
            assert current_key in fetched or short_key in fetched
            # Internal keys are still in long form
            try:
                value_match_piexif(metadata_content[current_key], fetched[short_key][1])
            except KeyError:
                value_match_piexif(
                    metadata_content[current_key], fetched[current_key][1]
                )


def test_metadatahandler_get_keys(metadata_handler, metadata_content):
    fetched_keys = list(metadata_handler.get_keys())
    available_keys = list(metadata_content.keys())

    # Available_keys does not contain all possible keys
    assert len(fetched_keys) >= len(available_keys)

    for key in available_keys:
        assert key in fetched_keys


def test_metadatahandler_get_keys_piexif(metadata_handler_piexif, metadata_content):
    fetched_keys = list(metadata_handler_piexif.get_keys())
    available_keys = list(metadata_content.keys())

    # Available_keys does not contain all possible keys
    assert len(fetched_keys) >= len(available_keys)

    for key in available_keys:
        short_key = key.rpartition(".")[-1]
        assert key in fetched_keys or short_key in fetched_keys


@pytest.fixture
def external_keyhandler(add_metadata_information, dummy_image, external_content):
    assert pyexiv2 is not None, "pyexiv2 required to add metadata information"
    image = dummy_image()
    add_metadata_information(image, external_content)
    return metadata.ExternalKeyHandler(image)


@pytest.fixture
def external_keyhandler_piexif(add_metadata_information, dummy_image, external_content):
    assert pyexiv2 is not None, "pyexiv2 required to add metadata information"
    image = dummy_image()
    add_metadata_information(image, external_content)
    return metadata._ExternalKeyHandlerPiexif(image)


def test_external_keyhandler_get_date_time(
    external_keyhandler, external_keyhandler_piexif
):
    assert external_keyhandler.get_date_time() == "2017-12-16 16:21:57"
    assert external_keyhandler_piexif.get_date_time() == "2017-12-16 16:21:57"


def test_external_keyhandler_copy_metadata(
    external_keyhandler, external_keyhandler_piexif, dummy_image, metadata_content
):
    for handler in (external_keyhandler, external_keyhandler_piexif):
        dest = dummy_image("dest.jpg")
        handler.copy_metadata(dest)
        assert len(list(metadata.MetadataHandler(dest).get_keys())) >= len(
            metadata_content
        )
