# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Fixtures and bdd-given steps related to setup and cleanup for end2end testing."""

import logging
import os

from PyQt5.QtGui import QPixmap

import pytest
import pytest_bdd as bdd

import mockdecorators

with mockdecorators.apply():
    from vimiv import api, startup, utils
    from vimiv.commands import runners
    from vimiv.imutils import filelist, immanipulate


########################################################################################
#                                   Pytest fixtures                                    #
########################################################################################
@pytest.fixture(autouse=True)
def qapp(qtbot):
    """Ensure a Qt application from qtbot is always available for end2end tests."""


@pytest.fixture(autouse=True)
def mock_directories(tmpdir):
    directory = tmpdir.join(".vimiv-data")
    utils.xdg.basedir = str(directory)
    yield
    utils.xdg.basedir = None


@pytest.fixture(autouse=True)
def cleanup():
    """Fixture to reset various vimiv properties at the end of each test."""
    yield
    utils.Pool.clear()
    utils.Pool.wait(5000)
    api.settings.reset()
    api.mark.mark_clear()
    runners._last_command.clear()
    filelist._paths = []
    filelist._index = 0
    for mode in api.modes.ALL:
        mode._entered = False


@pytest.fixture(autouse=True, scope="module")
def cleanup_module():
    """Fixture to reset properties on a module basis."""
    yield
    logging.getLogger().handlers = []  # Mainly to remove the statusbar handler
    mockdecorators.mockregister_cleanup()


@pytest.fixture(autouse=True, scope="session")
def faster_wait_times():
    """Fixture to set faster wait times for testing."""
    api.working_directory.WorkingDirectoryHandler.WAIT_TIME = 0
    immanipulate.WAIT_TIME = 0


###############################################################################
#                                  bdd Given                                  #
###############################################################################
@bdd.given("I start vimiv")
@bdd.given("I open any directory")
def start_vimiv(tmpdir):
    start_directory(tmpdir)


@bdd.given("I open a directory for which I do not have access permissions")
def start_directory_without_permission(tmpdir):
    start_directory(tmpdir, permission=0o666)


@bdd.given(bdd.parsers.parse("I open a directory with {n_children:d} paths"))
def start_directory_with_n_paths(tmpdir, n_children):
    start_directory(tmpdir, n_children=n_children)


@bdd.given(bdd.parsers.parse("I open a directory with {n_images:d} images"))
def start_directory_with_n_images(tmpdir, n_images):
    start_directory(tmpdir, n_images=n_images)


@bdd.given("I open any image")
def start_any_image(tmpdir):
    start_image(tmpdir)


@bdd.given(bdd.parsers.parse("I open any image of size {size}"))
def start_any_image_of_size(tmpdir, size):
    size = [int(elem) for elem in size.split("x")]
    start_image(tmpdir, size=size)


@bdd.given(bdd.parsers.parse("I open {n_images:d} images"))
def start_n_images(tmpdir, n_images):
    start_image(tmpdir, n_images=n_images)


@bdd.given(bdd.parsers.parse("I open {n_images:d} images with {args}"))
def start_n_images_with_args(tmpdir, n_images, args):
    start_image(tmpdir, n_images=n_images, args=args.split())


###############################################################################
#                              helper functions                               #
###############################################################################
def start_directory(tmpdir, n_children=0, n_images=0, permission=0o777):
    """Run vimiv startup using one directory as the passed path."""
    directory = tmpdir.mkdir("directory")
    os.chmod(str(directory), permission)

    for i in range(n_children):
        directory.mkdir(f"child_{i + 1:02d}")

    create_n_images(directory, n_images)

    start([str(directory)])


def start_image(tmpdir, n_images=1, size=(300, 300), args=None):
    """Run vimiv startup using n images as the passed paths."""
    paths = create_n_images(tmpdir, n_images, size=size)
    args = paths if args is None else paths + args
    start(args)


def start(argv):
    """Run vimiv startup passing argv as argument list."""
    args = startup.setup_pre_app(argv)
    startup.setup_post_app(args)


def create_n_images(tmpdir, number, size=(300, 300), imgformat="jpg"):
    paths = []
    for i in range(1, number + 1):
        basename = f"image.{imgformat}" if number == 1 else f"image_{i:02d}.{imgformat}"
        path = str(tmpdir.join(basename))
        QPixmap(*size).save(path, imgformat)
        paths.append(path)
    return paths
