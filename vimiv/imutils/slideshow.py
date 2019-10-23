# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Class to play a slideshow."""

from typing import Optional

from PyQt5.QtCore import QTimer

from vimiv import api


class Slideshow(QTimer):
    """Slideshow class inheriting from QTimer."""

    @api.objreg.register
    def __init__(self):
        super().__init__()
        api.settings.slideshow.delay.changed.connect(self._on_delay_changed)
        self.setInterval(int(api.settings.slideshow.delay.value * 1000))

    @api.keybindings.register("ss", "slideshow", mode=api.modes.IMAGE)
    @api.commands.register(mode=api.modes.IMAGE)
    def slideshow(self, count: Optional[int] = None):
        """Toggle slideshow.

        **count:** Set slideshow delay to count instead.
        """
        if count is not None:
            api.settings.slideshow.delay.value = count
            self.setInterval(1000 * count)
        elif self.isActive():
            self.stop()
        else:
            self.start()

    @api.status.module("{slideshow-delay}")
    def delay(self) -> str:
        """Slideshow delay in seconds if the slideshow is running."""
        interval_seconds = self.interval() / 1000
        return f"{interval_seconds:.1f}" if self.isActive() else ""

    @api.status.module("{slideshow-indicator}")
    def running_indicator(self) -> str:
        """Indicator if slideshow is running."""
        return api.settings.slideshow.indicator.value if self.isActive() else ""

    def _on_delay_changed(self, value: float):
        self.setInterval(int(value * 1000))
