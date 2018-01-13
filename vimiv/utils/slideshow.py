# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Class to play a slideshow."""

from PyQt5.QtCore import QTimer, pyqtSignal, pyqtSlot

from vimiv.commands import commands
from vimiv.config import settings, keybindings
from vimiv.gui import statusbar
from vimiv.utils import objreg


def init():
    """Create Slideshow object."""
    Slideshow()


class Slideshow(QTimer):
    """Slideshow class inheriting from QTimer.

    Signals:
        next_im: Emitted when the next image should be displayed.
    """

    next_im = pyqtSignal()

    @objreg.register("slideshow")
    def __init__(self):
        super().__init__()
        settings.signals.changed.connect(self._on_settings_changed)
        interval = settings.get_value("slideshow.delay") * 1000
        self.setInterval(interval)

    @keybindings.add("s", "slideshow", mode="image")
    @commands.register(instance="slideshow", mode="image", count=0)
    def slideshow(self, count):
        """Toggle slideshow."""
        if count:
            settings.override("slideshow.delay", str(count))
            self.setInterval(1000 * count)
        elif self.isActive():
            self.stop()
        else:
            self.start()

    def timerEvent(self, event):
        """Emit next_im signal on timer tick."""
        self.next_im.emit()
        statusbar.update()

    @statusbar.module("{slideshow-delay}", instance="slideshow")
    def get_delay(self):
        """Slideshow delay in seconds if the slideshow is running."""
        if self.isActive():
            delay = self.interval() / 1000
            return "%.1fs" % (delay)
        return ""

    @statusbar.module("{slideshow-indicator}", instance="slideshow")
    def running_indicator(self):
        """Indicator if slideshow is running."""
        if self.isActive():
            return settings.get_value("slideshow.indicator")
        return ""

    @pyqtSlot(str, object)
    def _on_settings_changed(self, setting, new_value):
        if setting == "slideshow.delay":
            self.setInterval(new_value * 1000)
