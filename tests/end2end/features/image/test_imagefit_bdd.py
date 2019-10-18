# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest_bdd as bdd


bdd.scenarios("imagefit.feature")


def almost_equal(size, expected):
    """Check if size is almost equal to the expected value.

    When scaling images the float value scale times the integer original size
    can lead to the size being smaller than the expected value by one.
    """
    assert size + 1 >= expected
    assert size <= expected


@bdd.then(bdd.parsers.parse("the pixmap width should be {width}"))
def check_pixmap_width(image, width):
    almost_equal(image.current_width(), int(width))


@bdd.then(bdd.parsers.parse("the pixmap height should be {height}"))
def check_pixmap_height(image, height):
    almost_equal(image.current_height(), int(height))


@bdd.then(bdd.parsers.parse("the pixmap width should fit"))
def check_pixmap_width_fit(image):
    almost_equal(image.current_width(), image.width())


@bdd.then(bdd.parsers.parse("the pixmap height should fit"))
def check_pixmap_height_fit(image):
    almost_equal(image.current_height(), image.height())


@bdd.then(bdd.parsers.parse("the pixmap width should not fit"))
def check_pixmap_width_no_fit(image):
    assert image.width() != image.current_width()


@bdd.then(bdd.parsers.parse("the pixmap height should not fit"))
def check_pixmap_height_no_fit(image):
    assert image.height() != image.current_height()
