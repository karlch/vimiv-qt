# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""QtWidgets for IMAGE mode."""

from contextlib import suppress
from typing import List, Union

from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QFrame,
    QGraphicsItem,
    QGraphicsPixmapItem,
    QLabel,
)
from PyQt5.QtGui import QMovie, QPixmap

from vimiv import api, imutils, utils
from vimiv.commands.argtypes import Direction, ImageScale, ImageScaleFloat, Zoom
from vimiv.config import styles

from .eventhandler import KeyHandler

# We need the check as svg support is optional
try:
    from PyQt5.QtSvg import QGraphicsSvgItem
except ImportError:
    QGraphicsSvgItem = None


INF = float("inf")


class ScrollableImage(KeyHandler, QGraphicsView):
    """QGraphicsView to display Image or Animation.

    Connects to the *_loaded signals to create the appropriate child widget.
    Commands used in image mode are defined here.

    Class Attributes:
        MIN_SCALE: Minimum scale to scale an image to.
        MAX_SCALE: Maximum scale to scale an image to.

    Attributes:
        _scale: ImageScale defining how to scale image on resize.
    """

    STYLESHEET = """
    QGraphicsView {
        background-color: {image.bg};
        border: none;
    }
    """

    MAX_SCALE = 8
    MIN_SCALE = 1 / 8

    @api.modes.widget(api.modes.IMAGE)
    @api.objreg.register
    def __init__(self) -> None:
        super().__init__()
        styles.apply(self)

        self._scale = ImageScaleFloat(1.0)

        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.Box)
        scene = QGraphicsScene()
        scene.setSceneRect(QRectF(0, 0, 1, 1))
        self.setScene(scene)
        self.setOptimizationFlags(QGraphicsView.DontSavePainterState)

        api.signals.pixmap_loaded.connect(self._load_pixmap)
        api.signals.movie_loaded.connect(self._load_movie)
        if QGraphicsSvgItem is not None:
            api.signals.svg_loaded.connect(self._load_svg)
        api.signals.all_images_cleared.connect(self._on_images_cleared)

    @staticmethod
    def current() -> str:
        """Current path for image mode."""
        return imutils.current()

    @staticmethod
    def pathlist() -> List[str]:
        """List of current paths for image mode."""
        return imutils.pathlist()

    def _load_pixmap(self, pixmap: QPixmap, reload_only: bool) -> None:
        """Load new pixmap into the graphics scene."""
        item = QGraphicsPixmapItem()
        item.setPixmap(pixmap)
        item.setTransformationMode(Qt.SmoothTransformation)
        self._update_scene(item, item.boundingRect(), reload_only)

    def _load_movie(self, movie: QMovie, reload_only: bool) -> None:
        """Load new movie into the graphics scene."""
        movie.jumpToFrame(0)
        if api.settings.image.autoplay.value:
            movie.start()
        widget = QLabel()
        widget.setMovie(movie)
        self._update_scene(widget, QRectF(movie.currentPixmap().rect()), reload_only)

    def _load_svg(self, path: str, reload_only: bool) -> None:
        """Load new vector graphic into the graphics scene."""
        item = QGraphicsSvgItem(path)
        self._update_scene(item, item.boundingRect(), reload_only)

    def _update_scene(
        self, item: Union[QGraphicsItem, QLabel], rect: QRectF, reload_only: bool
    ) -> None:
        """Update the scene with the newly loaded item."""
        self.scene().clear()
        if isinstance(item, QGraphicsItem):
            self.scene().addItem(item)
        else:
            self.scene().addWidget(item)
        self.scene().setSceneRect(rect)
        self.scale(self._scale if reload_only else ImageScale.Overzoom)  # type: ignore

    def _on_images_cleared(self) -> None:
        self.scene().clear()

    @api.keybindings.register("k", "scroll up", mode=api.modes.IMAGE)
    @api.keybindings.register("j", "scroll down", mode=api.modes.IMAGE)
    @api.keybindings.register("l", "scroll right", mode=api.modes.IMAGE)
    @api.keybindings.register("h", "scroll left", mode=api.modes.IMAGE)
    @api.commands.register(mode=api.modes.IMAGE)
    def scroll(self, direction: Direction, count: int = 1):  # type: ignore[override]
        """Scroll the image in the given direction.

        **syntax:** ``:scroll direction``

        positional arguments:
            * ``direction``: The direction to scroll in (left/right/up/down).

        **count:** multiplier
        """
        if direction in (direction.Left, direction.Right):
            bar = self.horizontalScrollBar()
            step = int(self.scene().sceneRect().width() * 0.05 * count)
        else:
            bar = self.verticalScrollBar()
            step = int(self.scene().sceneRect().height() * 0.05 * count)
        if direction in (direction.Right, direction.Down):
            bar.setValue(bar.value() + step)
        else:
            bar.setValue(bar.value() - step)

    @api.keybindings.register("M", "center", mode=api.modes.IMAGE)
    @api.commands.register(mode=api.modes.IMAGE)
    def center(self):
        """Center the image in the viewport."""
        rect = self.scene().sceneRect()
        self.centerOn(rect.width() / 2, rect.height() / 2)

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
        value = 0 if direction in (Direction.Left, Direction.Up) else bar.maximum()
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
        scale = 1.25 ** count if direction == Zoom.In else 1 / 1.25 ** count
        self._scale_to_float(self.zoom_level * scale)
        self._scale = ImageScaleFloat(self.zoom_level)

    @api.keybindings.register("w", "scale --level=fit", mode=api.modes.IMAGE)
    @api.keybindings.register("W", "scale --level=1", mode=api.modes.IMAGE)
    @api.keybindings.register("e", "scale --level=fit-width", mode=api.modes.IMAGE)
    @api.keybindings.register("E", "scale --level=fit-height", mode=api.modes.IMAGE)
    @api.commands.register()
    def scale(  # type: ignore[override]
        self, level: ImageScaleFloat = ImageScaleFloat(1), count: int = 1
    ):
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
        rect = self.scene().sceneRect()
        if level == ImageScale.Overzoom:
            self._scale_to_fit(
                rect.width(), rect.height(), limit=api.settings.image.overzoom.value
            )
        elif level == ImageScale.Fit:
            self._scale_to_fit(rect.width(), rect.height())
        elif level == ImageScale.FitWidth:
            self._scale_to_fit(width=rect.width())
        elif level == ImageScale.FitHeight:
            self._scale_to_fit(height=rect.height())
        elif isinstance(level, float):
            level *= count  # Required so it is stored correctly later
            self._scale_to_float(level)
        self._scale = level
        self.center()

    def _scale_to_fit(
        self, width: float = None, height: float = None, limit: float = INF
    ):
        """Scale image so it fits the widget size.

        Args:
            limit: Largest scale to apply trying to fit the widget size.
        """
        if self.scene() is None:
            return
        xratio = self.viewport().width() / width if width is not None else INF
        yratio = self.viewport().height() / height if height is not None else INF
        ratio = min(xratio, yratio, limit)
        self._scale_to_float(ratio)

    def _scale_to_float(self, level: float) -> None:
        """Scale image to a defined size.

        Args:
            level: Size to scale to. 1 is the original image size.
        """
        level = utils.clamp(level, self.MIN_SCALE, self.MAX_SCALE)
        super().scale(level / self.zoom_level, level / self.zoom_level)

    @property
    def zoom_level(self) -> float:
        """Retrieve the current zoom level. 1 is the original image size."""
        return self.transform().m11()

    @api.status.module("{zoomlevel}")
    def _get_zoom_level(self) -> str:
        """Zoom level of the image in percent."""
        return f"{self.zoom_level * 100:2.0f}%"

    @api.status.module("{image-size}")
    def _get_image_size(self):
        """Size of the image in pixels in the form WIDTHxHEIGHT."""
        rect = self.scene().sceneRect()
        return f"{rect.width():.0f}x{rect.height():.0f}"

    @api.keybindings.register("<space>", "play-or-pause", mode=api.modes.IMAGE)
    @api.commands.register(mode=api.modes.IMAGE)
    def play_or_pause(self):
        """Toggle betwen play and pause of animation."""
        with suppress(IndexError, AttributeError):  # No items loaded, not a movie
            widget = self.items()[0].widget()
            movie = widget.movie()
            movie.setPaused(not movie.state() == QMovie.Paused)

    def resizeEvent(self, event):
        """Rescale the child image and update statusbar on resize event."""
        super().resizeEvent(event)
        self.scale(self._scale)
        api.status.update("image zoom level changed")

    def mousePressEvent(self, event):
        """Update mouse press event to start panning on left button."""
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Update mouse release event to stop any panning."""
        self.setDragMode(QGraphicsView.NoDrag)
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        """Update mouse wheel to zoom with control."""
        if event.modifiers() & Qt.ControlModifier:
            scale = 1.03 ** event.angleDelta().y()
            self._scale_to_float(self.zoom_level * scale)
            self._scale = ImageScaleFloat(self.zoom_level)
            api.status.update("image zoom level changed")
        else:
            super().wheelEvent(event)
