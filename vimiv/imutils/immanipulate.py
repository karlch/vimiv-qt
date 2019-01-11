# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Perform more complex manipulations like brightness and contrast."""

import collections
import time

from PyQt5.QtCore import (QRunnable, QThreadPool, pyqtSignal, pyqtSlot,
                          QObject, QCoreApplication)
from PyQt5.QtGui import QPixmap, QImage

from vimiv.commands import commands, argtypes
from vimiv.config import keybindings
from vimiv.imutils import _c_manipulate  # pylint: disable=no-name-in-module
from vimiv.gui import statusbar
from vimiv.modes import modehandler, Modes
from vimiv.utils import objreg, clamp


WAIT_TIME = 0.3


class Manipulator(QObject):
    """Apply manipulations to an image.

    Provides commands for more complex manipulations like brightness and
    contrast.

    Attributes:
        manipulations: Dictionary storing the values of the manipulations.
        thread_id: ID of the current manipulation thread.
        data: bytes of the edited pixmap. Must be stored as the QPixmap is
            generated directly from the bytes and needs them to stay in memory.

        _handler: ImageFileHandler used to retrieve and set updated files.
        _current: Name of the manipulation that is currently being edited.
    """

    pool = QThreadPool()
    edited = pyqtSignal(str, int)
    focused = pyqtSignal(str)

    @objreg.register
    def __init__(self, handler):
        super().__init__()
        self._handler = handler
        self.manipulations = collections.OrderedDict([
            ("brightness", 0),
            ("contrast", 0),
        ])
        self.thread_id = 0
        self.data = None
        self._current = "brightness"
        QCoreApplication.instance().aboutToQuit.connect(self._on_quit)

    def set_pixmap(self, pixmap):
        """Set the pixmap to a newly edited version."""
        self._handler.update_pixmap(pixmap)

    def changed(self):
        """Return True if anything was edited."""
        return self.manipulations != {"brightness": 0, "contrast": 0}

    @keybindings.add("<return>", "accept", mode=Modes.MANIPULATE)
    @commands.register(mode=Modes.MANIPULATE)
    def accept(self):
        """Leave manipulate keeping the changes."""
        modehandler.leave(Modes.MANIPULATE)

    def reset(self):
        """Reset manipulations to default."""
        if self.changed():
            self._handler.update_pixmap(self._handler.transformed)
            self.manipulations = {
                "brightness": 0,
                "contrast": 0
            }
            self.edited.emit("brightness", 0)
            self.edited.emit("contrast", 0)

    @keybindings.add("b", "brightness", mode=Modes.MANIPULATE)
    @commands.register(mode=Modes.MANIPULATE)
    def brightness(self, value: argtypes.ManipulateLevel = 0, count: int = 0):
        """Manipulate brightness.

        **syntax:** ``:brightness [value]``

        If neither value nor count are given, set brightness to the current
        manipulation. Otherwise set brightness to the given value.

        positional arguments:
            * ``value``: Set the brightness to value. Range: -127 to 127.

        **count:** Set brightness to [count].
        """
        value = count if count else value
        self._update_manipulation("brightness", value)

    @keybindings.add("c", "contrast", mode=Modes.MANIPULATE)
    @commands.register(mode=Modes.MANIPULATE)
    def contrast(self, value: argtypes.ManipulateLevel = 0, count: int = 0):
        """Manipulate contrast.

        **syntax:** ``:contrast [value]``

        If neither value nor count are given, set contrast to the current
        manipulation. Otherwise set contrast to the given value.

        positional arguments:
            * ``value``: Set the contrast to value. Range: -127 to 127.

        **count:** Set contrast to [count].
        """
        value = count if count else value
        self._update_manipulation("contrast", value)

    @keybindings.add("K", "increase 10", mode=Modes.MANIPULATE)
    @keybindings.add("k", "increase 1", mode=Modes.MANIPULATE)
    @commands.register(mode=Modes.MANIPULATE)
    def increase(self, value: int, count: int = 1):
        """Increase the value of the current manipulation.

        **syntax:** ``:increase value``

        positional arguments:
            * ``value``: The value to increase by.

        **count:** multiplier
        """
        value = self.manipulations[self._current] + value * count
        self._update_manipulation(self._current, value)

    @keybindings.add("J", "decrease 10", mode=Modes.MANIPULATE)
    @keybindings.add("j", "decrease 1", mode=Modes.MANIPULATE)
    @commands.register(mode=Modes.MANIPULATE)
    def decrease(self, value: int, count: int = 1):
        """Decrease the value of the current manipulation.

        **syntax:** ``:decrease value``

        positional arguments:
            * ``value``: The value to decrease by.

        **count:** multiplier
        """
        value = self.manipulations[self._current] - value * count
        self._update_manipulation(self._current, value)

    @keybindings.add("gg", "set -127", mode=Modes.MANIPULATE)
    @keybindings.add("G", "set 127", mode=Modes.MANIPULATE)
    @commands.register(mode=Modes.MANIPULATE)
    def set(self, value: int, count: int = 0):
        """Set the value of the current manipulation.

        **syntax:** ``:set value``

        positional arguments:
            * ``value``: Value to set the manipulation to. Range -127 to 127.

        **count:** Set the manipulation to [count] instead.
        """
        value = count if count else value
        self._update_manipulation(self._current, value)

    def _update_manipulation(self, name, value):
        """Update the value of one manipulation.

        Args:
            name: Name of the manipulation to update.
            value: Integer value to set the manipulation to.
        """
        self._current = name
        self.focused.emit(name)
        if value is not None:
            value = clamp(value, -127, 127)
            self.edited.emit(name, value)
            self.manipulations[name] = value
            self.thread_id += 1
            runnable = ManipulateRunner(self, self.thread_id)
            self.pool.start(runnable)

    @statusbar.module("{processing}")
    def _processing_indicator(self):
        """Print ``processing...`` if manipulations are running."""
        if self.pool.activeThreadCount():
            return "processing..."
        return ""

    def unmanipulated(self):
        """Return unmanipulated image data for ManipulateRunner."""
        return self._handler.transformed.toImage()

    @pyqtSlot()
    def _on_quit(self):
        """Finish thread pool on quit."""
        self.pool.clear()
        self.pool.waitForDone()


def instance():
    return objreg.get(Manipulator)


class ManipulateRunner(QRunnable):
    """Apply manipulations in an extra thread.

    Args:
        _manipulator: Manipulator class to interact with.
        _id: Integer id of this thread.
    """

    def __init__(self, manipulator, thread_id):
        super().__init__()
        self._manipulator = manipulator
        self._id = thread_id

    def run(self):
        """Apply manipulations."""
        # Retrieve current unmanipulated image
        image = self._manipulator.unmanipulated()
        # Wait for a bit in case user holds down key
        time.sleep(WAIT_TIME)
        if self._id != self._manipulator.thread_id:
            return
        # Convert original pixmap to python bytes
        bits = image.constBits()
        bits.setsize(image.byteCount())
        data = bytes(bits)
        # Run C function
        bri = self._manipulator.manipulations["brightness"] / 255
        con = self._manipulator.manipulations["contrast"] / 255
        self._manipulator.data = \
            _c_manipulate.manipulate(data, image.hasAlphaChannel(), bri, con)
        # Convert bytes to QPixmap and set the manipulator pixmap
        new_image = QImage(self._manipulator.data, image.width(),
                           image.height(), image.bytesPerLine(),
                           image.format())
        self._manipulator.set_pixmap(QPixmap(new_image))
