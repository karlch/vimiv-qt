# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Methods to read keybindings from file and store them."""

import configparser
import logging
import os

from vimiv.config import keybindings
from vimiv.utils import xdg


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
    parser = KeyfileParser(delimiters=":")
    # Add sections
    parser.add_section("GLOBAL")
    parser.add_section("IMAGE")
    parser.add_section("LIBRARY")
    parser.add_section("THUMBNAIL")
    parser.add_section("MANIPULATE")
    parser.add_section("COMMAND")
    # Add default bindings
    for mode, bindings in keybindings.items():
        for binding, command in bindings.items():
            parser[mode.upper()][binding] = command.replace("%","%%")
    # Write to file
    user_file = xdg.join_vimiv_config("keys.conf")
    with open(user_file, "w") as f:
        parser.write(f)
    logging.info("Created default keys file %s", user_file)


def _read(filename):
    """Read keybindings in one file into the keybindings registry.

    Args:
        filename: Name of the keybinding file to read.
    """
    parser = KeyfileParser()
    parser.read(filename)
    for mode, bindings in keybindings.items():
        section = parser[mode.upper()]
        _update_bindings(bindings, section)
    logging.info("Read keybindings from '%s'", filename)


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
