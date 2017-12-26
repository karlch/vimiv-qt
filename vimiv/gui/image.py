# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""QtWidgets for IMAGE mode."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QScrollArea
from PyQt5.QtGui import QPixmap, QColor

from vimiv.config import styles, keybindings
from vimiv.commands import argtypes, commands
from vimiv.gui import statusbar
from vimiv.imutils.communicate import signals
from vimiv.modes import modehandler
from vimiv.utils import eventhandler, objreg


class ScrollableImage(eventhandler.KeyHandler, QScrollArea):
    """QScrollArea which contains the Image class to allow scrolling."""

    STYLESHEET = """
    QScrollArea {
        background-color: {image.bg};
    }

    QScrollArea QScrollBar {
        width: {image.scrollbar.width};
        background: {image.scrollbar.bg};

    }
    QScrollArea QScrollBar::handle {
        width: {image.scrollbar.width};
        background: {image.scrollbar.fg};
        border: {image.scrollbar.padding} solid {image.scrollbar.bg};
        min-height: 10px;
    }

    QScrollArea QScrollBar::sub-line, QScrollBar::add-line {
        border: none;
        background: none;
    }

    QScrollArea QScrollBar:horizontal {
        height: {image.scrollbar.width};
        background: {image.scrollbar.bg};

    }
    QScrollArea QScrollBar::handle:horizontal {
        height: {image.scrollbar.width};
        background: {image.scrollbar.fg};
        border: {image.scrollbar.padding} solid {image.scrollbar.bg};
        min-width: 10px;
    }

    QScrollArea QScrollBar::sub-line, QScrollBar::add-line {
        border: none;
        background: none;
    }
    """

    @objreg.register("image")
    def __init__(self, stack):
        super().__init__()
        self._stack = stack
        styles.apply(self)
        self.setWidget(Image(parent=self))
        self.setWidgetResizable(True)

        modehandler.signals.enter.connect(self._on_enter)

    @keybindings.add("k", "scroll up", mode="image")
    @keybindings.add("j", "scroll down", mode="image")
    @keybindings.add("l", "scroll right", mode="image")
    @keybindings.add("h", "scroll left", mode="image")
    @commands.argument("direction", type=argtypes.scroll_direction)
    @commands.register(instance="image", mode="image", count=1)
    def scroll(self, direction, count):
        """Scroll the image.

        Args:
            direction: One of "left", "right", "up", "down".
        """
        if direction in ["left", "right"]:
            bar = self.horizontalScrollBar()
            step = self.widget().width() * 0.05 * count
        else:
            bar = self.verticalScrollBar()
            step = self.widget().height() * 0.05 * count
        if direction in ["right", "down"]:
            step *= -1
        bar.setValue(bar.value() - step)

    def resizeEvent(self, event):
        """Rescale the child image and update statusbar on resize event."""
        self.widget().rescale()
        statusbar.update()  # Zoom level changes

    def _on_enter(self, widget):
        if widget == "image":
            self._stack.setCurrentWidget(self)


class Image(QLabel):
    """QLabel to display a QPixmap.

    Attributes:
        _pm_original: The pixmap as directly read from file without rescaling.
        _bg: Color to show if no image is open.
    """

    STYLESHEET = """
    QLabel {
        background-color: {image.bg};
    }
    """

    @objreg.register("pixmap")
    def __init__(self, parent):
        """Create the image object.

        Args:
            paths: Initial paths given from the command line.
        """
        super().__init__(parent=parent)
        styles.apply(self)
        self._pm_original = QPixmap(1, 1)
        self._bg = QColor(0, 0, 0)
        try:
            self._bg.setNamedColor(styles.get("image.bg"))
        except KeyError:
            self._bg.setNamedColor("#000000")
        self._pm_original.fill(self._bg)
        self.setAlignment(Qt.AlignCenter)
        signals.image_loaded.connect(self._on_image_loaded)
        self._scale = "fit"

    def _on_image_loaded(self, path):
        """Open an image and display it.

        Args:
            path: Path of the image to open.
        """
        self._scale = "fit"
        if not path:  # TODO test if image was there
            self._pm_original.fill(self._bg)
        else:
            self._pm_original = QPixmap(path)
            self._scale_to_fit()

    @keybindings.add("-", "zoom out", mode="image")
    @keybindings.add("+", "zoom in", mode="image")
    @commands.argument("direction", type=argtypes.zoom)
    @commands.register(instance="pixmap", count=1)
    def zoom(self, direction, count):
        """Zoom the image.

        Args:
            direction: One of "in", "out".
        """
        width = self.pixmap().width()
        if direction == "in":
            width *= 1.1**count
        else:
            width /= 1.1**count
        self._scale = width / self._pm_original.width()
        self.rescale()

    @keybindings.add("w", "scale --level=fit", mode="image")
    @keybindings.add("W", "scale --level=1", mode="image")
    @keybindings.add("e", "scale --level=fit-width", mode="image")
    @keybindings.add("E", "scale --level=fit-height", mode="image")
    @commands.argument("level", optional=True, type=argtypes.image_scale)
    @commands.register(instance="pixmap", count=1)
    def scale(self, level, count):
        """Scale the image.

        Args:
            level: One of "fit", "fit-width", "fit-height", positive_float
                defining the level of the scale.
        """
        if level == "fit":
            self._scale_to_fit()
        elif level == "fit-width":
            self._scale_to_width()
        elif level == "fit-height":
            self._scale_to_height()
        else:
            self._scale_to_float(level * count)
        self._scale = level

    def rescale(self):
        """Rescale the image to a new scale."""
        self.scale(self._scale, 1)

    def _scale_to_fit(self):
        """Scale image so it fits the widget size."""
        w_factor = self.parent().width() / self._pm_original.width()
        h_factor = self.parent().height() / self._pm_original.height()
        if w_factor < h_factor:
            self._scale_to_width()
        else:
            self._scale_to_height()

    def _scale_to_width(self):
        """Scale image so the width fits the widgets width."""
        pm = self._pm_original.scaledToWidth(self.parent().width(),
                                             mode=Qt.SmoothTransformation)
        self.setPixmap(pm)

    def _scale_to_height(self):
        """Scale image so the height fits the widgets width."""
        pm = self._pm_original.scaledToHeight(self.parent().height(),
                                              mode=Qt.SmoothTransformation)
        self.setPixmap(pm)

    def _scale_to_float(self, level):
        """Scale image to a defined size.

        Args:
            level: Size to scale to as float. 1 is the original image size.
        """
        width = self._pm_original.width() * level
        pm = self._pm_original.scaledToWidth(width,
                                             mode=Qt.SmoothTransformation)
        self.setPixmap(pm)

    @statusbar.module("{zoomlevel}", instance="pixmap")
    def _get_zoom_level(self):
        """Return the current zoom level in percent."""
        if self._pm_original.width() == 1:  # No image
            return "   "
        level = self.pixmap().width() / self._pm_original.width()
        return "%2.0f%%" % (level * 100)
