# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

from PyQt5.QtGui import QResizeEvent

import pytest_bdd as bdd


bdd.scenarios("imagescroll.feature")


@bdd.when("I resize the image")
def resize_image(image):
    image.resizeEvent(QResizeEvent(image.size(), image.size()))


@bdd.then(bdd.parsers.parse("the image {position} should be {value:d}"))
def check_image_coordinate(image, position, value):
    rect = image.visible_rect
    assert position_to_value(position, rect) == value


@bdd.then(bdd.parsers.parse("the image {position} should not be {value:d}"))
def check_image_not_coordinate(image, position, value):
    rect = image.visible_rect
    assert position_to_value(position, rect) != value


def position_to_value(position, rect):
    position = position.lower()
    if position == "left-edge":
        return rect.x()
    if position == "right-edge":
        return rect.x() + rect.width()
    if position == "top-edge":
        return rect.y()
    raise ValueError(f"Unknown position '{position}'")
