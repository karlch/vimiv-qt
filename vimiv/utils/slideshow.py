# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Class to play a slideshow."""

from PyQt5.QtCore import QTimer, pyqtSignal

from vimiv.commands import commands
from vimiv.config import settings, keybindings
from vimiv.gui import statusbar
from vimiv.utils import objreg


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
        # TODO get default somehow
        self.setInterval(2000)

    @keybindings.add("s", "slideshow", mode="image")
    @commands.register(instance="slideshow", mode="image", count=0)
    def slideshow(self, count):
        """Toggle slideshow."""
        if count:
            self.setInterval(1000 * count)
        elif self.isActive():
            self.stop()
        else:
            self.start()

    def timerEvent(self, event):
        """Emit next_im signal on timer tick."""
        self.next_im.emit()
        statusbar.update()

    def _on_settings_changed(self, setting, new_value):
        if setting == "slideshow_delay":
            self.setInterval(new_value * 1000)
