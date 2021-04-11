# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.imutils.metadata."""

from fractions import Fraction
from PyQt5.QtGui import QPixmap
import pytest

from vimiv import imutils, utils
from vimiv.imutils import metadata
from vimiv.imutils.metadata import MetadataHandler

try:
    import piexif
except ImportError:
    piexif = None

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
def metadata_content():
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
def dummy_image(qapp, tmp_path):
    filename = "./image.jpg"
    filename = str(tmp_path / "image.jpg")
    QPixmap(300, 300).save(filename)
    return filename


@pytest.fixture
def metadata_handler(add_metadata_information, dummy_image, metadata_content):
    assert pyexiv2 is not None, "pyexiv2 required to add metadata information"
    add_metadata_information(dummy_image, metadata_content)
    return MetadataHandler(dummy_image)


@pytest.fixture
def metadata_handler_piexif(dummy_image, metadata_handler):
    metadata_handler._ext_handler = metadata._ExternalKeyHandlerPiexif(dummy_image)
    return metadata_handler


def test_metadatahandler_fetch_key(metadata_handler, metadata_content):
    for key, value in metadata_content.items():
        fetched_key, _, fetched_value = metadata_handler.fetch_key(key)
        assert fetched_key == key
        try:
            assert fetched_value == value.human_value
        except AttributeError:
            assert fetched_value == value.raw_value


def test_metadatahandler_fetch_key_piexif(metadata_handler_piexif, metadata_content):
    for key, value in metadata_content.items():
        fetched_key, _, fetched_value = metadata_handler_piexif.fetch_key(key)
        short_key = key.rpartition(".")[-1]
        assert fetched_key == short_key
        assert fetched_value == value.raw_value
