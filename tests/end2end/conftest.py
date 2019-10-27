# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions, fixtures and bdd-like steps for end2end testing."""

import os

from PyQt5.QtGui import QPixmap

import pytest
import pytest_bdd as bdd

import mockdecorators
from vimivprocess import VimivProc


@pytest.fixture(autouse=True, scope="module")
def cleanup_objreg():
    """Fixture to clear any left-over instances of the objreg."""
    yield
    mockdecorators.mockregister_cleanup()


###############################################################################
#                                  bdd Given                                  #
###############################################################################
@bdd.given("I start vimiv")
@bdd.given("I open any directory")
def start_vimiv(qtbot, tmpdir):
    yield from run_directory(tmpdir)


@bdd.given("I open a directory for which I do not have access permissions")
def start_directory_without_permission(qtbot, tmpdir):
    yield from run_directory(tmpdir, permission=0o666)


@bdd.given(bdd.parsers.parse("I open a directory with {n_children:d} paths"))
def start_directory_with_n_paths(qtbot, tmpdir, n_children):
    yield from run_directory(tmpdir, n_children=n_children)


@bdd.given(bdd.parsers.parse("I open a directory with {n_images:d} images"))
def start_directory_with_n_images(qtbot, tmpdir, n_images):
    yield from run_directory(tmpdir, n_images=n_images)


@bdd.given("I open any image")
def start_any_image(qtbot, tmpdir):
    yield from run_image(tmpdir)


@bdd.given(bdd.parsers.parse("I open any image of size {size}"))
def start_any_image_of_size(qtbot, tmpdir, size):
    size = [int(elem) for elem in size.split("x")]
    yield from run_image(tmpdir, size=size)


@bdd.given(bdd.parsers.parse("I open {n_images:d} images"))
def start_n_images(qtbot, tmpdir, n_images):
    yield from run_image(tmpdir, n_images=n_images)


@bdd.given(bdd.parsers.parse("I open {n_images:d} images with {args}"))
def start_n_images_with_args(qtbot, tmpdir, n_images, args):
    yield from run_image(tmpdir, n_images=n_images, args=args.split())


###############################################################################
#                              helper functions                               #
###############################################################################
def run_directory(tmpdir, n_children=0, n_images=0, permission=0o777):
    path = tmpdir.mkdir("directory")
    os.chmod(str(path), permission)

    for i in range(n_children):
        path.mkdir(f"child_{i + 1:02d}")

    create_n_images(path, n_images)

    with VimivProc([str(path)]):
        yield


def run_image(tmpdir, n_images=1, size=(300, 300), args=None):
    paths = create_n_images(tmpdir, n_images, size=size)
    args = paths if args is None else paths + args
    with VimivProc(args):
        yield


def create_n_images(tmpdir, number, size=(300, 300), imgformat="jpg"):
    paths = []
    for i in range(1, number + 1):
        basename = f"image.{imgformat}" if number == 1 else f"image_{i:02d}.{imgformat}"
        path = str(tmpdir.join(basename))
        QPixmap(*size).save(path, imgformat)
        paths.append(path)
    return paths
