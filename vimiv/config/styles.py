# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions dealing with the stylesheet of the Qt widgets.

Module Attributes:
    _styles: Dictionary saving the style settings from the config file, form:
        _styles["image.bg"] = "#000000"
"""

import collections
import configparser
import logging
import os

from vimiv.config import settings
from vimiv.utils import xdg


class Styles(collections.UserDict):
    """Class to store all styles.

    Attributes:
        current: Name of the currently used style.
    """

    def __init__(self):
        super().__init__()
        self.current = "default"


_styles = Styles()


def current():
    return _styles[_styles.current]


class Style(collections.OrderedDict):
    """Class defining a single style.

    A python dictionary with a name and overridden __setitem__ for convenience.
    Ordered so referencing and dereferencing variables is well defined.
    """

    def __init__(self, name):
        super().__init__()
        _styles[name] = self

    def __setitem__(self, name, item):
        """Store item automatically surrounding the name with {} if needed."""
        assert isinstance(name, str), "Style options must be strings."
        assert isinstance(item, str), "Style values must be strings."
        if not name.startswith("{"):
            name = "{%s}" % (name)
        if item in self:
            super().__setitem__(name, self[item])
        else:
            super().__setitem__(name, item)


def parse():
    """Setup the style.

    Checks for a style name and reads it from file. If the name is default, the
    defaults are simply used and the default style file is written to disk for
    reference.
    """
    name = settings.get_value(settings.Names.STYLE)
    filename = xdg.join_vimiv_config("styles/%s" % (name))
    if name in ["default", "default-dark"]:
        create_default()
        create_default_dark()
    elif os.path.exists(filename):
        read(name, filename)
    else:
        logging.error("style file '%s' does not exist", filename)
        logging.info("falling back to default style")
        name = "default"
        create_default()
    _styles.current = name


def store(configsection):
    """Store all styles defined in the STYLES section of the config file."""
    for option, value in configsection.items():
        _styles["{%s}" % (option)] = value


def apply(obj, append=""):
    """Apply stylesheet to an object dereferencing config options.

    Args:
        obj: The QObject to apply the stylesheet to.
        append: Extra string to append to the stylesheet.
    """
    sheet = obj.STYLESHEET + append
    style = current()
    for option, value in style.items():
        sheet = sheet.replace(option, value)
    obj.setStyleSheet(sheet)


def get(name):
    """Return style option for a given name."""
    style = current()
    try:
        return style["{%s}" % (name)]
    except KeyError:
        logging.error("Style option '%s' not found, falling back to default",
                      name)
        return ""


def create_default():
    """Create the default style."""
    default = Style("default")
    # Color definitions
    # Uses base16 tomorrow
    # Thanks to https://github.com/chriskempson/base16-tomorrow-scheme/
    default["base00"] = "#ffffff"
    default["base01"] = "#e0e0e0"
    default["base02"] = "#d6d6d6"
    default["base03"] = "#8e908c"
    default["base04"] = "#969896"
    default["base05"] = "#4d4d4c"
    default["base06"] = "#282a2e"
    default["base07"] = "#1d1f21"
    default["base08"] = "#c82829"
    default["base09"] = "#f5871f"
    default["base0a"] = "#eab700"
    default["base0b"] = "#718c00"
    default["base0c"] = "#3e999f"
    default["base0d"] = "#81a2be"
    default["base0e"] = "#8959a8"
    default["base0f"] = "#a3685a"
    # Insert style
    _insert_values(default)
    # Dump
    if not os.path.isfile(xdg.join_vimiv_config("styles/default")):
        dump("default")


def create_default_dark():
    """Create the default dark style."""
    default_dark = Style("default-dark")
    # Color definitions
    # Uses base16 tomorrow-night
    # Thanks to https://github.com/chriskempson/base16-tomorrow-scheme/
    default_dark["base00"] = "#1d1f21"
    default_dark["base01"] = "#282a2e"
    default_dark["base02"] = "#373b41"
    default_dark["base03"] = "#969896"
    default_dark["base04"] = "#b4b7b4"
    default_dark["base05"] = "#c5c8c6"
    default_dark["base06"] = "#e0e0e0"
    default_dark["base07"] = "#ffffff"
    default_dark["base08"] = "#cc6666"
    default_dark["base09"] = "#de935f"
    default_dark["base0a"] = "#f0c674"
    default_dark["base0b"] = "#b5bd68"
    default_dark["base0c"] = "#8abeb7"
    default_dark["base0d"] = "#81a2be"
    default_dark["base0e"] = "#b294bb"
    default_dark["base0f"] = "#a3685a"
    # Insert style
    _insert_values(default_dark)
    # Dump
    if not os.path.isfile(xdg.join_vimiv_config("styles/default-dark")):
        dump("default-dark")


def _insert_values(style):
    """Insert all style values into a default style.

    Args:
        style: The Style object to insert values into.
    """
    # We are only storing all the values here
    # pylint: disable=too-many-statements
    # Image
    style["image.bg"] = "{base00}"
    style["image.scrollbar.width"] = "8px"
    style["image.scrollbar.bg"] = "{image.bg}"
    style["image.scrollbar.fg"] = "{base03}"
    style["image.scrollbar.padding"] = "2px"
    # Library
    style["library.font"] = "10pt Monospace"
    style["library.fg"] = "{base06}"
    style["library.directory.fg"] = "{base07}"
    style["library.even.bg"] = "{base01}"
    style["library.odd.bg"] = "{base01}"
    style["library.selected.bg"] = "{base0d}"
    style["library.selected.fg"] = "{base07}"
    style["library.search.highlighted.fg"] = "{base01}"
    style["library.search.highlighted.bg"] = "{base04}"
    style["library.scrollbar.width"] = "{image.scrollbar.width}"
    style["library.scrollbar.bg"] = "{image.bg}"
    style["library.scrollbar.fg"] = "{image.scrollbar.fg}"
    style["library.scrollbar.padding"] = "{image.scrollbar.padding}"
    style["library.border"] = "0px solid"
    # Thumbnail
    style["thumbnail.font"] = "{library.font}"
    style["thumbnail.fg"] = "{library.fg}"
    style["thumbnail.bg"] = "{image.bg}"
    style["thumbnail.padding"] = "20"
    style["thumbnail.selected.bg"] = "{library.selected.bg}"
    style["thumbnail.search.highlighted.bg"] = \
        "{library.search.highlighted.bg}"
    style["thumbnail.default.bg"] = "{statusbar.info}"
    style["thumbnail.error.bg"] = "{statusbar.error}"
    style["thumbnail.frame.fg"] = "{thumbnail.fg}"
    # Statusbar
    style["statusbar.font"] = "10pt Monospace"
    style["statusbar.bg"] = "{base02}"
    style["statusbar.fg"] = "{base07}"
    style["statusbar.error"] = "{base08}"
    style["statusbar.warning"] = "{base09}"
    style["statusbar.info"] = "{base0c}"
    style["statusbar.message_border"] = "2px solid"
    style["statusbar.padding"] = "4"
    # Completion
    style["completion.height"] = "16em"
    style["completion.fg"] = "{statusbar.fg}"
    style["completion.even.bg"] = "{statusbar.bg}"
    style["completion.odd.bg"] = "{statusbar.bg}"
    style["completion.selected.fg"] = "{library.selected.fg}"
    style["completion.selected.bg"] = "{library.selected.bg}"
    style["completion.scrollbar.width"] = "{image.scrollbar.width}"
    style["completion.scrollbar.bg"] = "{image.scrollbar.bg}"
    style["completion.scrollbar.fg"] = "{image.scrollbar.fg}"
    style["completion.scrollbar.padding"] = "{image.scrollbar.padding}"
    # Manipulate
    style["manipulate.fg"] = "{statusbar.fg}"
    style["manipulate.focused.fg"] = "{base0c}"
    style["manipulate.bg"] = "{image.bg}"
    style["manipulate.bar.bg"] = "{statusbar.bg}"
    style["manipulate.bar.fg"] = "{library.selected.bg}"
    style["manipulate.bar.border"] = "0px solid"


def read(name, filename):
    """Read style from styles file.

    Args:
        name: Name of the style.
        filename: Name of the styles file to read
    """
    parser = configparser.ConfigParser()
    parser.read(filename)
    style = Style(name)
    for option, value in parser["STYLE"].items():
        style[option] = value
    _styles[name] = style


def dump(name):
    """Dump style to styles file."""
    filename = xdg.join_vimiv_config("styles/%s" % (name))
    parser = configparser.ConfigParser()
    parser.add_section("STYLE")
    style = _styles[name]
    for option, value in style.items():
        option = option.strip("{}")
        parser["STYLE"][option] = value
    with open(filename, "w") as f:
        f.write("; This file is a reference for creating own styles."
                " It will never be read.\n"
                "; To change values, copy this file using a new name and"
                " set the style setting\n; in vimiv.conf to that name.\n")
        parser.write(f)
        f.write("; vim:ft=dosini")
