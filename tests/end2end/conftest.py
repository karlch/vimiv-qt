# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Fixtures and bdd-given steps related to setup and cleanup for end2end testing."""

import logging

from PyQt5.QtGui import QPixmap

import pytest
import pytest_bdd as bdd

import mockdecorators

with mockdecorators.apply():
    from vimiv import api, startup, utils
    from vimiv.commands import runners
    from vimiv.imutils import filelist
    from vimiv.gui import eventhandler
    from vimiv.utils import trash_manager


########################################################################################
#                                   Pytest fixtures                                    #
########################################################################################
@pytest.fixture(autouse=True)
def ensureqtbot(qtbot):
    """Ensure a Qt application from qtbot is always available for end2end tests."""


@pytest.fixture(autouse=True)
def mock_directories(tmp_path):
    directory = tmp_path / ".vimiv-data"
    utils.xdg.basedir = str(directory)
    yield
    utils.xdg.basedir = None


@pytest.fixture(autouse=True)
def home_directory(tmp_path, mocker):
    """Fixture to mock os.path.expanduser to return a different home directory."""
    directory = tmp_path / ".home"
    directory.mkdir()
    new_home = str(directory)

    def expand_user(path):
        return path.replace("~", new_home)

    mocker.patch("os.path.expanduser", new=expand_user)
    return new_home


@pytest.fixture(autouse=True)
def cleanup():
    """Fixture to reset various vimiv properties at the end of each test."""
    yield
    utils.Throttle.stop_all()
    utils.Pool.clear()
    utils.Pool.wait(5000)
    api.settings.reset()
    api.mark.mark_clear()
    runners._last_command.clear()
    filelist._paths = []
    filelist._index = 0
    api.modes.Mode.active = api.modes.IMAGE
    for mode in api.modes.ALL:
        mode._entered = False
        mode.last = api.modes.IMAGE if mode != api.modes.IMAGE else api.modes.LIBRARY
    trash_manager.trash_info.cache_clear()
    eventhandler.EventHandlerMixin.partial_handler.clear_keys()


@pytest.fixture(autouse=True, scope="module")
def cleanup_module():
    """Fixture to reset properties on a module basis."""
    yield
    logging.getLogger().handlers = []  # Mainly to remove the statusbar handler
    mockdecorators.mockregister_cleanup()


@pytest.fixture(autouse=True, scope="session")
def faster_wait_times():
    """Fixture to set faster wait times for testing."""
    utils.Throttle.unthrottle()


###############################################################################
#                                  bdd Given                                  #
###############################################################################
@bdd.given("I start vimiv")
@bdd.given("I open any directory")
def start_vimiv(tmp_path):
    start_directory(tmp_path)


@bdd.given(bdd.parsers.parse("I start vimiv with {args}"))
def start_vimiv_with_args(tmp_path, args):
    start_directory(tmp_path, args=args.split())


@bdd.given("I run vimiv --version")
def run_vimiv_version():
    with pytest.raises(SystemExit):
        startup.setup_pre_app(["--version"])


@bdd.given("I start vimiv with --log-level <level>")
def start_vimiv_log_level(tmp_path, level):
    start_directory(tmp_path, args=["--log-level", level])


@bdd.given("I open a directory for which I do not have access permissions")
def start_directory_without_permission(tmp_path):
    start_directory(tmp_path, permission=0o666)


@bdd.given(bdd.parsers.parse("I open a directory with {n_children:d} paths"))
def start_directory_with_n_paths(tmp_path, n_children):
    start_directory(tmp_path, n_children=n_children)


@bdd.given(bdd.parsers.parse("I open a directory with {n_images:d} images"))
def start_directory_with_n_images(tmp_path, n_images):
    start_directory(tmp_path, n_images=n_images)


@bdd.given("I open any image")
def start_any_image(tmp_path):
    start_image(tmp_path)


@bdd.given(bdd.parsers.parse("I open any image of size {size}"))
def start_any_image_of_size(tmp_path, size):
    size = [int(elem) for elem in size.split("x")]
    start_image(tmp_path, size=size)


@bdd.given(bdd.parsers.parse("I open {n_images:d} images"))
def start_n_images(tmp_path, n_images):
    start_image(tmp_path, n_images=n_images)


@bdd.given(
    bdd.parsers.parse("I open {n_images:d} images without leading zeros in their name")
)
def start_n_images_no_zeros(tmp_path, n_images):
    start_image(tmp_path, n_images=n_images, leading_zeros=False)


@bdd.given(bdd.parsers.parse("I open {n_images:d} images with {args}"))
def start_n_images_with_args(tmp_path, n_images, args):
    start_image(tmp_path, n_images=n_images, args=args.split())


@bdd.given(bdd.parsers.parse("I open the image '<name>'"))
@bdd.given(bdd.parsers.parse("I open the image '{name}'"))
def start_image_name(tmp_path, name):
    filename = str(tmp_path / name)
    create_image(filename)
    start([filename])


@bdd.given("I open an animated gif")
def start_animated_gif(gif):
    start([gif])


@bdd.given("I open a vector graphic")
def start_vector_graphic(svg):
    start([svg])


@bdd.given("I open images from multiple directories")
def start_multiple_directories(tmp_path):
    dir1 = tmp_path / "dir1"
    dir1.mkdir()
    dir2 = tmp_path / "dir2"
    dir2.mkdir()
    dir3 = tmp_path / "dir3"
    dir3.mkdir()

    paths = []

    for i in range(1, 4):
        path = str(dir1 / f"image_dir1_{i}.png")
        create_image(path)
        paths.append(path)

    for i in range(1, 3):
        path = str(dir2 / f"also_image_dir2_{i}.png")
        create_image(path)
        paths.append(path)

    for i in range(1, 5):
        path = str(dir3 / f"more_image_dir3_{i}.png")
        create_image(path)
        paths.append(path)

    return start(paths)


@bdd.given("I capture output", target_fixture="output")
def capture_output(capsys):
    return Output(capsys)


###############################################################################
#                                  bdd Then                                   #
###############################################################################
@bdd.then(bdd.parsers.parse("stdout should contain '{text}'"))
def check_stdout(output, text):
    assert text in output.out


@bdd.then(bdd.parsers.parse("stderr should contain '{text}'"))
def check_stderr(output, text):
    assert text in output.err


###############################################################################
#                              helpers                                        #
###############################################################################
def start_directory(tmp_path, n_children=0, n_images=0, permission=0o777, args=None):
    """Run vimiv startup using one directory as the passed path."""
    args = args if args is not None else []
    directory = tmp_path / "directory"
    directory.mkdir(mode=permission)

    for i in range(n_children):
        (directory / f"child_{i + 1:02d}").mkdir()

    create_n_images(directory, n_images)

    start([directory] + args)


def start_image(tmp_path, n_images=1, size=(300, 300), args=None, leading_zeros=True):
    """Run vimiv startup using n images as the passed paths."""
    paths = create_n_images(tmp_path, n_images, size=size, leading_zeros=leading_zeros)
    argv = paths if args is None else paths + args
    start(argv)


def start(argv):
    """Run vimiv startup passing argv as argument list."""
    argv = [str(arg) for arg in argv]
    args = startup.setup_pre_app(argv)
    startup.setup_post_app(args)


def create_n_images(
    directory, number, size=(300, 300), leading_zeros=True, imgformat="jpg"
):
    paths = []
    for i in range(1, number + 1):
        if number == 1:
            basename = f"image.{imgformat}"
        elif leading_zeros:
            basename = f"image_{i:02d}.{imgformat}"
        else:
            basename = f"image_{i:d}.{imgformat}"
        path = directory / basename
        create_image(str(path.resolve()), size=size)
        paths.append(path)
    return paths


def create_image(filename: str, *, size=(300, 300)):
    QPixmap(*size).save(filename)


class Output:
    """Wrapper class around the pytest capsys fixture for ease of usage in bdd."""

    def __init__(self, capsys):
        self.capsys = capsys
        self._out = self._err = None

    @property
    def out(self):
        if self._out is None:
            self._capture_output()
        return self._out

    @property
    def err(self):
        if self._err is None:
            self._capture_output()
        return self._err

    def _capture_output(self):
        captured = self.capsys.readouterr()
        self._out = captured.out
        self._err = captured.err
