# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""QtWidgets for IMAGE mode."""

from functools import partial
from contextlib import suppress
from typing import Optional, List

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QScrollArea, QLabel
from PyQt5.QtGui import QMovie

from vimiv import api, utils, imutils
from vimiv.config import styles
from vimiv.commands.argtypes import Direction, ImageScale, ImageScaleFloat, Zoom
from .eventhandler import KeyHandler

# We need the check as svg support is optional
try:
    from PyQt5.QtSvg import QSvgWidget
except ImportError:
    QSvgWidget = None


class ScrollableImage(KeyHandler, QScrollArea):
    """QScrollArea to display Image or Animation.

    Connects to the *_loaded signals to create the appropriate child widget.
    Commands used in image mode are defined here. Interaction with the child
    widget happens via the methods defined by ImageLabel.

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

    @api.modes.widget(api.modes.IMAGE)
    @api.objreg.register
    def __init__(self):
        super().__init__()
        self._scale = 1.0

        styles.apply(self)
        self.setAlignment(Qt.AlignCenter)
        self.setWidgetResizable(True)
        self.setWidget(Empty())

        api.signals.pixmap_loaded.connect(
            partial(self._load, widget=Image, scale=ImageScale.Overzoom)
        )
        api.signals.movie_loaded.connect(partial(self._load, widget=Animation, scale=1))
        if QSvgWidget is not None:  # Only connect loading of svg if available
            api.signals.svg_loaded.connect(
                partial(self._load, widget=VectorGraphic, scale=ImageScale.Fit)
            )
        api.signals.all_images_cleared.connect(self._on_images_cleared)

    @utils.slot
    def _on_images_cleared(self) -> None:
        self.setWidget(Empty())

    def _load(
        self, argument, reload_only, widget, scale: Optional[ImageScale] = None
    ) -> None:
        """Load a new widget into the scrollable image.

        This method is specialized accordingly for the different possible widgets using
        functools.partial  in __init__. The argument is always passed by the emitted
        signal, the other args are specialized using partial.

        Args:
            argument: Argument passed to the widget constructor.
            reload_only: True if the current image is only reloaded.
            widget: Widget created for this argument.
            scale: Scale to set after loading defaulting to the current scale.
        """
        scale = scale if scale is not None and not reload_only else self._scale
        self.setWidget(widget(argument))
        self.scale(scale)
        api.status.update()

    @api.keybindings.register("k", "scroll up", mode=api.modes.IMAGE)
    @api.keybindings.register("j", "scroll down", mode=api.modes.IMAGE)
    @api.keybindings.register("l", "scroll right", mode=api.modes.IMAGE)
    @api.keybindings.register("h", "scroll left", mode=api.modes.IMAGE)
    @api.commands.register(mode=api.modes.IMAGE)
    def scroll(self, direction: Direction, count: int = 1):
        """Scroll the image in the given direction.

        **syntax:** ``:scroll direction``

        positional arguments:
            * ``direction``: The direction to scroll in (left/right/up/down).

        **count:** multiplier
        """
        if direction in (direction.Left, direction.Right):
            bar = self.horizontalScrollBar()
            step = int(self.widget().width() * 0.05 * count)
        else:
            bar = self.verticalScrollBar()
            step = int(self.widget().height() * 0.05 * count)
        if direction in (direction.Right, direction.Down):
            step *= int(-1)
        bar.setValue(bar.value() - step)

    @api.keybindings.register("M", "center", mode=api.modes.IMAGE)
    @api.commands.register(mode=api.modes.IMAGE)
    def center(self):
        """Center the image in the viewport."""
        for bar in (self.horizontalScrollBar(), self.verticalScrollBar()):
            bar.setValue(bar.maximum() // 2)

    @api.keybindings.register("K", "scroll-edge up", mode=api.modes.IMAGE)
    @api.keybindings.register("J", "scroll-edge down", mode=api.modes.IMAGE)
    @api.keybindings.register("L", "scroll-edge right", mode=api.modes.IMAGE)
    @api.keybindings.register("H", "scroll-edge left", mode=api.modes.IMAGE)
    @api.commands.register(mode=api.modes.IMAGE)
    def scroll_edge(self, direction: Direction):
        """Scroll the image to one edge.

        **syntax:** ``:scroll-edge direction``.

        positional arguments:
            * ``direction``: The direction to scroll in (left/right/up/down).
        """
        if direction in (Direction.Left, Direction.Right):
            bar = self.horizontalScrollBar()
        else:
            bar = self.verticalScrollBar()
        if direction in (Direction.Left, Direction.Up):
            value = 0
        else:
            value = bar.maximum()
        bar.setValue(value)

    @api.keybindings.register("-", "zoom out", mode=api.modes.IMAGE)
    @api.keybindings.register("+", "zoom in", mode=api.modes.IMAGE)
    @api.commands.register(mode=api.modes.IMAGE)
    def zoom(self, direction: Zoom, count: int = 1):
        """Zoom the current widget.

        **syntax:** ``:zoom direction``

        positional arguments:
            * ``direction``: The direction to zoom in (in/out).

        **count:** multiplier
        """
        width = self.current_width()
        if direction == Zoom.In:
            width *= 1.1 ** count
        else:
            width /= 1.1 ** count
        self._scale = width / self.original_width()
        self._scale_to_float(self._scale)

    @api.keybindings.register("w", "scale --level=fit", mode=api.modes.IMAGE)
    @api.keybindings.register("W", "scale --level=1", mode=api.modes.IMAGE)
    @api.keybindings.register("e", "scale --level=fit-width", mode=api.modes.IMAGE)
    @api.keybindings.register("E", "scale --level=fit-height", mode=api.modes.IMAGE)
    @api.commands.register()
    def scale(self, level: ImageScaleFloat = ImageScaleFloat(1), count: int = 1):
        """Scale the image.

        **syntax:** ``:scale [--level=LEVEL]``

        **count:** If level is a float, multiply by count.

        optional arguments:
            * ``--level``: The level to scale the image to.

        .. hint:: supported levels:

            * **fit**: Fit image to current viewport.
            * **fit-width**: Fit image width to current viewport.
            * **fit-height**: Fit image height to current viewport.
            * **overzoom**: Like **fit** but limit to the overzoom setting.
            * **float**: Set scale to arbitrary decimal value.
        """
        if level == ImageScale.Overzoom:
            self._scale_to_fit(limit=api.settings.image.overzoom.value)
        elif level == ImageScale.Fit:
            self._scale_to_fit()
        elif level == ImageScale.FitWidth:
            self._scale_to_width()
        elif level == ImageScale.FitHeight:
            self._scale_to_height()
        elif isinstance(level, float):
            level *= count  # Required so it is stored correctly later
            self._scale_to_float(level)
        self._scale = level

    @api.keybindings.register("<space>", "play-or-pause", mode=api.modes.IMAGE)
    @api.commands.register(mode=api.modes.IMAGE)
    def play_or_pause(self):
        """Toggle betwen play and pause of animation."""
        with suppress(AttributeError):  # Currently no animation displayed
            self.widget().play_or_pause()

    @staticmethod
    def current() -> str:
        """Current path for image mode."""
        return imutils.current()

    @staticmethod
    def pathlist() -> List[str]:
        """List of current paths for manipulate mode."""
        return imutils.pathlist()

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
        self.scale(self._scale, count=1)
        api.status.update()  # Zoom level changes

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
        return f"{level * 100:2.0f}%"

    @api.status.module("{image-size}")
    def _get_image_size(self):
        """Size of the image in pixels in the form WIDTHxHEIGHT."""
        return f"{self.original_width()}x{self.original_height()}"

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
        widget_size = min(self.original_width(), self.original_height())
        return max(self.MIN_SIZE_SCALE, self.MIN_SIZE_PIXEL / widget_size)


class ImageLabel(QLabel):
    """Label used to display images in image mode."""

    STYLESHEET = """
    QLabel {
        background-color: {image.bg};
    }
    """

    def __init__(self):
        super().__init__()
        styles.apply(self)
        self.setAlignment(Qt.AlignCenter)

    def current_size(self):
        """Return size of the currently displayed image."""
        raise NotImplementedError("Must be implemented by child widget")

    def original_size(self):
        """Return size of the original image."""
        raise NotImplementedError("Must be implemented by child widget")

    def rescale(self, scale):
        """Rescale the widget to scale."""
        raise NotImplementedError("Must be implemented by child widget")


class Empty(ImageLabel):
    """Empty QLabel to display if there is no image."""

    def original_size(self):
        return QSize(1, 1)

    def current_size(self):
        return QSize(1, 1)

    def rescale(self, scale):
        pass


class Image(ImageLabel):
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
        pixmap = self._original.scaled(
            self._original.size() * scale, transformMode=Qt.SmoothTransformation
        )
        self.setPixmap(pixmap)


class Animation(ImageLabel):
    """QLabel to display a QMovie.

    Attributes:
        _original_size: Size of the first frame without rescaling.
    """

    def __init__(self, movie):
        super().__init__()
        self.setMovie(movie)
        movie.jumpToFrame(0)
        self._original_size = movie.currentPixmap().size()
        self.movie().setScaledSize(self._original_size)
        if api.settings.image.autoplay.value:
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
