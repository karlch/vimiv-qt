# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Perform more complex manipulations like brightness and contrast."""

import collections
import time

from PyQt5.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject
from PyQt5.QtGui import QPixmap, QImage

from vimiv.commands import commands, argtypes
from vimiv.config import keybindings
from vimiv.imutils import imsignals, _c_manipulate, imloader
from vimiv.gui import statusbar
from vimiv.modes import modehandler
from vimiv.utils import objreg, misc


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
        original: Original QPixmap to manipulate.
        pixmap: The manipulated QPixmap.
        _current: Name of the manipulation that is currently being edited.
    """

    pool = QThreadPool()
    edited = pyqtSignal(str, int)
    focused = pyqtSignal(str)

    @objreg.register("manipulator")
    def __init__(self):
        super().__init__()
        self.manipulations = collections.OrderedDict([
            ("brightness", 0),
            ("contrast", 0),
        ])
        self.thread_id = 0
        self.data = None
        self.original = None
        self.pixmap = None
        self._current = "brightness"

        imsignals.connect(self._on_pixmap_loaded, "pixmap_loaded")

    def set_pixmap(self, pixmap):
        """Set the pixmap to a newly edited version."""
        self.pixmap = pixmap
        imsignals.emit("pixmap_updated", self.pixmap)

    def changed(self):
        """Return True if anything was edited."""
        return self.manipulations != {"brightness": 0, "contrast": 0}

    @keybindings.add("<return>", "accept", mode="manipulate")
    @commands.register(instance="manipulator", mode="manipulate")
    def accept(self):
        """Apply changes to file and leave manipulate."""
        modehandler.leave("manipulate")
        if self.manipulations == {"brightness": 0, "contrast": 0}:
            return
        imloader.set_pixmap(self.pixmap)

    @keybindings.add("<escape>", "discard", mode="manipulate")
    @commands.register(instance="manipulator", mode="manipulate")
    def discard(self):
        """Discard any changes and leave manipulate."""
        modehandler.leave("manipulate")
        # Show original image
        if self.manipulations != {"brightness": 0, "contrast": 0}:
            imsignals.emit("pixmap_updated", self.original)
        self.manipulations = {
            "brightness": 0,
            "contrast": 0
        }

    @keybindings.add("b", "brightness", mode="manipulate")
    @commands.argument("value", optional=True, type=argtypes.manipulate_level)
    @commands.register(mode="manipulate", instance="manipulator", count=0)
    def brightness(self, value, count):
        """Manipulate brightness."""
        value = count if count else value
        self._update_manipulation("brightness", value)

    @keybindings.add("c", "contrast", mode="manipulate")
    @commands.argument("value", optional=True, type=argtypes.manipulate_level)
    @commands.register(mode="manipulate", instance="manipulator", count=0)
    def contrast(self, value, count):
        """Manipulate contrast."""
        value = count if count else value
        self._update_manipulation("contrast", value)

    @keybindings.add("K", "increase 10", mode="manipulate")
    @keybindings.add("k", "increase 1", mode="manipulate")
    @commands.argument("value", type=int)
    @commands.register(mode="manipulate", instance="manipulator", count=1)
    def increase(self, value, count):
        """Increase the value of the current manipulation."""
        value = self.manipulations[self._current] + value * count
        self._update_manipulation(self._current, value)

    @keybindings.add("J", "decrease 10", mode="manipulate")
    @keybindings.add("j", "decrease 1", mode="manipulate")
    @commands.argument("value", type=int)
    @commands.register(mode="manipulate", instance="manipulator", count=1)
    def decrease(self, value, count):
        """Decrease the value of the current manipulation."""
        value = self.manipulations[self._current] - value * count
        self._update_manipulation(self._current, value)

    @keybindings.add("gg", "set -127", mode="manipulate")
    @keybindings.add("G", "set 127", mode="manipulate")
    @commands.argument("value", type=int)
    @commands.register(mode="manipulate", instance="manipulator", count=0)
    def set(self, value, count):
        """Set the value of the current manipulation."""
        value = count if count else value
        self._update_manipulation(self._current, value)

    def _on_pixmap_loaded(self, pixmap):
        """Store original version of the pixmap."""
        self.original = pixmap

    def _update_manipulation(self, name, value):
        """Update the value of one manipulation.

        Args:
            name: Name of the manipulation to update.
            value: Integer value to set the manipulation to.
        """
        self._current = name
        self.focused.emit(name)
        if value is not None:
            value = misc.clamp(value, -127, 127)
            self.edited.emit(name, value)
            self.manipulations[name] = value
            self.thread_id += 1
            runnable = ManipulateRunner(self, self.thread_id)
            self.pool.start(runnable)

    @statusbar.module("{processing}", instance="manipulator")
    def _processing_indicator(self):
        if self.pool.activeThreadCount():
            return "processing..."
        return ""


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
        # Wait for a bit in case user holds down key
        time.sleep(WAIT_TIME)
        if self._id != self._manipulator.thread_id:
            return
        # Convert original pixmap to python bytes
        image = self._manipulator.original.toImage()
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
