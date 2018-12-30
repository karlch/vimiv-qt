# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""QtWidgets for IMAGE mode."""

from PyQt5.QtCore import Qt, QSize, pyqtSlot
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtGui import QMovie, QPixmap

from vimiv.config import styles, keybindings, settings
from vimiv.commands import argtypes, commands
from vimiv.gui import statusbar, widgets
from vimiv.imutils.imsignals import imsignals
from vimiv.modes import modehandler, modewidget, Mode, Modes
from vimiv.utils import eventhandler, objreg

# We need the check as svg support is optional
try:
    from PyQt5.QtSvg import QSvgWidget
except ImportError:
    QSvgWidget = None


class ScrollableImage(eventhandler.KeyHandler, QScrollArea):
    """QScrollArea to display Image or Animation.

    Connects to the pixmap_loaded and movie_loaded signals to create the
    appropriate child widget. All commands used for both children are
    implemented here. Interaction with the children happens via the
    pixmap(), original(), and rescale() methods.

    Attributes:
        _scale: How to scale image on resize.
            One of "overzoom", "fit", "fit-height", "fit-width", float.
        _stack: QStackedLayout containing the ScrollableImage and Thumbnail
            widgets.
    """

    STYLESHEET = """
    QScrollArea {
        background-color: {image.bg};
        border: none;
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

    @modewidget(Modes.IMAGE)
    @objreg.register
    def __init__(self, stack):
        super().__init__()
        self._scale = 1
        self._stack = stack

        styles.apply(self)
        self.setAlignment(Qt.AlignCenter)
        self.setWidgetResizable(True)

        modehandler.signals.entered.connect(self._on_mode_entered)
        imsignals.pixmap_loaded.connect(self._on_pixmap_loaded)
        imsignals.movie_loaded.connect(self._on_movie_loaded)
        imsignals.svg_loaded.connect(self._on_svg_loaded)
        imsignals.pixmap_updated.connect(self._on_pixmap_updated)

    @pyqtSlot(QPixmap)
    def _on_pixmap_loaded(self, pixmap):
        self.setWidget(Image(pixmap))
        self.scale("overzoom", 1)

    @pyqtSlot(QMovie)
    def _on_movie_loaded(self, movie):
        self.setWidget(Animation(movie))
        self.scale(1, 1)

    @pyqtSlot(str)
    def _on_svg_loaded(self, path):
        self.setWidget(VectorGraphic(path))
        self.scale("fit", 1)

    @pyqtSlot(QPixmap)
    def _on_pixmap_updated(self, pixmap):
        self.setWidget(Image(pixmap))
        self.scale(self._scale, 1)
        statusbar.update()

    @keybindings.add("k", "scroll up", mode=Modes.IMAGE)
    @keybindings.add("j", "scroll down", mode=Modes.IMAGE)
    @keybindings.add("l", "scroll right", mode=Modes.IMAGE)
    @keybindings.add("h", "scroll left", mode=Modes.IMAGE)
    @commands.argument("direction", type=argtypes.scroll_direction)
    @commands.register(mode=Modes.IMAGE, count=1)
    def scroll(self, direction, count):
        """Scroll the image in the given direction.

        **syntax:** ``:scroll direction``

        positional arguments:
            * ``direction``: The direction to scroll in (left/right/up/down).

        **count:** multiplier
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

    @keybindings.add("M", "center", mode=Modes.IMAGE)
    @commands.register(mode=Modes.IMAGE)
    def center(self):
        """Center the image in the viewport."""
        for bar in [self.horizontalScrollBar(), self.verticalScrollBar()]:
            bar.setValue(bar.maximum() // 2)

    @keybindings.add("K", "scroll-edge up", mode=Modes.IMAGE)
    @keybindings.add("J", "scroll-edge down", mode=Modes.IMAGE)
    @keybindings.add("L", "scroll-edge right", mode=Modes.IMAGE)
    @keybindings.add("H", "scroll-edge left", mode=Modes.IMAGE)
    @commands.argument("direction", type=argtypes.scroll_direction)
    @commands.register(mode=Modes.IMAGE)
    def scroll_edge(self, direction):
        """Scroll the image to one edge.

        **syntax:** ``:scroll-edge direction``.

        positional arguments:
            * ``direction``: The direction to scroll in (left/right/up/down).
        """
        if direction in ["left", "right"]:
            bar = self.horizontalScrollBar()
        else:
            bar = self.verticalScrollBar()
        if direction in ["left", "up"]:
            value = 0
        else:
            value = bar.maximum()
        bar.setValue(value)

    @keybindings.add("-", "zoom out", mode=Modes.IMAGE)
    @keybindings.add("+", "zoom in", mode=Modes.IMAGE)
    @commands.argument("direction", type=argtypes.zoom)
    @commands.register(count=1, mode=Modes.IMAGE)
    def zoom(self, direction, count):
        """Zoom the current widget.

        **syntax:** ``:zoom direction``

        positional arguments:
            * ``direction``: The direction to zoom in (in/out).

        **count:** multiplier
        """
        width = self.pixmap().width()
        if direction == "in":
            width *= 1.1**count
        else:
            width /= 1.1**count
        self._scale = width / self.original().width()
        self.widget().rescale(self._scale)

    @keybindings.add("w", "scale --level=fit", mode=Modes.IMAGE)
    @keybindings.add("W", "scale --level=1", mode=Modes.IMAGE)
    @keybindings.add("e", "scale --level=fit-width", mode=Modes.IMAGE)
    @keybindings.add("E", "scale --level=fit-height", mode=Modes.IMAGE)
    @commands.argument("level", optional=True, type=argtypes.image_scale,
                       default="fit")
    @commands.register(count=1)
    def scale(self, level, count):
        """Scale the image.

        **syntax:** ``:scale [--level=LEVEL]``

        optional arguments:
            * ``level``: The level to scale the image to.

        .. hint:: supported levels:

            * **fit**: Fit image to current viewport.
            * **fit-width**: Fit image width to current viewport.
            * **fit-height**: Fit image height to current viewport.
            * **overzoom**: Like **fit** but limit to the overzoom setting.
            * **float**: Set scale to arbitrary decimal value.
        """
        if level == "overzoom":
            self._scale_to_fit(
                limit=settings.get_value(settings.Names.IMAGE_OVERZOOM))
        elif level == "fit":
            self._scale_to_fit()
        elif level == "fit-width":
            self._scale_to_width()
        elif level == "fit-height":
            self._scale_to_height()
        else:
            self._scale_to_float(level * count)
        self._scale = level

    @keybindings.add("<space>", "play-or-pause", mode=Modes.IMAGE)
    @commands.register(mode=Modes.IMAGE)
    def play_or_pause(self):
        """Toggle betwen play and pause of animation."""
        try:
            self.widget().play_or_pause()
        except AttributeError:  # Currently no animation displayed
            pass

    def _scale_to_fit(self, limit=-1):
        """Scale image so it fits the widget size.

        Args:
            limit: Largest scale to apply trying to fit the widget size.
        """
        w_factor = self.width() / self.original().width()
        h_factor = self.height() / self.original().height()
        scale = min(w_factor, h_factor)
        # Apply overzoom limit
        if limit > 0:
            scale = min(scale, limit)
        self._scale_to_float(scale)

    def _scale_to_width(self):
        """Scale image so the width fits the widgets width."""
        scale = self.width() / self.original().width()
        self.widget().rescale(scale)

    def _scale_to_height(self):
        """Scale image so the height fits the widgets width."""
        scale = self.height() / self.original().height()
        self.widget().rescale(scale)

    def _scale_to_float(self, level):
        """Scale image to a defined size.

        Args:
            level: Size to scale to as float. 1 is the original image size.
        """
        self.widget().rescale(level)

    def resizeEvent(self, event):
        """Rescale the child image and update statusbar on resize event."""
        super().resizeEvent(event)
        if self.widget():
            self.scale(self._scale, 1)
        statusbar.update(clear_message=False)  # Zoom level changes

    def width(self):
        """Return width of the viewport to remove scrollbar width."""
        return self.viewport().width()

    def height(self):
        """Returh height of the viewport to remove scrollbar height."""
        return self.viewport().height()

    @statusbar.module("{zoomlevel}")
    def _get_zoom_level(self):
        """Zoom level of the image in percent."""
        if not self.widget():
            return "None"
        level = self.pixmap().width() / self.original().width()
        return "%2.0f%%" % (level * 100)

    @statusbar.module("{image-size}")
    def _get_image_size(self):
        """Size of the image in pixels in the form WIDTHxHEIGHT."""
        return "%dx%d" % (self.original().width(), self.original().height())

    def pixmap(self):
        """Convenience method to get the widgets current pixmap."""
        return self.widget().pixmap()

    def original(self):
        """Convenience method to get the widgets original pixmap."""
        return self.widget().original

    @pyqtSlot(Mode, Mode)
    def _on_mode_entered(self, mode, last_mode):
        if mode == Modes.IMAGE:
            self._stack.setCurrentWidget(self)


def instance():
    return objreg.get(ScrollableImage)


class Image(widgets.ImageLabel):
    """QLabel to display a QPixmap.

    Attributes:
        original: Pixmap without rescaling.
    """

    def __init__(self, pixmap):
        """Create the image object.

        Args:
            paths: Initial paths given from the command line.
        """
        super().__init__()
        self.original = pixmap

    def rescale(self, scale):
        """Rescale the image to a new scale."""
        width = self.original.width() * scale
        pixmap = self.original.scaledToWidth(width,
                                             mode=Qt.SmoothTransformation)
        self.setPixmap(pixmap)


class Animation(widgets.ImageLabel):
    """QLabel to display a QMovie.

    Attributes:
        original: Pixmap of the first frame without rescaling.
    """

    def __init__(self, movie):
        super().__init__()
        self.setMovie(movie)
        movie.jumpToFrame(0)
        self.original = movie.currentPixmap()
        if settings.get_value(settings.Names.IMAGE_AUTOPLAY):
            movie.start()

    def pixmap(self):
        """Convenience method to get current pixmap."""
        return self.movie().currentPixmap()

    def rescale(self, scale):
        """Rescale the movie to a new scale."""
        width = self.original.width() * scale
        height = self.original.height() * scale
        self.movie().setScaledSize(QSize(width, height))

    def play_or_pause(self):
        """Toggle betwen play and pause of animation."""
        if self.movie().state() == QMovie.Paused:
            self.movie().setPaused(False)
        else:
            self.movie().setPaused(True)


if QSvgWidget is not None:
    class VectorGraphic(QSvgWidget):
        """Widget to display a vector graphic.

        Attributes:
            original: QSize of the original svg for proper rescaling.
        """

        STYLESHEET = """
        QSvgWidget {
            background-color: {image.bg};
        }
        """

        def __init__(self, path):
            super().__init__(path)
            self.original = self.sizeHint()
            styles.apply(self)

        def pixmap(self):
            """Return the QSvgWidget for size comparisons."""
            return super()

        def rescale(self, scale):
            """Rescale the svg to a new scale."""
            width = self.original.width() * scale
            height = self.original.height() * scale
            self.setFixedSize(width, height)
