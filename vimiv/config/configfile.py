# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions to read configurations from config file and update settings."""

import configparser
import logging
import os

from vimiv import api, plugins
from vimiv.commands import aliases
from vimiv.utils import xdg


def parse(args):
    """Parse configuration files.

    This reads settings from user config file and possibly the file given from
    the commandline. If the user config file does not exist, a default file is
    created.

    Args:
        args: Arguments returned from parser.parse_args().
    """
    user_file = xdg.join_vimiv_config("vimiv.conf")
    files = []
    if not os.path.isfile(user_file):  # Create default config file
        dump()
    else:
        files.append(user_file)
    if args.config is not None:
        files.append(args.config)
    if files:
        _read(files)
        logging.debug("Read configuration from %s", ", ".join(files))


def dump():
    """Write default configurations to config file."""
    parser = configparser.ConfigParser()
    # Add default options
    for name, setting in api.settings.items():
        section, option = _get_section_option(name)
        if section not in parser:
            parser.add_section(section)
        default = str(setting.default)
        parser[section][option] = default
    # Add default plugins
    parser.add_section("PLUGINS")
    parser["PLUGINS"] = plugins.get_plugins()
    # Write to file
    user_file = xdg.join_vimiv_config("vimiv.conf")
    with open(user_file, "w") as f:
        parser.write(f)
        f.write("; vim:ft=dosini")
    logging.debug("Created default config file %s", user_file)


def _read(files):
    """Read config from list of files into settings.

    The files given first are overridden by the files given later.

    Args:
        files: List of paths for config files to read.
    """
    parser = _setup_parser()
    parser.read(files)
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


def _update_setting(name, parser):
    """Update one setting from the values in the config parser.

    Args:
        name: Name of the setting to update.
        parser: configparser.ConfigParser object.
    """
    section, option = _get_section_option(name)
    try:
        parser_option = parser.get(section, option)
        setting_name = "%s.%s" % (section.lower(), option)
        setting_name = setting_name.replace("general.", "")
        setting = api.settings.get(setting_name)
        logging.debug("Setting '%s' to '%s'", setting_name, parser_option)
        setting.value = parser_option
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        logging.debug("%s in configfile", str(e))
    except ValueError as e:
        logging.error("Error reading setting %s: %s", setting_name, str(e))


def _add_statusbar_formatters(configsection):
    """Add optional statusbar formatters if they are in the config.

    Args:
        configsection: STATUSBAR section in the config file.
    """
    positions = ["left", "center", "right"]
    possible = ["%s_%s" % (p, m.name) for p in positions for m in api.modes.ALL]
    for name, value in configsection.items():
        if name in possible:
            api.settings.StrSetting("statusbar.%s" % (name), value)


def _setup_parser():
    """Setup config file parser."""
    parser = configparser.ConfigParser()
    return parser


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
            logging.error("Reading aliases from config: %s", str(e))


def _read_plugins(pluginsection):
    """Set plugins from configuration file as requested plugins.

    Args:
        pluginsection: PLUGINS section in the config file.
    """
    logging.debug("Plugins in config: %s", ", ".join(pluginsection))
    plugins.add_plugins(**pluginsection)
