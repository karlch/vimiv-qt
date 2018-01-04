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
from vimiv.imutils import imsignals
from vimiv.modes import modehandler
from vimiv.utils import eventhandler, objreg


class ScrollableImage(eventhandler.KeyHandler, QScrollArea):
    """QScrollArea to display Image or Animation.

    Connects to the pixmap_loaded and movie_loaded signals to create the
    appropriate child widget. All commands used for both children are
    implemented here. Interaction to the children happens via the
    pixmap(), original(), and rescale() methods.

    Attributes:
        _scale: How to scale image on resize.
            One of "overzoom", "fit", "fit-height", "fit-width", float.
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

    @objreg.register("image")
    def __init__(self, stack):
        super().__init__()
        self._stack = stack
        styles.apply(self)
        self.setWidgetResizable(True)
        self._scale = "1"

        modehandler.instance().entered.connect(self._on_enter)
        imsignals.connect(self._on_pixmap_loaded, "pixmap_loaded")
        imsignals.connect(self._on_movie_loaded, "movie_loaded")

    @pyqtSlot(QPixmap)
    def _on_pixmap_loaded(self, pixmap):
        self.setWidget(Image(self, pixmap))
        self.scale("overzoom", 1)

    @pyqtSlot(QMovie)
    def _on_movie_loaded(self, movie):
        self.setWidget(Animation(self, movie))
        self.scale(1, 1)

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

    @keybindings.add("M", "center", mode="image")
    @commands.register(instance="image", mode="image")
    def center(self):
        """Center the image."""
        for bar in [self.horizontalScrollBar(), self.verticalScrollBar()]:
            bar.setValue(bar.maximum() // 2)

    @keybindings.add("K", "scroll-edge up", mode="image")
    @keybindings.add("J", "scroll-edge down", mode="image")
    @keybindings.add("L", "scroll-edge right", mode="image")
    @keybindings.add("H", "scroll-edge left", mode="image")
    @commands.argument("direction", type=argtypes.scroll_direction)
    @commands.register(instance="image", mode="image")
    def scroll_edge(self, direction):
        """Scroll the image to the edge.

        Args:
            direction: One of "left", "right", "up", "down".
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

    @keybindings.add("-", "zoom out", mode="image")
    @keybindings.add("+", "zoom in", mode="image")
    @commands.argument("direction", type=argtypes.zoom)
    @commands.register(instance="image", count=1, mode="image")
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
        self._scale = width / self.original().width()
        self.widget().rescale(self._scale)

    @keybindings.add("w", "scale --level=fit", mode="image")
    @keybindings.add("W", "scale --level=1", mode="image")
    @keybindings.add("e", "scale --level=fit-width", mode="image")
    @keybindings.add("E", "scale --level=fit-height", mode="image")
    @commands.argument("level", optional=True, type=argtypes.image_scale)
    @commands.register(instance="image", count=1)
    def scale(self, level, count):
        """Scale the image.

        Args:
            level: One of "fit", "fit-width", "fit-height", positive_float
                defining the level of the scale.
        """
        if level == "overzoom":
            self._scale_to_fit(limit=settings.get_value("image.overzoom"))
        elif level == "fit":
            self._scale_to_fit()
        elif level == "fit-width":
            self._scale_to_width()
        elif level == "fit-height":
            self._scale_to_height()
        else:
            self._scale_to_float(level * count)
        self._scale = level

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

    @statusbar.module("{zoomlevel}", instance="image")
    def _get_zoom_level(self):
        """Return the current zoom level in percent."""
        if not self.widget():
            return "None"
        level = self.pixmap().width() / self.original().width()
        return "%2.0f%%" % (level * 100)

    def pixmap(self):
        """Convenience method to get the widgets current pixmap."""
        return self.widget().pixmap()

    def original(self):
        """Convenience method to get the widgets original pixmap."""
        return self.widget().original

    @pyqtSlot(str)
    def _on_enter(self, widget):
        if widget == "image":
            self._stack.setCurrentWidget(self)


class Image(widgets.ImageLabel):
    """QLabel to display a QPixmap.

    Attributes:
        original: Pixmap without rescaling.
    """

    def __init__(self, parent, pixmap):
        """Create the image object.

        Args:
            paths: Initial paths given from the command line.
        """
        super().__init__(parent=parent)
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

    def __init__(self, parent, movie):
        super().__init__(parent=parent)
        self.setMovie(movie)
        movie.jumpToFrame(0)
        self.original = movie.currentPixmap()
        if settings.get_value("image.autoplay"):
            movie.start()

    def pixmap(self):
        """Convenience method to get current pixmap."""
        return self.movie().currentPixmap()

    def rescale(self, scale):
        """Rescale the movie to a new scale."""
        width = self.original.width() * scale
        height = self.original.height() * scale
        self.movie().setScaledSize(QSize(width, height))

    @keybindings.add("<space>", "play-or-pause", mode="image")
    @commands.register(instance="animation", mode="image")
    def play_or_pause(self):
        """Toggle betwen play and pause of animation."""
        if self.movie().state() == QMovie.Paused:
            self.movie().setPaused(False)
        else:
            self.movie().setPaused(True)
