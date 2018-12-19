# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions, fixtures and bdd-like steps for end2end testing."""

from PyQt5.QtGui import QPixmap

import pytest_bdd as bdd

import vimivprocess


###############################################################################
#                              helper functions                               #
###############################################################################
def create_image(path, fileformat="jpg", size=(300, 300)):
    """Generate a valid image file.

    Args:
        path: The path at which the image is created.
        fileformat: The fileformat of the image to create, e.g. jpg.
        size: (width, height) as tuple of integers.
    """
    pixmap = QPixmap(*size)
    pixmap.save(path, fileformat)


###############################################################################
#                                  bdd Given                                  #
###############################################################################


@bdd.given("I start vimiv")
def startup(qtbot, tmpdir):
    # Not really any different from "I open any directory" below but cleaner to
    # read in scenarios where the directory is not explicitly needed
    vimivprocess.init(qtbot, [str(tmpdir)])
    yield
    vimivprocess.exit()


@bdd.given("I open any directory")
def any_directory(qtbot, tmpdir):
    path = tmpdir.mkdir("directory")
    vimivprocess.init(qtbot, [str(path)])
    yield
    vimivprocess.exit()


@bdd.given(bdd.parsers.parse("I open a directory with {N} paths"))
def directory_with_n_paths(qtbot, tmpdir, N):
    path = tmpdir.mkdir("directory")
    for i in range(int(N)):
        path.mkdir("child_%d" % (i + 1))
    vimivprocess.init(qtbot, [str(path)])
    yield
    vimivprocess.exit()


@bdd.given("I open any image")
def any_image(qtbot, tmpdir):
    path = str(tmpdir.join("image.jpg"))
    create_image(path)
    vimivprocess.init(qtbot, [path])
    yield
    vimivprocess.exit()


@bdd.given(bdd.parsers.parse("I open any image of size {size}"))
def any_image_of_size(qtbot, tmpdir, size):
    size = size.split("x")
    size = [int(elem) for elem in size]
    path = str(tmpdir.join("image.jpg"))
    create_image(path, size=size)
    vimivprocess.init(qtbot, [path])
    yield
    vimivprocess.exit()


@bdd.given(bdd.parsers.parse("I open {N} images"))
def n_images(qtbot, tmpdir, N):
    paths = []
    for i in range(1, int(N) + 1):
        path = str(tmpdir.join("image_%d.jpg" % (i)))
        create_image(path)
        paths.append(path)
    vimivprocess.init(qtbot, paths)
    yield
    vimivprocess.exit()
