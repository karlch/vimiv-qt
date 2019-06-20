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

    # One of the values is a property and overall none of this is very complicated
    # pylint: disable=too-many-instance-attributes
    def __init__(self, name, value=0, lower=-127, upper=127):
        self.bar = QProgressBar()
        self.bar.setMinimum(lower)
        self.bar.setMaximum(upper)
        self.bar.setFormat("%v")

        self.label = QLabel(name)

        self.name = name
        self.limits = collections.namedtuple("Limits", ["lower", "upper"])(lower, upper)

        self.value = self._value = self._init_value = value
        self.changed = False

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
        self.changed = True

    def reset(self):
        """Reset value and bar to default."""
        self.value = self._init_value
        self.bar.setValue(self._init_value)
        self.changed = False

    def focus(self):
        fg = styles.get("manipulate.focused.fg")
        self.label.setText(utils.wrap_style_span(f"color: {fg}", self.name))

    def unfocus(self):
        fg = styles.get("manipulate.fg")
        self.label.setText(utils.wrap_style_span(f"color: {fg}", self.name))

    def __repr__(self):
        return f"{self.__class__.__qualname__}(name={self.name}, value={self.value})"


class Manipulations(list):
    """Class of all manipulations.

    Each group consists of manipulations that are applied together in one function, e.g.
    brightness and contrast. Iterating over the class yields the individual
    manipulations.

    Applying the manipulations can be done individually using the apply method and all
    at once using the apply_all method.
    """

    def __init__(self):
        self.brightness = Manipulation("brightness")
        self.contrast = Manipulation("contrast")

        group = collections.namedtuple("ManipulationGroup", ["title", "manipulations"])
        self.groups = (
            group("Brightness / Contrast", (self.brightness, self.contrast)),
        )

        self.extend(utils.flatten([group.manipulations for group in self.groups]))

    def group(self, manipulation):
        """Return the group of the manipulation."""
        for group in self.groups:
            if manipulation in group.manipulations:
                return group
        raise KeyError(f"Unknown manipulation {manipulation}")

    def groupindex(self, manipulation):
        """Retrun the index of the group of which the manipulation is part."""
        for i, group in enumerate(self.groups):
            if manipulation in group.manipulations:
                return i
        raise KeyError(f"Unknown manipulation {manipulation}")

    def apply_all(self, pixmap):
        """Apply all manipulations iteratively to pixmap."""
        for group in self.groups:
            pixmap, data = self.apply(pixmap, group.manipulations[0])
        return pixmap, data

    def apply(self, pixmap, manipulation):
        """Manipulate a pixmap according to the manipulation.

        Args:
            pixmap: The QPixmap to manipulate.
            manipulation: The manipulation to apply.
        Returns:
            The manipulated pixmap.
            The underlying data to store
        """
        image = pixmap.toImage()
        # Convert original pixmap to python bytes
        bits = image.constBits()
        bits.setsize(image.byteCount())
        data = bytes(bits)
        # Apply c-function corresponding to manipulation
        if manipulation in (self.brightness, self.contrast):
            data = self._apply_bc(data, image.hasAlphaChannel())
        image = QImage(
            data, image.width(), image.height(), image.bytesPerLine(), image.format()
        )
        return QPixmap(image), data

    def _apply_bc(self, data, has_alpha):
        """Manipulate brightness and contrast."""
        if self.brightness.changed or self.contrast.changed:
            return _c_manipulate.brightness_contrast(
                data, has_alpha, self.brightness.value / 255, self.contrast.value / 255
            )
        return data


class Manipulator(QObject):
    """Apply manipulations to an image.

    Provides commands for more complex manipulations like brightness and
    contrast.

    Attributes:
        manipulations: Manipulations class storing all manipulations.
        thread_id: ID of the current manipulation thread.
        data: bytes of the edited pixmap. Must be stored as the QPixmap is
            generated directly from the bytes and needs them to stay in memory.

        _handler: ImageFileHandler used to retrieve and set updated files.
        _current: Currently edited manipulation.
        _pixmap: Manipulated pixmap.
    """

    pool = QThreadPool()

    updated = pyqtSignal(QPixmap)
    group_focused = pyqtSignal(int)

    @api.objreg.register
    def __init__(self, handler):
        super().__init__()
        self._handler = handler
        self.thread_id = 0
        self.data = None
        self._pixmap = None
        self.manipulations = Manipulations()
        self._current = self.manipulations.brightness  # Default manipulation

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
        pixmap, self.data = self.manipulations.apply_all(self._handler.transformed)
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

    @api.keybindings.register("n", "next", mode=api.modes.MANIPULATE)
    @api.commands.register(mode=api.modes.MANIPULATE)
    def next(self, count: int = 1):
        """Focus the next manipulation in the current tab.

        **count:** multiplier
        """
        self._navigate_in_tab(count)

    @api.keybindings.register("p", "prev", mode=api.modes.MANIPULATE)
    @api.commands.register(mode=api.modes.MANIPULATE)
    def prev(self, count: int = 1):
        """Focus the previous manipulation in the current tab.

        **count:** multiplier
        """
        self._navigate_in_tab(-count)

    def _navigate_in_tab(self, count):
        """Navigate by count steps in current tab."""
        group = self.manipulations.group(self._current)
        index = (group.manipulations.index(self._current) + count) % len(
            group.manipulations
        )
        self._focus(group.manipulations[index])

    @api.keybindings.register("<tab>", "tabnext", mode=api.modes.MANIPULATE)
    @api.commands.register(mode=api.modes.MANIPULATE)
    def tabnext(self, count: int = 1):
        """Focus the next manipulation tab.

        **count:** multiplier
        """
        self._navigate_tab(count)

    @api.keybindings.register("<shift><tab>", "tabprev", mode=api.modes.MANIPULATE)
    @api.commands.register(mode=api.modes.MANIPULATE)
    def tabprev(self, count: int = 1):
        """Focus the previous manipulation tab.

        **count:** multiplier
        """
        self._navigate_tab(-count)

    def _navigate_tab(self, count):
        """Navigate by count steps in tabs."""
        current_index = self.manipulations.groupindex(self._current)
        next_index = (current_index + count) % len(self.manipulations.groups)
        manipulation = self.manipulations.groups[next_index].manipulations[0]
        self._focus(manipulation)

    def reset(self):
        """Reset manipulations to default."""
        for manipulation in self.manipulations:
            manipulation.reset()

    def _manipulation_command(self, manipulation, value, count):
        """Run a manipulation command.

        This focuses the manipulation and if a new value is passed applies it to the
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
        runnable = ManipulateRunner(self, self.thread_id, self._pixmap, manipulation)
        self.pool.start(runnable)

    def _focus(self, focused_manipulation: Manipulation):
        """Focus the manipulation and unfocus all others."""
        self._current = focused_manipulation
        focused_manipulation.focus()
        for manipulation in self.manipulations:
            if manipulation != focused_manipulation:
                manipulation.unfocus()
        self.group_focused.emit(self.manipulations.groupindex(focused_manipulation))

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

    def __init__(self, manipulator, thread_id, pixmap, manipulation):
        super().__init__()
        self._manipulator = manipulator
        self._id = thread_id
        self._pixmap = pixmap
        self._manipulation = manipulation

    def run(self):
        """Apply manipulations."""
        # Wait for a bit in case user holds down key
        time.sleep(WAIT_TIME)
        if self._id != self._manipulator.thread_id:
            return
        # Apply manipulations to pixmap
        pixmap, self._manipulator.data = self._manipulator.manipulations.apply(
            self._pixmap, self._manipulation
        )
        # Update
        self._manipulator.updated.emit(pixmap)
        api.status.update()
