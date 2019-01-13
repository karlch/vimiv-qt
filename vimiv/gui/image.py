# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""QtWidgets for IMAGE mode."""

from PyQt5.QtCore import Qt, QSize, pyqtSlot
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtGui import QMovie, QPixmap

from vimiv import api
from vimiv.config import styles, keybindings, settings
from vimiv.commands import argtypes, commands
from vimiv.gui import statusbar, widgets
from vimiv.imutils.imsignals import imsignals
from vimiv.modes import modewidget, Modes
from vimiv.utils import eventhandler, objreg, ignore

# We need the check as svg support is optional
try:
    from PyQt5.QtSvg import QSvgWidget
except ImportError:
    QSvgWidget = None


class ScrollableImage(eventhandler.KeyHandler, QScrollArea):
    """QScrollArea to display Image or Animation.

    Connects to the *_loaded signals to create the appropriate child widget.
    Commands used in image mode are defined here. Interaction with the child
    widget happens via the methods defined by widgets.ImageLabel.

    Class Attributes:
        MIN_SIZE_SCALE: Minimum scale to scale an image to.
        MIN_SIZE_PIXEL: Minimum pixel size to scale an image to.
        MAX_SIZE_SCALE: Maximum scale to scale an image to.

    Attributes:
        _scale: ImageScale defining how to scale image on resize.
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

    MIN_SIZE_SCALE = 0.01
    MIN_SIZE_PIXEL = 20
    MAX_SIZE_SCALE = 256

    @modewidget(Modes.IMAGE)
    @objreg.register
    def __init__(self):
        super().__init__()
        self._scale = 1.0

        styles.apply(self)
        self.setAlignment(Qt.AlignCenter)
        self.setWidgetResizable(True)
        self.setWidget(Empty())

        imsignals.pixmap_loaded.connect(self._on_pixmap_loaded)
        imsignals.movie_loaded.connect(self._on_movie_loaded)
        imsignals.svg_loaded.connect(self._on_svg_loaded)
        imsignals.pixmap_updated.connect(self._on_pixmap_updated)
        imsignals.all_images_cleared.connect(self._on_images_cleared)

    @pyqtSlot()
    def _on_images_cleared(self):
        self.setWidget(Empty())

    @pyqtSlot(QPixmap)
    def _on_pixmap_loaded(self, pixmap):
        self.setWidget(Image(pixmap))
        self.scale(argtypes.ImageScale.Overzoom, 1)

    @pyqtSlot(QMovie)
    def _on_movie_loaded(self, movie):
        self.setWidget(Animation(movie))
        self.scale(1, 1)

    @pyqtSlot(str)
    def _on_svg_loaded(self, path):
        self.setWidget(VectorGraphic(path))
        self.scale(argtypes.ImageScale.Fit, 1)

    @pyqtSlot(QPixmap)
    def _on_pixmap_updated(self, pixmap):
        self.setWidget(Image(pixmap))
        self.scale(self._scale, 1)
        statusbar.update()

    @keybindings.add("k", "scroll up", mode=Modes.IMAGE)
    @keybindings.add("j", "scroll down", mode=Modes.IMAGE)
    @keybindings.add("l", "scroll right", mode=Modes.IMAGE)
    @keybindings.add("h", "scroll left", mode=Modes.IMAGE)
    @commands.register(mode=Modes.IMAGE)
    def scroll(self, direction: argtypes.Direction, count: int = 1):
        """Scroll the image in the given direction.

        **syntax:** ``:scroll direction``

        positional arguments:
            * ``direction``: The direction to scroll in (left/right/up/down).

        **count:** multiplier
        """
        if direction in [direction.Left, direction.Right]:
            bar = self.horizontalScrollBar()
            step = self.widget().width() * 0.05 * count
        else:
            bar = self.verticalScrollBar()
            step = self.widget().height() * 0.05 * count
        if direction in [direction.Right, direction.Down]:
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
    @commands.register(mode=Modes.IMAGE)
    def scroll_edge(self, direction: argtypes.Direction):
        """Scroll the image to one edge.

        **syntax:** ``:scroll-edge direction``.

        positional arguments:
            * ``direction``: The direction to scroll in (left/right/up/down).
        """
        if direction in [direction.Left, direction.Right]:
            bar = self.horizontalScrollBar()
        else:
            bar = self.verticalScrollBar()
        if direction in [direction.Left, direction.Up]:
            value = 0
        else:
            value = bar.maximum()
        bar.setValue(value)

    @keybindings.add("-", "zoom out", mode=Modes.IMAGE)
    @keybindings.add("+", "zoom in", mode=Modes.IMAGE)
    @commands.register(mode=Modes.IMAGE)
    def zoom(self, direction: argtypes.Zoom, count: int = 1):
        """Zoom the current widget.

        **syntax:** ``:zoom direction``

        positional arguments:
            * ``direction``: The direction to zoom in (in/out).

        **count:** multiplier
        """
        width = self.current_width()
        if direction == direction.In:
            width *= 1.1**count
        else:
            width /= 1.1**count
        self._scale = width / self.original_width()
        self._scale_to_float(self._scale)

    @keybindings.add("w", "scale --level=fit", mode=Modes.IMAGE)
    @keybindings.add("W", "scale --level=1", mode=Modes.IMAGE)
    @keybindings.add("e", "scale --level=fit-width", mode=Modes.IMAGE)
    @keybindings.add("E", "scale --level=fit-height", mode=Modes.IMAGE)
    @commands.register()
    def scale(self, level: argtypes.ImageScaleFloat = 1, count: int = 1):
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
        if level == argtypes.ImageScale.Overzoom:
            self._scale_to_fit(
                limit=settings.get_value(settings.Names.IMAGE_OVERZOOM))
        elif level == argtypes.ImageScale.Fit:
            self._scale_to_fit()
        elif level == argtypes.ImageScale.FitWidth:
            self._scale_to_width()
        elif level == argtypes.ImageScale.FitHeight:
            self._scale_to_height()
        else:
            level *= count  # Required so it is stored correctly later
            self._scale_to_float(level)
        self._scale = level

    @keybindings.add("<space>", "play-or-pause", mode=Modes.IMAGE)
    @commands.register(mode=Modes.IMAGE)
    def play_or_pause(self):
        """Toggle betwen play and pause of animation."""
        with ignore(AttributeError):  # Currently no animation displayed
            self.widget().play_or_pause()

    def _scale_to_fit(self, limit=-1):
        """Scale image so it fits the widget size.

        Args:
            limit: Largest scale to apply trying to fit the widget size.
        """
        w_factor = self.width() / self.original_width()
        h_factor = self.height() / self.original_height()
        scale = min(w_factor, h_factor)
        # Apply overzoom limit
        if limit > 0:
            scale = min(scale, limit)
        self._scale_to_float(scale)

    def _scale_to_width(self):
        """Scale image so the width fits the widgets width."""
        scale = self.width() / self.original_width()
        self._scale_to_float(scale)

    def _scale_to_height(self):
        """Scale image so the height fits the widgets width."""
        scale = self.height() / self.original_height()
        self._scale_to_float(scale)

    def _scale_to_float(self, level):
        """Scale image to a defined size.

        Args:
            level: Size to scale to as float. 1 is the original image size.
        """
        self.widget().rescale(self._clamp_scale(level))

    def resizeEvent(self, event):
        """Rescale the child image and update statusbar on resize event."""
        super().resizeEvent(event)
        self.scale(self._scale, 1)
        statusbar.update(clear_message=False)  # Zoom level changes

    def width(self):
        """Return width of the viewport to remove scrollbar width."""
        return self.viewport().width()

    def height(self):
        """Returh height of the viewport to remove scrollbar height."""
        return self.viewport().height()

    @api.status.module("{zoomlevel}")
    def _get_zoom_level(self):
        """Zoom level of the image in percent."""
        level = self.current_width() / self.original_width()
        return "%2.0f%%" % (level * 100)

    @api.status.module("{image-size}")
    def _get_image_size(self):
        """Size of the image in pixels in the form WIDTHxHEIGHT."""
        return "%dx%d" % (self.original_width(), self.original_height())

    def current_width(self):
        """Convenience method to get the widgets current width."""
        return self.widget().current_size().width()

    def current_height(self):
        """Convenience method to get the widgets current height."""
        return self.widget().current_size().height()

    def original_width(self):
        """Convenience method to get the widgets original width."""
        return self.widget().original_size().width()

    def original_height(self):
        """Convenience method to get the widgets original height."""
        return self.widget().original_size().height()

    def _clamp_scale(self, scale):
        """Clamp scale applying boundaries."""
        scale = max(scale, self._get_min_scale())
        return min(scale, self.MAX_SIZE_SCALE)

    def _get_min_scale(self):
        """Return minimum scale.

        This is either MIN_SIZE_SCALE or the scale which corresponds to
        MIN_SIZE_PIXEL.
        """
        try:
            widget_size = min(self.widget().original.width(),
                              self.widget().original.height())
            return max(self.MIN_SIZE_SCALE, self.MIN_SIZE_PIXEL / widget_size)
        except AttributeError:
            return 0.01


def instance():
    return objreg.get(ScrollableImage)


class Empty(widgets.ImageLabel):
    """Empty QLabel to display if there is no image."""

    def original_size(self):
        return QSize(1, 1)

    def current_size(self):
        return QSize(1, 1)

    def rescale(self, scale):
        pass


class Image(widgets.ImageLabel):
    """QLabel to display a QPixmap.

    Attributes:
        _original: Pixmap without rescaling.
    """

    def __init__(self, pixmap):
        super().__init__()
        self._original = pixmap

    def current_size(self):
        return self.pixmap().size()

    def original_size(self):
        return self._original.size()

    def rescale(self, scale):
        pixmap = self._original.scaled(self._original.size() * scale,
                                       transformMode=Qt.SmoothTransformation)
        self.setPixmap(pixmap)


class Animation(widgets.ImageLabel):
    """QLabel to display a QMovie.

    Attributes:
        _original_size: Size of the first frame without rescaling.
    """

    def __init__(self, movie):
        super().__init__()
        self.setMovie(movie)
        movie.jumpToFrame(0)
        self._original_size = movie.currentPixmap().size()
        if settings.get_value(settings.Names.IMAGE_AUTOPLAY):
            movie.start()

    def current_size(self):
        return self.movie().scaledSize()

    def original_size(self):
        return self._original_size

    def rescale(self, scale):
        self.movie().setScaledSize(self._original_size * scale)

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
            styles.apply(self)

        def current_size(self):
            return super().size()

        def original_size(self):
            return self.sizeHint()

        def rescale(self, scale):
            self.setFixedSize(self.original_size() * scale)
