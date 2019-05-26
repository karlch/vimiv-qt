# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Commands dealing with settings and configuration."""

from typing import List

from vimiv import api


@api.keybindings.register("sl", "set slideshow.delay +0.5", mode=api.modes.IMAGE)
@api.keybindings.register("sh", "set slideshow.delay -0.5", mode=api.modes.IMAGE)
@api.keybindings.register("H", "set library.width -0.05", mode=api.modes.LIBRARY)
@api.keybindings.register("L", "set library.width +0.05", mode=api.modes.LIBRARY)
@api.keybindings.register("b", "set statusbar.show!")
@api.commands.register()
def set(name: str, value: List[str]):  # pylint: disable=redefined-builtin
    """Set an option.

    **syntax:** ``:set name [value]``

    positional arguments:
        * ``name``: Name of the setting to set.
        * ``value``: Value to set the setting to. If not given, set to default.
    """
    strvalue = " ".join(value)  # List comes from nargs='*'
    try:
        # Toggle boolean settings
        if name.endswith("!"):
            name = name.rstrip("!")
            api.settings.toggle(name)
        # Add to number settings
        elif strvalue and (strvalue.startswith("+") or strvalue.startswith("-")):
            api.settings.add_to(name, strvalue)
        # Set default
        elif strvalue == "":
            api.settings.set_to_default(name)
        else:
            api.settings.override(name, strvalue)
    except KeyError:
        raise api.commands.CommandError("unknown setting %s" % (name))
    except TypeError as e:
        raise api.commands.CommandError(str(e))
    except ValueError as e:
        raise api.commands.CommandError(str(e))


@api.commands.register()
def bind(keybinding: str, command: List[str], mode: str = None):
    """Bind keys to a command.

    **syntax:** ``:bind keybinding command [--mode=MODE]``

    positional arguments:
        * ``keybinding``: The keys to bind.
        * ``command``: The command to execute with optional arguments.

    optional arguments:
        * ``mode``: The mode to bind the keybinding in. Default: current.
    """
    modeobj = api.modes.get_by_name(mode) if mode else api.modes.current()
    api.keybindings.bind(keybinding, " ".join(command), modeobj)


@api.commands.register()
def unbind(keybinding: str, mode: str = None):
    """Unbind a keybinding.

    **syntax:** ``:unbind keybinding [--mode=MODE]``

    positional arguments:
        * ``keybinding``: The keybinding to unbind.

    optional arguments:
        * ``mode``: The mode to unbind the keybinding in. Default: current.
    """
    modeobj = api.modes.get_by_name(mode) if mode else api.modes.current()
    api.keybindings.unbind(keybinding, modeobj)


@api.commands.register(mode=api.modes.MANIPULATE)
@api.commands.register(mode=api.modes.COMMAND)
@api.commands.register()
def nop():
    """Do nothing.

    This is useful to remove default keybindings by explicitly binding them to
    nop.
    """


def init():
    """Initialize config commands."""
    # Currently does not do anything but the commands need to be registered by
    # an import. May become useful in the future.
