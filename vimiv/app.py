# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Main application class using QApplication."""

import os

from PyQt5.QtWidgets import QApplication

import vimiv
from vimiv.config import keybindings
from vimiv.commands import commands
from vimiv.modes import modehandler
from vimiv.utils import objreg, impaths, libpaths, files


class Application(QApplication):
    """Main application class."""

    @objreg.register("app")
    def __init__(self):
        """Initialize the main Qt application."""
        super().__init__([vimiv.__name__])  # Only pass program name to Qt

    @keybindings.add("q", "quit")
    @commands.register(instance="app")
    def quit(self):
        """Quit the QApplication and therefore exit."""
        super().quit()


# We want to use the name open here as it is the best name for the command
@commands.argument("paths")
@commands.register()
def open(path):  # pylint: disable=redefined-builtin
    """Open a path.

    If the path is an image, it is opened in image mode. Otherwise if it is a
    directory, it is opened in the library.

    Args:
        path: The path as string.
    """
    assert isinstance(path, str), "Path must be given as string."
    open_paths([path])


def open_paths(paths, select_mode=True):
    """Open a list of paths possibly switching to a new mode.

    Args:
        paths: List of paths to open.
        select_mode: If True, select mode according to paths given.
    """
    images, directories = files.get_supported(paths)
    mode = "library"
    if images:
        _open_images(images)
        mode = "image"
    elif directories:
        libpaths.load(directories[0])
    else:
        libpaths.load(os.getcwd())
    if select_mode:
        modehandler.enter(mode)


def _open_images(images):
    """Open a list of images.

    If the list contains a single element, all images in the same directory are
    opened. Otherwise the list is opened as is.

    Args:
        images: List of images.
    """
    images = [os.path.abspath(image) for image in images]  # chdir later
    image_directory = os.path.dirname(images[0])
    # Populate library if the directory has changed
    if image_directory != os.getcwd():
        os.chdir(image_directory)
        libpaths.load(image_directory)
    # Populate list of images in the same directory for only one path
    index = 0
    if len(images) == 1:
        first_image = os.path.abspath(os.path.basename(images[0]))
        images, _ = files.get_supported(files.ls(os.getcwd()))
        index = images.index(first_image)
    # Load images
    impaths.load(images, index)
