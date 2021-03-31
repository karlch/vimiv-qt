# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.imutils.metadata."""

from fractions import Fraction
from PyQt5.QtGui import QPixmap
from PIL import Image
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
def dummy_image():
    filename = "./image.jpg"
    Image.new(mode="RGB", size=(300, 300), color="red").save(filename)
    # QPixmap(*(300, 300)).save(filename)
    return filename


@pytest.fixture
def get_MetadataHandler(add_metadata_information, dummy_image, metadata_content):
    assert pyexiv2 is not None, "pyexiv2 required to add metadata information"
    add_metadata_information(dummy_image, metadata_content)
    return MetadataHandler(dummy_image)


def test_MetadataHandler_fetch_key(get_MetadataHandler, metadata_content):
    handler = get_MetadataHandler
    for key, value in metadata_content.items():
        data = handler.fetch_key(key)
        assert data[0] == key
        try:
            assert data[2] == value.human_value
        except AttributeError:
            assert data[2] == value.raw_value
