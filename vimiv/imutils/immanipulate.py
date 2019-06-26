# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""More complex image manipulations like brightness and contrast."""

import abc
import collections
import copy
import logging
import time
from typing import Optional, NamedTuple

from PyQt5.QtCore import (
    QRunnable,
    QThreadPool,
    QObject,
    QCoreApplication,
    pyqtSignal,
    Qt,
    QSignalBlocker,
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QLabel, QApplication

from vimiv import api, utils
from vimiv.gui.widgets import SliderWithValue
from vimiv.config import styles
from vimiv.imutils import (  # type: ignore # pylint: disable=no-name-in-module
    _c_manipulate,
)


WAIT_TIME = 0.3


class Manipulation(QObject):
    """Storage class for one manipulation.

    The manipulation is associated with the displayed label and progressbar, the value
    can be changed and it can be (un-)focused.

    Attributes:
        slider: QSlider to show the current value.
        label: QLabel displaying the name of the manipulation.
        limits: Namedtuple of lower and upper limit for value.
        name: Name identifier of the manipulation (e.g. brightness).

        _init_value: Initial value used for resetting.
    """

    updated = pyqtSignal(object)

    def __init__(self, name, value=0, lower=-127, upper=127, init_value=0):
        super().__init__()
        self.slider = SliderWithValue(
            "{manipulate.slider.left}",
            "{manipulate.slider.handle}",
            "{manipulate.slider.right}",
            Qt.Horizontal,
        )
        self.slider.setMinimum(lower)
        self.slider.setMaximum(upper)
        self.slider.setTracking(False)

        self.label = QLabel(name)

        self.limits = collections.namedtuple("Limits", ["lower", "upper"])(lower, upper)
        self.name = name

        self.value, self._init_value = value, init_value

        self.slider.valueChanged.connect(lambda value: self.updated.emit(self))

    @property
    def value(self):
        """Current value of the manipulation.

        Wraps slider.value() and slider.setValue() for convenience.
        """
        return self.slider.value()

    @value.setter
    def value(self, value):
        self.slider.setValue(value)

    @property
    def changed(self):
        """True if the manipulation was changed."""
        return self.value != self._init_value

    def reset(self):
        """Reset value and bar to default."""
        with QSignalBlocker(self):  # We do not want to re-run manipulate on reset
            self.value = self._init_value

    def focus(self):
        fg = styles.get("manipulate.focused.fg")
        self.label.setText(utils.wrap_style_span(f"color: {fg}", self.name))

    def unfocus(self):
        fg = styles.get("manipulate.fg")
        self.label.setText(utils.wrap_style_span(f"color: {fg}", self.name))

    def __repr__(self):
        return f"{self.__class__.__qualname__}(name={self.name}, value={self.value})"

    def __copy__(self):
        return Manipulation(self.name, self.value, *self.limits)


class ManipulationGroup(abc.ABC):
    """Group of manipulations associated to one manipulation tab.

    The group stores the individual manipulations, associates them to a manipulate C
    function and provides a title.

    Attributes:
        manipulations: Tuple of individual manipulations.
    """

    def __init__(self, *manipulations: Manipulation):
        self.manipulations = manipulations

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
        """True if any manipulation changed."""
        for manipulation in self.manipulations:
            if manipulation.changed:
                return True
        return False

    def apply(self, data: bytes) -> bytes:
        """Apply manipulation function to image data if any manipulation changed."""
        if not self.changed:
            return data
        return self._apply(data, *self.manipulations)

    @abc.abstractproperty
    def title(self):
        """Title of the manipulation group as referred to in its tab."""

    @abc.abstractmethod
    def _apply(self, data: bytes, *manipulations: Manipulation):
        """Apply all manipulations of this group.

        Must be implemented by the child class.
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
    brightness and contrast. Iterating over the class yields the individual
    manipulations.

    Applying manipulations can be done for a single manipulation using apply and for
    multiple groups using apply_groups.

    Attributes:
        groups: Tuple of all manipulation groups.
        data: bytes of the edited pixmap. Must be stored as the QPixmap is
            generated directly from the bytes and needs them to stay in memory.
    """

    def __init__(self):
        self.groups = (BriConGroup(), HSLGroup())
        self.data = None
        super().__init__(utils.flatten([group.manipulations for group in self.groups]))

    def group(self, manipulation: Manipulation) -> ManipulationGroup:
        """Return the group of the manipulation."""
        for group in self.groups:
            if manipulation in group.manipulations:
                return group
        raise KeyError(f"Unknown manipulation {manipulation}")

    def groupindex(self, manipulation: Manipulation) -> int:
        """Return the index of the group of which the manipulation is part."""
        for i, group in enumerate(self.groups):
            if manipulation in group.manipulations:
                return i
        raise KeyError(f"Unknown manipulation {manipulation}")

    def apply_groups(self, pixmap: QPixmap, *groups: ManipulationGroup) -> QPixmap:
        """Manipulate pixmap according all manipulations in groups.

        Args:
            pixmap: The QPixmap to manipulate.
            groups: Manipulation groups containing all manipulations to apply in series.
        Returns:
            The manipulated pixmap.
        """
        logging.debug("Manipulate: applying %d groups", len(groups))
        image = pixmap.toImage()
        # Convert original pixmap to python bytes
        bits = image.constBits()
        bits.setsize(image.byteCount())
        self.data = bytes(bits)
        for group in groups:
            image = self._apply_group(group, image)
        return QPixmap(image)

    def apply(self, pixmap: QPixmap, manipulation: Manipulation) -> QPixmap:
        """Manipulate pixmap according to single manipulation."""
        return self.apply_groups(pixmap, self.group(manipulation))

    def _apply_group(self, group: Optional[ManipulationGroup], image: QImage) -> QImage:
        """Apply manipulations of a single group to image."""
        if group is None:
            return image
        logging.debug("Manipulate: applying group %r", group)
        self.data = group.apply(self.data)
        return QImage(
            self.data,
            image.width(),
            image.height(),
            image.bytesPerLine(),
            image.format(),
        )


class Manipulator(QObject):
    """Handler class to apply manipulations to the current image.

    Provides commands for more complex manipulations like brightness and
    contrast. Acts as binding link between the manipulations and the gui interface.

    Attributes:
        manipulations: Manipulations class storing all manipulations.
        thread_id: ID of the current manipulation thread.

        _changes: List of applied ManipulationChanges.
        _current: Currently editedfocused manipulation.
        _handler: ImageFileHandler used to retrieve and set updated files.
        _pixmap: Pixmap to apply current manipulation to.
        _manipulated: Pixmap after applying current manipulation.
    """

    pool = QThreadPool()

    updated = pyqtSignal(QPixmap)

    @api.objreg.register
    def __init__(self, handler):
        super().__init__()

        self.manipulations = Manipulations()
        self.thread_id = 0

        self._changes = []
        self._current = self.manipulations[0]  # Default manipulation
        self._current.focus()
        self._handler = handler
        self._pixmap = self._manipulated = None

        QCoreApplication.instance().aboutToQuit.connect(self._on_quit)
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
        self._save_changes()  # For the current manipulation
        pixmap = self.manipulations.apply_groups(
            self._handler.transformed,
            *[change.manipulations for change in self._changes],
        )  # Apply all changes to the full-scale pixmap
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

    def reset(self):
        """Reset manipulations to default."""
        for manipulation in self.manipulations:
            manipulation.reset()
        self._pixmap = self._manipulated = None

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

    def _apply_manipulation(self, manipulation: Manipulation):
        """Apply changes to displayed image according to an updated manipulation."""
        self._focus(manipulation)
        self.thread_id += 1
        runnable = ManipulateRunner(self, self.thread_id, self._pixmap, manipulation)
        self.pool.start(runnable)

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

    def _on_updated(self, pixmap):
        """Set manipulated and update status when pixmap was updated.

        This is done with signal handling as the ManipulateRunner runs in another
        thread and finally emits the signal.
        """
        self._manipulated = pixmap
        api.status.update()

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


def instance():
    return api.objreg.get(Manipulator)


class ManipulateRunner(QRunnable):
    """Apply manipulations in an extra thread.

    Attributes:
        _id: Integer id of this thread.
        _manipulation: Manipulation to apply.
        _manipulator: Manipulator class to interact with.
        _pixmap: Pixmap to manipulate.
    """

    def __init__(self, manipulator, thread_id, pixmap, manipulation):
        super().__init__()
        self._id = thread_id
        self._manipulation = manipulation
        self._manipulator = manipulator
        self._pixmap = pixmap

    def run(self):
        """Apply manipulations."""
        # Wait for a bit in case user holds down key
        time.sleep(WAIT_TIME)
        if self._id != self._manipulator.thread_id:
            return
        # Apply manipulations to pixmap
        pixmap = self._manipulator.manipulations.apply(self._pixmap, self._manipulation)
        # Update
        self._manipulator.updated.emit(pixmap)
