# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Module to play a slideshow."""

from typing import Optional

from vimiv.qt.core import QTimer

from vimiv import api


class Timer(QTimer):
    """Slideshow timer with interval according to the current setting."""

    def __init__(self):
        super().__init__()
        api.settings.slideshow.delay.changed.connect(self._set_delay)
        self._set_delay(api.settings.slideshow.delay.value)

    def _set_delay(self, value: float):
        self.setInterval(int(value * 1000))


# Create timer and expose a few methods to the public
_timer = Timer()
event = _timer.timeout
stop = _timer.stop
start = _timer.start


@api.keybindings.register("ss", "slideshow", mode=api.modes.IMAGE)
@api.commands.register(mode=api.modes.IMAGE, name="slideshow")
def toggle(count: Optional[int] = None):
    """Toggle slideshow.

    **count:** Set slideshow delay to count instead.
    """
    if count is not None:
        api.settings.slideshow.delay.value = count
        _timer.setInterval(1000 * count)
    elif _timer.isActive():
        _timer.stop()
    else:
        _timer.start()


@api.status.module("{slideshow-delay}")
def delay() -> str:
    """Slideshow delay in seconds if the slideshow is running."""
    if _timer.isActive():
        interval_seconds = _timer.interval() / 1000
        return f"{interval_seconds:.1f}"
    return ""


@api.status.module("{slideshow-indicator}")
def running_indicator() -> str:
    """Indicator if slideshow is running."""
    return api.settings.slideshow.indicator.value if _timer.isActive() else ""
