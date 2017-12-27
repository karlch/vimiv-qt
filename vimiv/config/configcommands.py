# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.
"""Commands dealing with settings and configuration."""

from vimiv.commands import commands, cmdexc
from vimiv.config import settings, keybindings
from vimiv.utils import strconvert


@keybindings.add(".", "set slideshow.delay +0.5", mode="image")
@keybindings.add(",", "set slideshow.delay -0.5", mode="image")
@keybindings.add("H", "set library.width -20", mode="library")
@keybindings.add("L", "set library.width +20", mode="library")
@keybindings.add("b", "set statusbar.show!")
@commands.argument("value", nargs="*")
@commands.argument("setting")
@commands.register()
def set(setting, value=None):  # pylint: disable=redefined-builtin
    """Set an option.

    Args:
        setting: Name of the setting to set.
        value: Value to set the setting to.
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


def init():
    """Initialize config commands."""
    # Currently does not do anything but the commands need to be registered by
    # an import. May become useful in the future.
