# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions to read configurations from config file and update settings."""

import configparser
import re

from vimiv import api, plugins
from vimiv.commands import aliases
from vimiv.config import read_log_exception, parse_config, external_configparser
from vimiv.utils import log, quotedjoin


_logger = log.module_logger(__name__)


def parse(cli_path: str) -> None:
    """Parse settings from the vimiv.conf into the settings api."""
    parse_config(cli_path, "vimiv.conf", read, dump)


def dump(path: str) -> None:
    """Write default configurations to config file at path."""
    with open(path, "w") as f:
        get_default_parser().write(f)
    _logger.debug("Created default configuration file '%s'", path)


def get_default_parser() -> configparser.ConfigParser:
    """Retrieve configparser with default values."""
    parser = configparser.ConfigParser()
    # Add default options
    for name, setting in api.settings.items():
        section, option = _get_section_option(name)
        if section not in parser:
            parser.add_section(section)
        default = str(setting.default)
        parser[section][option] = default
    # Add default plugins and aliases section
    parser.add_section("PLUGINS")
    parser["PLUGINS"] = plugins.get_plugins()
    parser.add_section("ALIASES")
    # Only write the individual key sets, not the current keyset as the first of the
    # individual options is chosen as the current one
    del parser["METADATA"]["current_keyset"]
    parser["METADATA"].update(
        {f"keys{num:d}": value for num, value in api.settings.metadata.keysets.items()}
    )
    return parser


def read(path: str) -> None:
    """Read config from path into settings."""
    parser = external_configparser.get_parser()
    read_log_exception(parser, _logger, path)
    # Try to update every single setting
    for name, _ in api.settings.items():
        _update_setting(name, parser)
    # Read additional statusbar formatters
    if "STATUSBAR" in parser:
        _add_statusbar_formatters(parser["STATUSBAR"])
    # Read aliases
    if "ALIASES" in parser:
        _add_aliases(parser["ALIASES"])
    # Read plugins
    if "PLUGINS" in parser:
        _read_plugins(parser["PLUGINS"])
    # Read metadata sets
    if "METADATA" in parser:
        _add_metadata(parser["METADATA"])
    _logger.debug("Read configuration from '%s'", path)


def _update_setting(name, parser):
    """Update one setting from the values in the config parser.

    Args:
        name: Name of the setting to update.
        parser: configparser.ConfigParser object.
    """
    section, option = _get_section_option(name)
    try:
        parser_option = parser.get(section, option)
        setting_name = f"{section}.{option}".lower()
        setting_name = setting_name.replace("general.", "")
        setting = api.settings.get(setting_name)
        _logger.debug("Updating '%s' with '%s'", setting_name, parser_option)
        setting.value = parser_option
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        _logger.debug("%s in configfile", str(e))
    except ValueError as e:
        _logger.error("Error reading setting %s: %s", setting_name, str(e))


def _add_statusbar_formatters(configsection):
    """Add optional statusbar formatters if they are in the config.

    Args:
        configsection: STATUSBAR section in the config file.
    """
    positions = ("left", "center", "right")
    possible = [
        f"{position}_{mode.name}" for position in positions for mode in api.modes.ALL
    ]
    for name, value in configsection.items():
        if name in possible:
            _logger.debug("Adding statusbar formatter '%s' with '%s'", name, value)
            api.settings.StrSetting(f"statusbar.{name}", value)


def _get_section_option(name):
    """Return the section and the option name for config file of a setting.

    Args:
        name: Name of the setting in the settings storage.
    Returns:
        section: Name of the section in the config file of the setting.
        option: Name of the option in the config file of the setting.
    """
    if "." not in name:
        name = "general." + name
    split = name.split(".")
    section = split[0].upper()
    option = split[1]
    return section, option


def _add_aliases(configsection):
    """Add optional aliases defined in the alias section to AliasRunner.

    Args:
        configsection: ALIASES section in the config file.
    """
    for name, command in configsection.items():
        try:
            aliases.alias(name, [command], "global")
        except api.commands.CommandError as e:
            log.error("Reading aliases from config: %s", str(e))


def _read_plugins(pluginsection):
    """Set plugins from configuration file as requested plugins.

    Args:
        pluginsection: PLUGINS section in the config file.
    """
    _logger.debug("Plugins in config: %s", quotedjoin(pluginsection))
    plugins.add_plugins(**pluginsection)


def _add_metadata(configsection):
    """Set available metadata sets from config file.

    Args:
        configsection: METADATA section in the config file.
    """
    for name, value in configsection.items():
        match = re.search(r"keys(\d+)", name)
        if match:
            number = int(match.group(1))
            api.settings.metadata.keysets[number] = value
            _logger.debug("Keyset %d: '%s' found", number, value)
    if len(api.settings.metadata.keysets) > 0:
        api.settings.metadata.current_keyset.value = api.settings.metadata.keysets[
            min(api.settings.metadata.keysets.keys())
        ]
