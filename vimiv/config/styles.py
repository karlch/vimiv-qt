# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions dealing with the stylesheet of the Qt widgets.

Module Attributes:
    NAME_DEFAULT: Name of the default theme.
    NAME_DEFAULT_DARK: Name of the dark default theme.
    DEFAULT_FONT: Default font to use if none is given by the user.

    _style: Dictionary saving the style settings from the config file, form:
        _style["image.bg"] = "#000000"
"""

import configparser
import os
import re
import sys
from typing import cast

from vimiv import api
from vimiv.utils import xdg, log, customtypes

from . import read_log_exception, external_configparser
from ._style_options import DEFAULT_OPTIONS


NAME_DEFAULT = "default"
NAME_DEFAULT_DARK = "default-dark"
DEFAULT_FONT = "10pt Monospace"

_style = cast("Style", None)
_logger = log.module_logger(__name__)


class Style(dict):
    """Class defining a single style.

    The style is based on 16 colors according to base16.

    A python dictionary with a name and overridden __setitem__ for convenience.
    Ordered so referencing and dereferencing variables is well defined.
    """

    def __init__(self, *colors: str, font: str = DEFAULT_FONT):
        """Initialize style with 16 colors for base 16 and a font."""
        super().__init__()
        _logger.debug(
            "Initializing style with colors:\n%s\nfont: %s", "\n".join(colors), font
        )
        # Initialize the colorscheme from base16
        if len(colors) != 16:
            raise ValueError("Styles must be created with 16 colors for base16")
        for i, color in enumerate(colors):
            self.check_valid_color(color)
            self[f"base{i:02x}"] = color
        # Fill in all default values
        self["font"] = font
        for key, value in DEFAULT_OPTIONS.items():
            self[key] = value
        # Add values with alpha channel that require special handling
        self["library.selected.bg.unfocus"] = self.add_alpha(self["{base0d}"], "88")
        self["thumbnail.selected.bg.unfocus"] = self["{library.selected.bg.unfocus}"]
        self["metadata.bg"] = self.add_alpha(self["{statusbar.bg}"], "AA")

    def __setitem__(self, name: str, item: str):
        """Store item automatically surrounding the name with {} if needed."""
        assert isinstance(name, str), "Style options must be strings."
        assert isinstance(item, str), "Style values must be strings."
        if not name.startswith("{"):
            name = "{%s}" % (name)
        if item in self:
            super().__setitem__(name, self[item])
        else:
            if self.is_color_option(name):
                self.check_valid_color(item)
            super().__setitem__(name, item)

    @staticmethod
    def is_color_option(name: str) -> bool:
        """Return True if the style option name corresponds to a color."""
        return name.strip("{}").endswith((".fg", ".bg", ".color"))

    @staticmethod
    def check_valid_color(color: str):
        """Check if a color string is a valid html color.

        Accepts strings that start with # and have 6 (#RRGGBB) or 8 (#AARRGGBB) hex
        digits.

        Raises:
            ValueError if the string is invalid.
        """
        if not re.fullmatch(r"#([0-9a-f]{6}|[0-9a-f]{8})", color.lower()):
            raise ValueError(
                f"{color} is not a valid html color. "
                "Supported formats are #RRGGBB and #AARRGGBB."
            )

    @staticmethod
    def add_alpha(color: str, alpha: str) -> str:
        """Add alpha channel to color if it is not there already."""
        assert len(alpha) == 2, "Require 2 characters to define alpha"
        return color.replace("#", f"#{alpha}") if len(color) == 7 else color


def abspath(name: str) -> str:
    """Return absolute path to style file from style name."""
    return xdg.vimiv_config_dir("styles", name)


def parse():
    """Setup the style.

    Checks for a style name and reads it from file. If the name is default, the
    defaults are simply used and the default style file is written to disk for
    reference.
    """
    global _style
    name = api.settings.style.value
    _logger.debug("Parsing style '%s'", name)
    filename = abspath(name)
    if name == NAME_DEFAULT:
        _style = create_default()
    elif name == NAME_DEFAULT_DARK:
        _style = create_default(dark=True)
    elif os.path.exists(filename):
        _style = read(filename)
    else:
        log.error("Style file '%s' not found, falling back to default", filename)
        _style = create_default()


def apply(obj, append: str = ""):
    """Apply stylesheet to an object dereferencing config options.

    Args:
        obj: The QObject to apply the stylesheet to.
        append: Extra string to append to the stylesheet.
    """
    sheet = obj.STYLESHEET + append
    for option, value in _style.items():
        sheet = sheet.replace(option, value)
    obj.setStyleSheet(sheet)


def get(name: str) -> str:
    """Return style option for a given name."""
    try:
        return _style["{%s}" % (name)]
    except KeyError:
        log.error("Style option '%s' not found, falling back to default", name)
        return ""


def create_default(dark: bool = False, save_to_file: bool = True) -> Style:
    """Create the default style.

    Args:
        dark: Create the default dark style instead.
        save_to_file: Dump the default style to file for reading and reference.
    """
    _logger.debug("Creating default style")
    # Color definitions
    # Uses base16 tomorrow
    # Thanks to https://github.com/chriskempson/base16-tomorrow-scheme/
    if dark:
        style = Style(
            "#1d1f21",  # base00
            "#282a2e",  # base01
            "#373b41",  # base02
            "#969896",  # base03
            "#b4b7b4",  # base04
            "#c5c8c6",  # base05
            "#e0e0e0",  # base06
            "#ffffff",  # base07
            "#cc6666",  # base08
            "#de935f",  # base09
            "#f0c674",  # base0a
            "#b5bd68",  # base0b
            "#8abeb7",  # base0c
            "#81a2be",  # base0d
            "#b294bb",  # base0e
            "#a3685a",  # base0f
        )
        name = NAME_DEFAULT_DARK
    else:
        style = Style(
            "#ffffff",  # base00
            "#e0e0e0",  # base01
            "#d6d6d6",  # base02
            "#8e908c",  # base03
            "#969896",  # base04
            "#4d4d4c",  # base05
            "#282a2e",  # base06
            "#1d1f21",  # base07
            "#c82829",  # base08
            "#f5871f",  # base09
            "#eab700",  # base0a
            "#718c00",  # base0b
            "#3e999f",  # base0c
            "#81a2be",  # base0d
            "#8959a8",  # base0e
            "#a3685a",  # base0f
        )
        name = NAME_DEFAULT
    if save_to_file and not os.path.isfile(abspath(name)):
        dump(name, style)
    return style


def read(path: str) -> Style:
    """Read style from styles file.

    Args:
        path: Name of the styles file to read
    """
    _logger.debug("Reading style from file '%s'", path)
    parser = external_configparser.get_parser()
    read_log_exception(parser, _logger, path)
    # Retrieve the STYLE section
    try:
        section = parser["STYLE"]
    except KeyError:
        _crash_read(path, "Style files must start with the [STYLE] header")
    # Retrieve base colors
    try:
        colors = [section.pop(f"base{i:02x}") for i in range(16)]
    except KeyError as e:
        _crash_read(path, f"Style is missing requred base color {e}")
    # Create style class with possibly user-defined font
    try:
        style = Style(*colors, font=section.pop("font", DEFAULT_FONT))
    except ValueError as e:
        _crash_read(path, str(e))
    # Override additional options
    for option, value in parser["STYLE"].items():
        _logger.debug("Overriding '%s' with '%s'", option, value)
        try:
            style[option] = value
        except ValueError as e:
            _logger.error(
                "Error parsing style option '%s' = '%s':\n%s", option, value, e
            )
    return style


def dump(name: str, style: Style):
    """Dump style to styles file."""
    filename = abspath(name)
    xdg.makedirs(os.path.dirname(filename))
    _logger.debug("Dumping style to file '%s'", filename)
    parser = configparser.ConfigParser()
    parser.add_section("STYLE")
    for option, value in style.items():
        option = option.strip("{}")
        parser["STYLE"][option] = value
    with open(filename, "w") as f:
        f.write(
            "; This file is a reference for creating own styles."
            " It will never be read.\n"
            "; To change values, copy this file using a new name and"
            " set the style setting\n; in vimiv.conf to that name.\n"
        )
        parser.write(f)
        f.write("; vim:ft=dosini")


def _crash_read(path: str, message: str):
    """Crash consistently on critical errors when reading user styles."""
    _logger.error(
        "Error reading styles file '%s':\n\n%s\n\nPlease fix the file :)", path, message
    )
    sys.exit(customtypes.Exit.err_config)
