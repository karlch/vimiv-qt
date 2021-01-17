# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Methods to read keybindings from file and store them."""

import configparser
from typing import Iterable, Tuple

from vimiv import api, config
from vimiv.utils import log


_logger = log.module_logger(__name__)

DEL_BINDING_COMMAND = "unbind"


def parse(cli_path: str):
    """Parse keybindings from the keys.conf into the keybindings registry."""
    config.parse_config(cli_path, "keys.conf", read, dump)
    api.keybindings.check()


def dump(path: str):
    """Write default keybindings to keys file at path."""
    with open(path, "w") as f:
        get_default_parser().write(f)
    _logger.debug("Created default keys file '%s'", path)


def get_default_parser() -> configparser.ConfigParser:
    """Retrieve configparser with default keybindings."""
    parser = KeyfileParser(delimiters=":")
    # Add default bindings
    for mode, bindings in api.keybindings.items():
        parser.add_section(mode.name.upper())
        for binding, command in bindings:
            parser[mode.name.upper()][binding] = command.replace("%", "%%")
    return parser


def read(path: str) -> None:
    """Read keybindings from path into the keybindings registry."""
    _logger.debug("Reading keybindings from '%s'", path)
    parser = KeyfileParser()
    config.read_log_exception(parser, _logger, path)
    for section in parser.sections():
        try:
            _logger.debug("Reading keybindings from section '%s'", section)
            mode = api.modes.get_by_name(section)
            _read_mode(bindings=parser[section].items(), mode=mode)
        except api.modes.InvalidMode:
            _logger.warning("Ignoring bindings for unknown '%s' mode", section)
    _logger.debug("Read keybindings from '%s'", path)


def _read_mode(bindings: Iterable[Tuple[str, str]], mode: api.modes.Mode):
    """Read bindings for one mode into the keybindings registry."""
    for keybinding, command in bindings:
        if command == DEL_BINDING_COMMAND:
            _delete_binding(keybinding, mode)
        else:
            api.keybindings.bind(keybinding, command, mode)
            _logger.debug(
                "Read keybinding '%s': '%s' for mode '%s'",
                keybinding,
                command,
                mode.name,
            )


def _delete_binding(keybinding: str, mode: api.modes.Mode):
    """Remove a keybinding for this specific mode."""
    try:
        api.keybindings.unbind(keybinding, mode)
    except api.commands.CommandError:
        _logger.warning(
            "Cannot unbind '%s' for mode '%s', no binding found.", keybinding, mode.name
        )


class KeyfileParser(configparser.ConfigParser):
    """Parser used for keyfiles.

    Same as configparser.ConfigParser but case sensitive for options.
    """

    def optionxform(self, optionstr):
        """Override so the parser becomes case sensitive."""
        return optionstr
