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

from vimiv import api
from vimiv.utils import xdg, log

from . import read_log_exception


NAME_DEFAULT = "default"
NAME_DEFAULT_DARK = "default-dark"
DEFAULT_FONT = "10pt Monospace"

_style = None
_logger = log.module_logger(__name__)


class Style(dict):
    """Class defining a single style.

    The style is based on 16 colors according to base16.

    A python dictionary with a name and overridden __setitem__ for convenience.
    Ordered so referencing and dereferencing variables is well defined.
    """

    def __init__(self, *colors, font=DEFAULT_FONT):
        """Initialize style with 16 colors for base 16 and a font."""
        # We are mainly storing all the values here
        # pylint: disable=too-many-statements
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
        # Fill in all values
        self["font"] = font
        # Image
        self["image.bg"] = "{base00}"
        self["image.scrollbar.width"] = "8px"
        self["image.scrollbar.bg"] = "{image.bg}"
        self["image.scrollbar.fg"] = "{base03}"
        self["image.scrollbar.padding"] = "2px"
        # Library
        self["library.font"] = "{font}"
        self["library.fg"] = "{base06}"
        self["library.padding"] = "2px"
        self["library.directory.fg"] = "{base07}"
        self["library.even.bg"] = "{base01}"
        self["library.odd.bg"] = "{base01}"
        self["library.selected.bg"] = "{base0d}"
        self["library.selected.fg"] = "{base07}"
        self["library.search.highlighted.fg"] = "{base01}"
        self["library.search.highlighted.bg"] = "{base04}"
        self["library.scrollbar.width"] = "{image.scrollbar.width}"
        self["library.scrollbar.bg"] = "{image.bg}"
        self["library.scrollbar.fg"] = "{image.scrollbar.fg}"
        self["library.scrollbar.padding"] = "{image.scrollbar.padding}"
        self["library.border"] = "0px solid"
        # Statusbar
        self["statusbar.font"] = "{font}"
        self["statusbar.bg"] = "{base02}"
        self["statusbar.fg"] = "{base06}"
        self["statusbar.error"] = "{base08}"
        self["statusbar.warning"] = "{base09}"
        self["statusbar.info"] = "{base0c}"
        self["statusbar.message_border"] = "2px solid"
        self["statusbar.padding"] = "4"
        # Thumbnail
        self["thumbnail.font"] = "{font}"
        self["thumbnail.fg"] = "{library.fg}"
        self["thumbnail.bg"] = "{image.bg}"
        self["thumbnail.padding"] = "20"
        self["thumbnail.selected.bg"] = "{library.selected.bg}"
        self["thumbnail.search.highlighted.bg"] = "{library.search.highlighted.bg}"
        self["thumbnail.default.bg"] = "{statusbar.info}"
        self["thumbnail.error.bg"] = "{statusbar.error}"
        self["thumbnail.frame.fg"] = "{thumbnail.fg}"
        # Completion
        self["completion.height"] = "16em"
        self["completion.fg"] = "{statusbar.fg}"
        self["completion.even.bg"] = "{statusbar.bg}"
        self["completion.odd.bg"] = "{statusbar.bg}"
        self["completion.selected.fg"] = "{library.selected.fg}"
        self["completion.selected.bg"] = "{library.selected.bg}"
        self["completion.scrollbar.width"] = "{image.scrollbar.width}"
        self["completion.scrollbar.bg"] = "{image.scrollbar.bg}"
        self["completion.scrollbar.fg"] = "{image.scrollbar.fg}"
        self["completion.scrollbar.padding"] = "{image.scrollbar.padding}"
        # Keyhint
        self["keyhint.padding"] = "2px"
        self["keyhint.border_radius"] = "10px"
        self["keyhint.suffix_color"] = "{base0c}"
        # Manipulate
        self["manipulate.fg"] = "{statusbar.fg}"
        self["manipulate.focused.fg"] = "{base0c}"
        self["manipulate.bg"] = "{image.bg}"
        self["manipulate.slider.left"] = "{library.selected.bg}"
        self["manipulate.slider.handle"] = "{base04}"
        self["manipulate.slider.right"] = "{statusbar.bg}"
        # Manipulate image overlay
        self["manipulate.image.border"] = "2px solid"
        self["manipulate.image.border.color"] = "{base0c}"
        # Mark
        self["mark.color"] = "{base0e}"
        # Metadata overlay
        self["metadata.bg"] = self["{statusbar.bg}"].replace("#", "#AA")  # Add alpha
        self["metadata.padding"] = "{keyhint.padding}"
        self["metadata.border_radius"] = "{keyhint.border_radius}"

    def __setitem__(self, name, item):
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
    def is_color_option(name: str):
        """Return True if the style option corresponds is a color."""
        return name.endswith((".fg", ".bg"))

    @staticmethod
    def check_valid_color(color: str):
        """Check if a color string is a valid html color.

        Accepts strings that start with # and have 3 or 6 hex digits.

        Raises:
            ValueError if the string is invalid.
        """
        if not re.fullmatch(r"#([0-9a-f]{3}|[0-9a-f]{6})", color.lower()):
            raise ValueError(f"{color} is not a valid html color")


def parse():
    """Setup the style.

    Checks for a style name and reads it from file. If the name is default, the
    defaults are simply used and the default style file is written to disk for
    reference.
    """
    global _style
    name = api.settings.style.value
    _logger.debug("Parsing style '%s'", name)
    filename = xdg.join_vimiv_config("styles/%s" % (name))
    if name == NAME_DEFAULT:
        _style = create_default()
    elif name == NAME_DEFAULT_DARK:
        _style = create_default(dark=True)
    elif os.path.exists(filename):
        _style = read(filename)
    else:
        log.error("Style file '%s' not found, falling back to default", filename)
        _style = create_default()


def apply(obj, append=""):
    """Apply stylesheet to an object dereferencing config options.

    Args:
        obj: The QObject to apply the stylesheet to.
        append: Extra string to append to the stylesheet.
    """
    sheet = obj.STYLESHEET + append
    for option, value in _style.items():
        sheet = sheet.replace(option, value)
    obj.setStyleSheet(sheet)


def get(name):
    """Return style option for a given name."""
    try:
        return _style["{%s}" % (name)]
    except KeyError:
        log.error("Style option '%s' not found, falling back to default", name)
        return ""


def create_default(dark=False, save_to_file=True):
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
    if save_to_file and not os.path.isfile(xdg.join_vimiv_config("styles", name)):
        dump(name, style)
    return style


def read(filename):
    """Read style from styles file.

    Args:
        filename: Name of the styles file to read
    """
    _logger.debug("Reading style from file '%s'", filename)
    parser = configparser.ConfigParser()
    # Retrieve the STYLE section
    try:
        read_log_exception(parser, _logger, filename)
        section = parser["STYLE"]
    except KeyError:
        log.error(
            "Style files must start with the [STYLE] header. Falling back to default."
        )
        return create_default(save_to_file=False)
    # Retrieve base colors
    try:
        colors = [section.pop(f"base{i:02x}") for i in range(16)]
    except KeyError as e:
        log.error("Style is missing color %s. Falling back to default.", e)
        return create_default(save_to_file=False)
    if "font" in section:  # User-defined global font
        style = Style(*colors, font=section.pop("font"))
    else:  # Default global font
        style = Style(*colors)
    # Override additional options
    for option, value in parser["STYLE"].items():
        _logger.debug("Overriding '%s' with '%s'", option, value)
        style[option] = value
    return style


def dump(name, style):
    """Dump style to styles file."""
    filename = xdg.join_vimiv_config("styles", name)
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
