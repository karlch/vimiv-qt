# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Perform more complex manipulations like brightness and contrast."""

import collections
import time
from typing import Optional

from PyQt5.QtCore import (
    QRunnable,
    QThreadPool,
    QObject,
    QCoreApplication,
    pyqtSignal,
    Qt,
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QProgressBar, QLabel, QApplication

from vimiv import api, utils
from vimiv.config import styles
from vimiv.imutils import (  # type: ignore # pylint: disable=no-name-in-module
    _c_manipulate,
)
from vimiv.utils import clamp


WAIT_TIME = 0.3


class Manipulation:
    """Storage class for one manipulation.

    Attributes:
        name: Name identifier of the manipulation (e.g. brightness).
        limits: Namedtuple of lower and upper limit for value.

        _init_value: Initial value of the manipulation to allow resetting.
        _value: Current value of the manipulation.
    """

    def __init__(self, name, value=0, lower=-127, upper=127):
        self.bar = QProgressBar()
        self.bar.setMinimum(lower)
        self.bar.setMaximum(upper)
        self.bar.setFormat("%v")

        self.label = QLabel(name)

        self.name = name
        self.limits = collections.namedtuple("Limits", ["lower", "upper"])(lower, upper)

        self.value = self._value = self._init_value = value

    @property
    def value(self):
        """Current value of the manipulation.

        Upon setting it is guaranteed that the value stays within the lower and upper
        limit and the bar value is updated.
        """
        return self._value

    @value.setter
    def value(self, value):
        self._value = clamp(value, self.limits.lower, self.limits.upper)
        self.bar.setValue(self._value)

    def reset(self):
        self.value = self._init_value
        self.bar.setValue(self._init_value)

    def focus(self):
        fg = styles.get("manipulate.focused.fg")
        self.label.setText(utils.wrap_style_span(f"color: {fg}", self.name))

    def unfocus(self):
        fg = styles.get("manipulate.fg")
        self.label.setText(utils.wrap_style_span(f"color: {fg}", self.name))

    def __repr__(self):
        return f"{self.__class__.__qualname__}(name={self.name}, value={self.value})"


class Manipulator(QObject):
    """Apply manipulations to an image.

    Provides commands for more complex manipulations like brightness and
    contrast.

    Attributes:
        manipulations: Namedtuple storing all manipulations.
        thread_id: ID of the current manipulation thread.
        data: bytes of the edited pixmap. Must be stored as the QPixmap is
            generated directly from the bytes and needs them to stay in memory.

        _handler: ImageFileHandler used to retrieve and set updated files.
        _current: Currently edited manipulation.
        _pixmap: Manipulated pixmap.
    """

    pool = QThreadPool()

    updated = pyqtSignal(QPixmap)

    @api.objreg.register
    def __init__(self, handler):
        super().__init__()
        self._handler = handler
        self.thread_id = 0
        self.data = None
        self._pixmap = None
        self.manipulations = collections.namedtuple(
            "Manipulations", ["Brightness", "Contrast"]
        )(Manipulation("brightness"), Manipulation("contrast"))
        self._current = self.manipulations.Brightness  # Default manipulation

        self._current.focus()

        QCoreApplication.instance().aboutToQuit.connect(self._on_quit)
        api.modes.MANIPULATE.entered.connect(self._on_enter)
        api.modes.MANIPULATE.left.connect(self._on_leave)

    @property
    def changed(self):
        """True if anything was edited."""
        for manipulation in self.manipulations:
            if manipulation.value != 0:
                return True
        return False

    @api.keybindings.register("<return>", "accept", mode=api.modes.MANIPULATE)
    @api.commands.register(mode=api.modes.MANIPULATE)
    def accept(self):
        """Leave manipulate applying the changes to file."""
        pixmap, self.data = manipulate_pixmap(
            self._handler.transformed, self.manipulations
        )
        self._handler.current = pixmap
        self._handler.write_pixmap(pixmap, parallel=False)
        api.modes.MANIPULATE.leave()

    @api.keybindings.register("<escape>", "discard", mode=api.modes.MANIPULATE)
    @api.commands.register(mode=api.modes.MANIPULATE)
    def discard(self):
        """Discard any changes and leave manipulate."""
        api.modes.MANIPULATE.leave()
        self.reset()
        self._handler.current = self._handler.transformed

    def reset(self):
        """Reset manipulations to default."""
        for manipulation in self.manipulations:
            manipulation.reset()

    @api.keybindings.register("b", "brightness", mode=api.modes.MANIPULATE)
    @api.commands.register(mode=api.modes.MANIPULATE)
    def brightness(self, value: int = None, count: Optional[int] = None):
        """Manipulate brightness.

        **syntax:** ``:brightness [value]``

        If neither value nor count are given, set brightness to the current
        manipulation. Otherwise set brightness to the given value.

        positional arguments:
            * ``value``: Set the brightness to value. Range: -127 to 127.

        **count:** Set brightness to [count].
        """
        self._manipulation_command(self.manipulations.Brightness, value, count)

    @api.keybindings.register("c", "contrast", mode=api.modes.MANIPULATE)
    @api.commands.register(mode=api.modes.MANIPULATE)
    def contrast(self, value: int = None, count: Optional[int] = None):
        """Manipulate contrast.

        **syntax:** ``:contrast [value]``

        If neither value nor count are given, set contrast to the current
        manipulation. Otherwise set contrast to the given value.

        positional arguments:
            * ``value``: Set the contrast to value. Range: -127 to 127.

        **count:** Set contrast to [count].
        """
        self._manipulation_command(self.manipulations.Contrast, value, count)

    def _manipulation_command(self, manipulation, value, count):
        """Run a manipulation command.

        This focused the manipulation and if a new value is passed applies it to the
        manipulate pixmap.

        Args:
            manipulation: The manipulation to update.
            value: Value to set the manipulation to if any.
            count: Count passed if any.
        """
        self._focus(manipulation)
        if count is None and value is None:  # Only focused
            return
        try:
            manipulation.value = int(count) if count is not None else value
        except ValueError as e:  # Invalid int value given
            raise api.commands.CommandError(str(e))
        self._apply_manipulation(manipulation)

    @api.keybindings.register(("K", "L"), "increase 10", mode=api.modes.MANIPULATE)
    @api.keybindings.register(("k", "l"), "increase 1", mode=api.modes.MANIPULATE)
    @api.commands.register(mode=api.modes.MANIPULATE)
    def increase(self, value: int, count: int = 1):
        """Increase the value of the current manipulation.

        **syntax:** ``:increase value``

        positional arguments:
            * ``value``: The value to increase by.

        **count:** multiplier
        """
        self._current.value += value * count
        self._apply_manipulation(self._current)

    @api.keybindings.register(("J", "H"), "decrease 10", mode=api.modes.MANIPULATE)
    @api.keybindings.register(("j", "h"), "decrease 1", mode=api.modes.MANIPULATE)
    @api.commands.register(mode=api.modes.MANIPULATE)
    def decrease(self, value: int, count: int = 1):
        """Decrease the value of the current manipulation.

        **syntax:** ``:decrease value``

        positional arguments:
            * ``value``: The value to decrease by.

        **count:** multiplier
        """
        self._current.value -= value * count
        self._apply_manipulation(self._current)

    @api.keybindings.register("gg", "set -127", mode=api.modes.MANIPULATE)
    @api.keybindings.register("G", "set 127", mode=api.modes.MANIPULATE)
    @api.commands.register(mode=api.modes.MANIPULATE)
    def set(self, value: int, count: Optional[int] = None):
        """Set the value of the current manipulation.

        **syntax:** ``:set value``

        positional arguments:
            * ``value``: Value to set the manipulation to. Range -127 to 127.

        **count:** Set the manipulation to [count] instead.
        """
        self._current.value = count if count is not None else value
        self._apply_manipulation(self._current)

    def _apply_manipulation(self, manipulation: Manipulation):
        """Apply changes to displayed image according to an updated manipulation."""
        self.thread_id += 1
        runnable = ManipulateRunner(self, self.thread_id, self._pixmap)
        self.pool.start(runnable)

    def _focus(self, focused_manipulation: Manipulation):
        """Focus the manipulation and unfocus all others."""
        self._current = focused_manipulation
        focused_manipulation.focus()
        for manipulation in self.manipulations:
            if manipulation != focused_manipulation:
                manipulation.unfocus()

    @api.status.module("{processing}")
    def _processing_indicator(self):
        """Print ``processing...`` if manipulations are running."""
        if self.pool.activeThreadCount():
            return "processing..."
        return ""

    @utils.slot
    def _on_quit(self):
        """Finish thread pool on quit."""
        self.pool.clear()
        self.pool.waitForDone(5000)  # Kill manipulate after 5s

    def _on_enter(self):
        """Create manipulate pixmap when entering manipulate mode.

        As the pixmap is only displayed in the bottom right, scaling it to be half the
        total screen width / height is always sufficiently large. This avoids working
        with the large original when it is not needed.
        """
        if self._handler.transformed is None:  # No image to display
            return
        screen_geometry = QApplication.desktop().screenGeometry()
        self._pixmap = self._handler.transformed.scaled(
            screen_geometry.width(),
            screen_geometry.height(),
            aspectRatioMode=Qt.KeepAspectRatio,
            transformMode=Qt.SmoothTransformation,
        )
        self.updated.emit(self._pixmap)

    def _on_leave(self):
        self._pixmap = None


def instance():
    return api.objreg.get(Manipulator)


class ManipulateRunner(QRunnable):
    """Apply manipulations in an extra thread.

    Attributes:
        _manipulator: Manipulator class to interact with.
        _id: Integer id of this thread.
    """

    def __init__(self, manipulator, thread_id, pixmap):
        super().__init__()
        self._manipulator = manipulator
        self._id = thread_id
        self._pixmap = pixmap

    def run(self):
        """Apply manipulations."""
        # Wait for a bit in case user holds down key
        time.sleep(WAIT_TIME)
        if self._id != self._manipulator.thread_id:
            return
        # Apply manipulations to pixmap
        pixmap, self._manipulator.data = manipulate_pixmap(
            self._pixmap, self._manipulator.manipulations
        )
        # Update
        self._manipulator.updated.emit(pixmap)
        api.status.update()


def manipulate_pixmap(pixmap, manipulations):
    """Manipulate a pixmap according to manipulations.

    Args:
        pixmap: The QPixmap to manipulate.
        manipulations: Namedtuple containing all the manipulations.
    Returns:
        The manipulated pixmap.
        The underlying data to store
    """
    image = pixmap.toImage()
    # Convert original pixmap to python bytes
    bits = image.constBits()
    bits.setsize(image.byteCount())
    data = bytes(bits)
    # Run C function
    bri = manipulations.Brightness.value / 255
    con = manipulations.Contrast.value / 255
    data = _c_manipulate.manipulate(data, image.hasAlphaChannel(), bri, con)
    # Convert bytes to image
    image = QImage(
        data, image.width(), image.height(), image.bytesPerLine(), image.format()
    )
    return QPixmap(image), data
