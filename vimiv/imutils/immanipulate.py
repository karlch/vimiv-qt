# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""*immanipulate - more complex image manipulations like brightness and contrast*.

The module includes classes in a hierarchical structure where each following class
includes components of the previous class in the hierarchy.

#. ``Manipulation`` stores a single manipulation such as brightness.
#. ``ManipulationGroup`` stores manipulations that are applied together such as
   brightness and contrast.
#. ``Manipulations`` stores all manipulation groups and provides commands to apply them.
#. ``Manipulator`` stores the manipulations class and interfaces it with the
   application.

.. _adding_new_manipulation:

Adding new manipulations is done by implementing a new :class:`ManipulationGroup` and
adding it to the ``Manipulations``.
"""

import abc
import copy
import time
import weakref
from typing import Optional, NamedTuple, List

from PyQt5.QtCore import QObject, pyqtSignal, Qt, QSignalBlocker, QTimer
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QLabel, QApplication

from vimiv import api, utils, widgets
from vimiv.config import styles

# mypy cannot read the C extension
from vimiv.imutils import _c_manipulate  # type: ignore


WAIT_TIME = 0.3
_logger = utils.log.module_logger(__name__)


class Limits(NamedTuple):
    """Storage class for manipulation value limits."""

    lower: int
    upper: int


class Manipulation(QObject):
    """Storage class for one manipulation.

    The manipulation is associated with the displayed label and slider, the value can be
    changed and it can be (un-)focused.

    Attributes:
        slider: QSlider to show the current value.
        label: QLabel displaying the name of the manipulation.
        limits: Namedtuple of lower and upper limit for value.
        name: Name identifier of the manipulation (e.g. brightness).

        _init_value: Initial value used for resetting.
    """

    updated = pyqtSignal(object)

    def __init__(
        self,
        name: str,
        value: int = 0,
        lower: int = -127,
        upper: int = 127,
        init_value: int = 0,
    ):
        super().__init__()
        self.slider = widgets.SliderWithValue(
            "{manipulate.slider.left}",
            "{manipulate.slider.handle}",
            "{manipulate.slider.right}",
            Qt.Horizontal,
        )
        self.slider.setMinimum(lower)
        self.slider.setMaximum(upper)
        self.slider.setTracking(False)

        self.label = QLabel(name)

        self.limits = Limits(lower, upper)
        self.name = name

        self.value, self._init_value = value, init_value

        self.slider.valueChanged.connect(self._on_value_changed)  # type: ignore

    @property
    def value(self) -> int:
        """Current value of the manipulation.

        Wraps slider.value() and slider.setValue() for convenience.
        """
        return self.slider.value()

    @value.setter
    def value(self, value: int) -> None:
        self.slider.setValue(value)

    @property
    def changed(self) -> bool:
        """True if the manipulation was changed."""
        return self.value != self._init_value

    def reset(self):
        """Reset value back to initial value."""
        with QSignalBlocker(self):  # We do not want to re-run manipulate on reset
            self.value = self._init_value

    def focus(self):
        fg = styles.get("manipulate.focused.fg")
        self.label.setText(utils.wrap_style_span(f"color: {fg}", self.name))

    def unfocus(self):
        fg = styles.get("manipulate.fg")
        self.label.setText(utils.wrap_style_span(f"color: {fg}", self.name))

    def _on_value_changed(self, _value):
        """Emit the updated signal when the slider value has changed."""
        self.updated.emit(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(name={self.name}, value={self.value})"

    def __copy__(self) -> "Manipulation":
        return Manipulation(self.name, self.value, *self.limits)


class ManipulationGroup(abc.ABC):
    """Base class for a group of manipulations associated to one manipulation tab.

    The group stores the individual manipulations, associates them to a manipulate
    function and provides a title.

    To implement a new manipulation group:

    * Inherit from this base class and define an appropriate constructor
    * Define the :func:`title` property
    * Implement the abstract method :func:`_apply`

    Attributes:
        manipulations: Tuple of individual manipulations.

        _data: bytes of the last change from this group. Must be stored as the QPixmap
            is generated directly from the bytes and needs them to stay in memory.
    """

    def __init__(self, *manipulations: Manipulation):
        self.manipulations = manipulations
        self._data = bytes()

    def __iter__(self):
        yield from self.manipulations

    def __copy__(self):
        """Copy manipulations to keep the current values upon copy."""
        manipulations = (copy.copy(manipulation) for manipulation in self.manipulations)
        return type(self)(*manipulations)

    def __repr__(self):
        return f"{self.__class__.__qualname__}(title={self.title})"

    @property
    def changed(self) -> bool:
        """True if any manipulation has been changed."""
        for manipulation in self.manipulations:
            if manipulation.changed:
                return True
        return False

    def apply(self, data: bytes) -> bytes:
        """Apply manipulation function to image data if any manipulation changed.

        Wraps the abstract :func:`_apply` with a common setup and finalize part.
        """
        if not self.changed:
            return data
        self._data = self._apply(data, *self.manipulations)
        return self._data

    @property
    @abc.abstractmethod
    def title(self):
        """Title of the manipulation group as referred to in its tab.

        Must be defined by the child class.
        """

    @abc.abstractmethod
    def _apply(self, data: bytes, *manipulations: Manipulation) -> bytes:
        """Apply all manipulations of this group.

        Takes the image data as raw bytes, applies the changes according the current
        manipulation values and returns the updated bytes. In general this is associated
        with a call to a function implemented in the C-extension which manipulates the
        raw data.

        Must be implemented by the child class.

        Args:
            data: The raw image data in bytes to manipulate.
        Returns:
            The updated raw image data in bytes.
        """


class BriConGroup(ManipulationGroup):
    """Manipulation group for brightness and contrast."""

    def __init__(self, *manipulations: Manipulation):
        if manipulations:  # For copy construction
            super().__init__(*manipulations)
        else:  # Default constructor
            super().__init__(Manipulation("brightness"), Manipulation("contrast"))

    @property
    def title(self):
        return "Bri | Con"

    def _apply(self, data, brightness, contrast):
        return _c_manipulate.brightness_contrast(
            data, brightness.value / 255, contrast.value / 255
        )


class HSLGroup(ManipulationGroup):
    """Manipulation group for hue, saturation and lightness."""

    def __init__(self, *manipulations):
        if manipulations:  # For copy construction
            super().__init__(*manipulations)
        else:  # Default constructor
            super().__init__(
                Manipulation("hue", lower=-180, upper=180),
                Manipulation("saturation", lower=-100, upper=100),
                Manipulation("lightness", lower=-100, upper=100),
            )

    @property
    def title(self):
        return "Hue | Sat | Light"

    def _apply(self, data, hue, saturation, lightness):
        return _c_manipulate.hue_saturation_lightness(
            data,
            hue.value,
            saturation.value / saturation.limits.upper,
            lightness.value / lightness.limits.upper,
        )


class ManipulationChange(NamedTuple):
    """Storage class for a manipulation change.

    Attributes:
        pixmap: The manipulated pixmap.
        manipulations: The manipulation group associated to these changes.
    """

    pixmap: QPixmap
    manipulations: ManipulationGroup


class Manipulations(list):
    """Class combining all manipulation groups.

    Each group consists of manipulations that are applied together in one function, e.g.
    brightness and contrast. The class is a list containing all individual
    manipulations.

    Applying manipulations can be done for a single manipulation using apply and for
    multiple groups using apply_groups.

    Attributes:
        groups: Tuple of all manipulation groups.
    """

    def __init__(self):
        self.groups = (BriConGroup(), HSLGroup())
        super().__init__(utils.flatten([group.manipulations for group in self.groups]))

    def group(self, manipulation: Manipulation) -> ManipulationGroup:
        """Return the group of the manipulation."""
        for group in self.groups:
            if manipulation in group.manipulations:
                return group
        raise KeyError(f"Unknown manipulation {manipulation}")

    def apply_groups(self, pixmap: QPixmap, *groups: ManipulationGroup) -> QPixmap:
        """Manipulate pixmap according all manipulations in groups.

        Args:
            pixmap: The QPixmap to manipulate.
            groups: Manipulation groups containing all manipulations to apply in series.
        Returns:
            The manipulated pixmap.
        """
        _logger.debug("Manipulate: applying %d groups", len(groups))
        # Convert original pixmap to python bytes
        image = pixmap.toImage()
        bits = image.constBits()
        bits.setsize(image.byteCount())
        data = bits.asstring()
        # Apply changes on the byte-level
        for group in groups:
            data = self._apply_group(group, data)
        # Convert updated bytes back to pixmap
        image = QImage(
            data, image.width(), image.height(), image.bytesPerLine(), image.format()
        )
        return QPixmap(image)

    def apply(self, pixmap: QPixmap, manipulation: Manipulation) -> QPixmap:
        """Manipulate pixmap according to single manipulation."""
        return self.apply_groups(pixmap, self.group(manipulation))

    def _apply_group(self, group: Optional[ManipulationGroup], data: bytes) -> bytes:
        """Apply manipulations of a single group to image."""
        if group is None:
            return data
        _logger.debug("Manipulate: applying group %r", group)
        return group.apply(data)


class Manipulator(QObject):
    """Handler class to apply manipulations to the current image.

    Provides commands for more complex manipulations like brightness and
    contrast. Acts as binding link between the manipulations and the gui interface.

    Class Attributes:
        pool: QThreadPool to apply manipulations in parallel.

    Attributes:
        manipulations: Manipulations class storing all manipulations.

        _changes: List of applied ManipulationChanges.
        _current: Currently editedfocused manipulation.
        _handler: weak reference to ImageFileHandler used to retrieve/set updated files.
        _pixmap: Pixmap to apply current manipulation to.
        _manipulated: Pixmap after applying current manipulation.
        _thread_id: ID of the current manipulation thread.

    Signals:
        updated: Emitted when the manipulated pixmap was changed.
            arg1: The new manipulated QPixmap.
    """

    pool = utils.Pool.get(globalinstance=False)
    pool.setMaxThreadCount(1)  # Only one manipulation is run in parallel

    updated = pyqtSignal(QPixmap)

    @api.objreg.register
    def __init__(self, handler):
        super().__init__()

        self.manipulations = Manipulations()

        self._changes: List[ManipulationChange] = []
        self._current = self.manipulations[0]  # Default manipulation
        self._current.focus()
        self._handler = weakref.ref(handler)
        self._pixmap = self._manipulated = None
        self._thread_id = 0

        api.modes.MANIPULATE.entered.connect(self._on_enter)
        api.modes.MANIPULATE.left.connect(self.reset)
        self.updated.connect(self._on_updated)
        for manipulation in self.manipulations:
            manipulation.updated.connect(self._apply_manipulation)

    @property
    def changed(self):
        """True if anything was edited."""
        for manipulation in self.manipulations:
            if manipulation.changed:
                return True
        return False

    @api.keybindings.register("<return>", "accept", mode=api.modes.MANIPULATE)
    @api.commands.register(mode=api.modes.MANIPULATE)
    def accept(self):
        """Leave manipulate applying the changes to file."""
        if self.changed:  # Only run the expensive part when needed
            self._save_changes()  # For the current manipulation
            pixmap = self.manipulations.apply_groups(
                self._handler().transformed,
                *[change.manipulations for change in self._changes],
            )  # Apply all changes to the full-scale pixmap
            self._handler().current = pixmap
            self._handler().write_pixmap(pixmap, parallel=False)
        api.modes.MANIPULATE.leave()

    @api.keybindings.register("<escape>", "discard", mode=api.modes.MANIPULATE)
    @api.commands.register(mode=api.modes.MANIPULATE)
    def discard(self):
        """Discard any changes and leave manipulate."""
        api.modes.MANIPULATE.leave()
        self.reset()
        self._handler().current = self._handler().transformed

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

    def reset(self):
        """Reset manipulations to default."""
        for manipulation in self.manipulations:
            manipulation.reset()
        self._pixmap = self._manipulated = None
        self._changes.clear()

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

    @api.keybindings.register("gg", "goto -127", mode=api.modes.MANIPULATE)
    @api.keybindings.register("G", "goto 127", mode=api.modes.MANIPULATE)
    @api.commands.register(mode=api.modes.MANIPULATE)
    def goto(self, value: int, count: Optional[int] = None):
        """Set the value of the current manipulation.

        **syntax:** ``:goto value``

        positional arguments:
            * ``value``: Value to set the manipulation to.

        **count:** Set the manipulation to [count] instead.
        """
        self._current.value = count if count is not None else value

    def _apply_manipulation(self, manipulation: Manipulation):
        """Apply changes to displayed image according to an updated manipulation."""
        self._focus(manipulation)
        self.pool.clear()
        self._thread_id += 1
        self._run_manipulation_thread(self._thread_id, manipulation)
        api.status.update("manipulate processing")

    @utils.asyncfunc(pool=pool)
    def _run_manipulation_thread(self, thread_id, manipulation):
        """Run manipulation in the thread pool.

        Some time is waited before running the manipulation, to keep the number of
        manipulations done reasonable in case of dragging the slider or keeping a key
        repeat.
        """
        time.sleep(WAIT_TIME)
        # self._pixmap is None if manipulate mode has been left
        if self._pixmap is not None and thread_id == self._thread_id:
            pixmap = self.manipulations.apply(self._pixmap, manipulation)
            self.updated.emit(pixmap)

    @utils.slot
    def focus_group_index(self, index: int):
        """Focus new manipulation group by index."""
        self._save_changes()
        group = self.manipulations.groups[index]
        self._focus(group.manipulations[0])

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

    def _on_enter(self):
        """Create manipulate pixmap when entering manipulate mode.

        As the pixmap is only displayed in the bottom right, scaling it to be half the
        total screen width / height is always sufficiently large. This avoids working
        with the large original when it is not needed.
        """
        if not self._handler().editable:
            api.modes.MANIPULATE.leave()
            QTimer.singleShot(
                0, lambda: utils.log.error("File format does not support manipulate")
            )
            return
        screen_geometry = QApplication.desktop().screenGeometry()
        self._pixmap = self._handler().transformed.scaled(
            screen_geometry.width(),
            screen_geometry.height(),
            aspectRatioMode=Qt.KeepAspectRatio,
            transformMode=Qt.SmoothTransformation,
        )
        self.updated.emit(self._pixmap)

    def _on_updated(self, pixmap):
        """Set manipulated and update status when pixmap was updated.

        This is done with signal handling as the ManipulateRunner runs in another
        thread and finally emits the signal.
        """
        self._manipulated = pixmap
        api.status.update("manipulate pixmap updated")

    def _save_changes(self):
        """Save changes according to the current manipulation."""
        if self._manipulated is None:  # Nothing changed
            return
        current_group = self.manipulations.group(self._current)
        self._changes.append(
            ManipulationChange(self._manipulated, copy.copy(current_group))
        )
        # Reset to avoid double application of the changes
        for manipulation in current_group:
            manipulation.reset()
        self._pixmap, self._manipulated = self._manipulated, None
