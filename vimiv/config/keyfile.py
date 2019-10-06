# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Methods to read keybindings from file and store them."""

import configparser
import os

from vimiv import api
from vimiv.utils import xdg, log

from . import read_log_exception


_logger = log.module_logger(__name__)


def parse(args):
    """Parse keybindings from the keys.conf into the keybindings registry.

    This reads keybindings from user keys file and possibly the file given from
    the commandline. If the user keys file does not exist, a default file is
    created.

    Args:
        args: Arguments returned from parser.parse_args().
    """
    keyfile = xdg.join_vimiv_config("keys.conf")
    if args.keyfile is not None:  # Read from commandline keys file
        _read(args.keyfile)
    elif os.path.isfile(keyfile):  # Read from keys file
        _read(keyfile)
    else:  # Create defaults
        dump()


def dump():
    """Write default keybindings to keys file."""
    _logger.debug("Dumping default keybindings to file")
    parser = KeyfileParser(delimiters=":")
    # Add sections
    parser.add_section("GLOBAL")
    parser.add_section("IMAGE")
    parser.add_section("LIBRARY")
    parser.add_section("THUMBNAIL")
    parser.add_section("MANIPULATE")
    parser.add_section("COMMAND")
    # Add default bindings
    for mode, bindings in api.keybindings.items():
        for binding, command in bindings.items():
            parser[mode.name.upper()][binding] = command.replace("%", "%%")
    # Write to file
    user_file = xdg.join_vimiv_config("keys.conf")
    with open(user_file, "w") as f:
        parser.write(f)
    _logger.debug("Created default keys file '%s'", user_file)


def _read(filename):
    """Read keybindings in one file into the keybindings registry.

    Args:
        filename: Name of the keybinding file to read.
    """
    _logger.debug("Reading keybindings from '%s'", filename)
    parser = KeyfileParser()
    read_log_exception(parser, _logger, filename)
    for mode, bindings in api.keybindings.items():
        try:
            section = parser[mode.name.upper()]
            _update_bindings(bindings, section)
        except KeyError:
            _logger.debug("Missing section '%s' in keys.conf", mode.name.upper())
    _logger.debug("Read keybindings from '%s'", filename)


class KeyfileParser(configparser.ConfigParser):
    """Parser used for keyfiles.

    Same as configparser.ConfigParser but case sensitive for options.
    """

    def optionxform(self, optionstr):
        """Override so the parser becomes case sensitive."""
        return optionstr


def _update_bindings(bindings, section):
    """Update keybindings dictionary with values from config section.

    The section corresponds to one mode and the bindings dictionary is the
    corresponding dictionary.

    Args:
        bindings: The keybindings dictionary to update.
        section: Section in keys.conf file to read keysbindings from.
    """
    for keybinding, command in section.items():
        bindings[keybinding] = command
        _logger.debug(
            "Read keybinding '%s': '%s' for mode '%s'",
            keybinding,
            command,
            section.name,
        )
