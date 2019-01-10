# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Commands dealing with settings and configuration."""

from typing import List

from vimiv.commands import commands, cmdexc
from vimiv.config import settings, keybindings
from vimiv.modes import modehandler, Modes
from vimiv.utils import strconvert


@keybindings.add(".", "set slideshow.delay +0.5", mode=Modes.IMAGE)
@keybindings.add(",", "set slideshow.delay -0.5", mode=Modes.IMAGE)
@keybindings.add("H", "set library.width -0.05", mode=Modes.LIBRARY)
@keybindings.add("L", "set library.width +0.05", mode=Modes.LIBRARY)
@keybindings.add("b", "set statusbar.show!")
@commands.register()
def set(setting: str, value: List[str]):  # pylint: disable=redefined-builtin
    """Set an option.

    **syntax:** ``:set setting [value]``

    positional arguments:
        * ``setting``: Name of the setting to set.
        * ``value``: Value to set the setting to. If not given, set to default.
    """
    value = " ".join(value)  # List comes from nargs='*'
    try:
        # Toggle boolean settings
        if setting.endswith("!"):
            setting = setting.rstrip("!")
            settings.toggle(setting)
        # Add to number settings
        elif value and (value.startswith("+") or value.startswith("-")):
            settings.add_to(setting, value)
        # Set default
        elif value == "":
            settings.set_to_default(setting)
        else:
            settings.override(setting, value)
        new_value = settings.get_value(setting)
        settings.signals.changed.emit(setting, new_value)
    except KeyError as e:
        raise cmdexc.CommandError("unknown setting %s" % (setting))
    except TypeError as e:
        raise cmdexc.CommandError(str(e))
    except strconvert.ConversionError as e:
        raise cmdexc.CommandError(str(e))


@commands.register()
def bind(keybinding: str, command: List[str], mode: str = None):
    """Bind keys to a command.

    **syntax:** ``:bind keybinding command [--mode=MODE]``

    positional arguments:
        * ``keybinding``: The keys to bind.
        * ``command``: The command to execute with optional arguments.

    optional arguments:
        * ``mode``: The mode to bind the keybinding in. Default: current.
    """
    mode = Modes.get_by_name(mode) if mode else modehandler.current()
    command = " ".join(command)
    keybindings.bind(keybinding, command, mode)


@commands.register()
def unbind(keybinding: str, mode: str = None):
    """Unbind a keybinding.

    **syntax:** ``:unbind keybinding [--mode=MODE]``

    positional arguments:
        * ``keybinding``: The keybinding to unbind.

    optional arguments:
        * ``mode``: The mode to unbind the keybinding in. Default: current.
    """
    mode = Modes.get_by_name(mode) if mode else modehandler.current()
    keybindings.unbind(keybinding, mode)


@commands.register(mode=Modes.MANIPULATE)
@commands.register(mode=Modes.COMMAND)
@commands.register()
def nop():
    """Do nothing.

    This is useful to remove default keybindings by explicitly binding them to
    nop.
    """
    pass


def init():
    """Initialize config commands."""
    # Currently does not do anything but the commands need to be registered by
    # an import. May become useful in the future.
