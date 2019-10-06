# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Methods to read keybindings from file and store them."""

import configparser

from vimiv import api
from vimiv.utils import log

from . import read_log_exception, parse_config


_logger = log.module_logger(__name__)


def parse(cli_path: str):
    """Parse keybindings from the keys.conf into the keybindings registry."""
    parse_config(cli_path, "keys.conf", read, dump)


def dump(path: str):
    """Write default keybindings to keys file at path."""
    with open(path, "w") as f:
        get_default_parser().write(f)
    _logger.debug("Created default keys file '%s'", path)


def get_default_parser() -> configparser.ConfigParser:
    """Retrieve configparser with default keybindings."""
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
    return parser


def read(path: str) -> None:
    """Read keybindings from path into the keybindings registry."""
    _logger.debug("Reading keybindings from '%s'", path)
    parser = KeyfileParser()
    read_log_exception(parser, _logger, path)
    for mode, bindings in api.keybindings.items():
        try:
            section = parser[mode.name.upper()]
            _update_bindings(bindings, section)
        except KeyError:
            _logger.debug("Missing section '%s' in keys.conf", mode.name.upper())
    _logger.debug("Read keybindings from '%s'", path)


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
