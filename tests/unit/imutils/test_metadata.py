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


EXTERNAL_CONTENT = {
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
    ),
    "Iptc.Application2.Program": pyexiv2.iptc.IptcTag(
        "Iptc.Application2.Program", ["Vimiv"]
    ),
    "Iptc.Application2.Keywords": pyexiv2.iptc.IptcTag(
        "Iptc.Application2.Keywords", ["ImageViewer", "Application", "Linux"]
    ),
    "Xmp.xmpRights.Owner": pyexiv2.xmp.XmpTag(
        "Xmp.xmpRights.Owner", ["vimiv-AUTHORS-2021"]
    ),
    "Xmp.xmp.Rating": pyexiv2.xmp.XmpTag("Xmp.xmp.Rating", 5),
}


INTERNAL_CONTENT = {
    "Vimiv.XDimension": 300,
    "Vimiv.YDimension": 300,
    "Vimiv.FileType": "jpg",
}


# TODO: Write as variable
def _full_content():
    # Merge both dicts
    # return external_content | internal_content # Only working for Py 3.9
    content = EXTERNAL_CONTENT.copy()
    content.update(INTERNAL_CONTENT)
    return content


FULL_CONTENT = _full_content()


INVALID_KEYS = ["Invalid", "Invalid.Key", "Not.Valid.2"]


TEST_KEYS = [
    list(FULL_CONTENT.keys()),
    ["Exif.Image.Copyright", "Exif.Image.Make"],
    ["Exif.GPSInfo.GPSAltitude", "Vimiv.XDimension", "Vimiv.YDimension"],
    INVALID_KEYS + ["Exif.Photo.FocalLength"],
    ["Iptc.Application2.Program", "Iptc.Application2.Keywords"],
    ["Xmp.xmp.Rating", "Exif.Photo.ISOSpeedRatings", "Iptc.Application2.Program"],
    ["Xmp.xmp.Rating", "Xmp.xmpRights.Owner"],
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
def main_handler_exiv2():
    return lambda s: MetadataHandler(s)


@pytest.fixture
def main_handler_piexif(main_handler_exiv2):
    def aux(img: str):
        handler = main_handler_exiv2(img)
        handler._ext_handler = metadata._ExternalKeyHandlerPiexif(img)
        return handler

    return aux


# Todo: Cleanup fixture by reusing main_handler_* fixtures
@pytest.fixture(params=[True, False])
def main_handler(request, main_handler_exiv2):
    if request.param:
        return lambda s: MetadataHandler(s)

    def aux(img: str):
        handler = main_handler_exiv2(img)
        handler._ext_handler = metadata._ExternalKeyHandlerPiexif(img)
        return handler

    return aux


@pytest.fixture(
    params=[metadata.ExternalKeyHandler, metadata._ExternalKeyHandlerPiexif]
)
def external_handler(request):
    """Parametrized pytest fixture to yield the different external handlers."""
    yield request.param


def test_check_external_dependency():
    default = None
    assert metadata.check_external_dependency(default) == default


def test_check_external_dependency_piexif(piexif):
    default = None
    assert (
        metadata.check_external_dependency(default)
        == metadata._ExternalKeyHandlerPiexif
    )


def test_check_external_dependency_noexif(noexif):
    default = None
    assert (
        metadata.check_external_dependency(default) == metadata._ExternalKeyHandlerBase
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


def value_match(required_value, actual_value):
    try:
        val = required_value.human_value
    except AttributeError:
        try:
            val = required_value.raw_value
        except AttributeError:
            try:
                val = required_value.value
            except AttributeError:
                val = required_value

    # Iptc is a list with byte elements of any type
    # Xmp can be a list with elements of any type
    try:
        try:
            joined_list = ", ".join([str(e.decode()) for e in val])
        except AttributeError:
            joined_list = ", ".join([str(e) for e in val])
    except TypeError:
        joined_list = ""

    assert actual_value in (val, joined_list)


def value_match_piexif(required_value, actual_value):
    try:
        val = required_value.raw_value
    except AttributeError:
        try:
            val = required_value.value
        except AttributeError:
            val = required_value

    assert actual_value == val


# TODO add more test cases
@pytest.mark.parametrize(
    "metadata_key, expected_key, expected_value",
    [("Exif.Image.Copyright", "Exif.Image.Copyright", "vimiv-AUTHORS-2021")],
)
def test_metadatahandler_fetch_key_exiv2(
    main_handler_exiv2,
    dummy_image,
    add_metadata_information,
    metadata_key,
    expected_key,
    expected_value,
):
    src = dummy_image()
    add_metadata_information(src, EXTERNAL_CONTENT)
    handler = main_handler_exiv2(src)

    fetched_key, _, fetched_value = handler.fetch_key(metadata_key)
    assert fetched_key == expected_key
    assert fetched_value == expected_value


# TODO add more test cases
@pytest.mark.parametrize(
    "metadata_key, expected_key, expected_value",
    [("Exif.Image.Copyright", "Exif.Image.Copyright", "vimiv-AUTHORS-2021")],
)
def test_metadatahandler_fetch_key_piexif(
    main_handler_piexif,
    dummy_image,
    add_metadata_information,
    metadata_key,
    expected_key,
    expected_value,
):
    src = dummy_image()
    add_metadata_information(src, EXTERNAL_CONTENT)
    handler = main_handler_piexif(src)

    if "iptc" in metadata_key.lower() or "xmp" in metadata_key.lower():
        return

    fetched_key, _, fetched_value = handler.fetch_key(metadata_key)
    short_key = metadata_key.rpartition(".")[-1]
    assert fetched_key in (metadata_key, short_key)
    assert fetched_value == expected_value


@pytest.mark.parametrize("metadata_key", INVALID_KEYS)
def test_metadatahandler_fetch_key_invalid(
    main_handler, dummy_image, add_metadata_information, metadata_key
):
    src = dummy_image()
    add_metadata_information(src, EXTERNAL_CONTENT)
    handler = main_handler(src)

    with pytest.raises(KeyError):
        _, _, _ = handler.fetch_key(metadata_key)


@pytest.mark.parametrize("current_keys", TEST_KEYS)
def test_metadatahandler_fetch_keys_exiv2(
    main_handler_exiv2, add_metadata_information, dummy_image, current_keys
):
    src = dummy_image()
    add_metadata_information(src, EXTERNAL_CONTENT)
    handler = main_handler_exiv2(src)

    valid_keys = [key for key in current_keys if key in FULL_CONTENT.keys()]
    fetched = handler.fetch_keys(current_keys)
    assert len(fetched) == len(valid_keys)

    for current_key in valid_keys:
        assert current_key in fetched
        value_match(FULL_CONTENT[current_key], fetched[current_key][1])


@pytest.mark.parametrize("current_keys", TEST_KEYS)
def test_metadatahandler_fetch_keys_piexif(
    main_handler_piexif, add_metadata_information, dummy_image, current_keys
):
    src = dummy_image()
    add_metadata_information(src, EXTERNAL_CONTENT)
    handler = main_handler_piexif(src)

    valid_keys = [
        key
        for key in current_keys
        if key in FULL_CONTENT.keys()
        and not ("iptc" in key.lower() or "xmp" in key.lower())
    ]

    fetched = handler.fetch_keys(current_keys)
    assert len(fetched) == len(valid_keys)

    for current_key in valid_keys:
        short_key = current_key.rpartition(".")[-1]
        assert current_key in fetched or short_key in fetched
        # Internal keys are still in long form
        try:
            value_match_piexif(FULL_CONTENT[current_key], fetched[short_key][1])
        except KeyError:
            value_match_piexif(FULL_CONTENT[current_key], fetched[current_key][1])


def test_metadatahandler_get_keys(main_handler, add_metadata_information, dummy_image):
    src = dummy_image()
    add_metadata_information(src, EXTERNAL_CONTENT)
    handler = main_handler(src)

    available_keys = list(FULL_CONTENT.keys())

    if isinstance(handler._external_handler, metadata._ExternalKeyHandlerPiexif):
        available_keys = [
            e for e in available_keys if not ("iptc" in e.lower() or "xmp" in e.lower())
        ]

    fetched_keys = list(handler.get_keys())

    # Available_keys does not contain all possible keys
    assert len(fetched_keys) >= len(available_keys)

    for key in available_keys:
        short_key = key.rpartition(".")[-1]
        assert key in fetched_keys or short_key in fetched_keys


@pytest.mark.parametrize(
    "metadata, expected_date",
    [
        (
            {
                "Exif.Image.DateTime": pyexiv2.exif.ExifTag(
                    "Exif.Image.DateTime", "2017-12-16 16:21:57"
                )
            },
            "2017-12-16 16:21:57",
        ),
        ({}, ""),
    ],
)
def test_external_keyhandler_get_date_time(
    external_handler, dummy_image, add_metadata_information, metadata, expected_date
):
    src = dummy_image("image.jpg")
    add_metadata_information(src, metadata)
    handler = external_handler(src)
    assert handler.get_date_time() == expected_date


def test_external_keyhandler_copy_metadata(
    external_handler, dummy_image, add_metadata_information
):
    src = dummy_image("src.jpg")
    add_metadata_information(src, EXTERNAL_CONTENT)
    src_handler = external_handler(src)

    dest = dummy_image("dest.jpg")
    src_handler.copy_metadata(dest)
    assert len(list(metadata.MetadataHandler(dest).get_keys())) >= len(FULL_CONTENT)
