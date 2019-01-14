# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Definition of commands and status objects only using the api.

This is in its own module as the api itself should only provide the
infrastructure and not define any actual implementations.
"""

from vimiv import api


###############################################################################
#                                  Commands                                   #
###############################################################################
@api.keybindings.add("gm", "enter manipulate")
@api.keybindings.add("gt", "enter thumbnail")
@api.keybindings.add("gl", "enter library")
@api.keybindings.add("gi", "enter image")
@api.commands.register()
def enter(mode: str):
    """Enter another mode.

    **syntax:** ``:enter mode``

    positional arguments:
        * ``mode``: The mode to enter (image/library/thumbnail/manipulate).
    """
    api.modes.enter(api.modes.get_by_name(mode))


@api.keybindings.add("tm", "toggle manipulate")
@api.keybindings.add("tt", "toggle thumbnail")
@api.keybindings.add("tl", "toggle library")
@api.commands.register()
def toggle(mode: str):
    """Toggle one mode.

    **syntax:** ``:toggle mode``.

    If the mode is currently visible, leave it. Otherwise enter it.

    positional arguments:
        * ``mode``: The mode to toggle (image/library/thumbnail/manipulate).
    """
    api.modes.toggle(api.modes.get_by_name(mode))


###############################################################################
#                               Status Modules                                #
###############################################################################
@api.status.module("{mode}")
def _active_name():
    """Current mode."""
    return api.modes.current().name.upper()


def init():
    """Initialize the api modules.

    Currently does not do anything but this module must be imported so the
    decorators register all the modules.
    """
