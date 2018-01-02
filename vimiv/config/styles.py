# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions dealing with the stylesheet of the Qt widgets.

Module Attributes:
    _styles: Dictionary saving the style settings from the config file, form:
        _styles["image.bg"] = "#000000"
"""

import collections
import configparser
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


def get_current():
    return _styles[_styles.current]


class Style(collections.UserDict):
    """Class defining a single style.

    A python dictionary with a name and overridden __setitem__ for convenience.
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
        super().__setitem__("%s" % (name), item)


def parse():
    """Setup the style.

    Checks for a style name and reads it from file. If the name is default, the
    defaults are simply used and the default style file is written to disk for
    reference.
    """
    name = settings.get_value("style")
    filename = xdg.join_vimiv_config("styles/%s" % (name))
    if name == "default":
        create_default()
        if not os.path.isfile(filename):
            dump("default")
    else:
        read(name)
        _styles.current = name
    replace_referenced_variables()


def store(configsection):
    """Store all styles defined in the STYLES section of the config file."""
    for option, value in configsection.items():
        _styles["{%s}" % (option)] = value


def replace_referenced_variables():
    """Replace referenced variables with the stored value."""
    style = get_current()
    iter_backup = dict(style)
    for option, value in iter_backup.items():
        if value in style:
            style[option] = style[value]


def apply(obj, append=""):
    """Apply stylesheet to an object dereferencing config options.

    Args:
        obj: The QObject to apply the stylesheet to.
        append: Extra string to append to the stylesheet.
    """
    sheet = obj.STYLESHEET + append
    style = get_current()
    for option, value in style.items():
        sheet = sheet.replace(option, value)
    obj.setStyleSheet(sheet)


def get(name):
    style = get_current()
    return style["{%s}" % (name)]


def create_default():
    """Create the default style."""
    default = Style("default")
    # Image
    default["image.bg"] = "#2b303b"
    default["image.scrollbar.width"] = "8px"
    default["image.scrollbar.bg"] = "{image.bg}"
    default["image.scrollbar.fg"] = "#65737e"
    default["image.scrollbar.padding"] = "2px"
    # Library
    default["library.font"] = "10pt Monospace"
    default["library.fg"] = "#dfe1e8"
    default["library.directory.fg"] = "#eff1f5"
    default["library.even.bg"] = "#2b303b"
    default["library.odd.bg"] = "#343d46"
    default["library.selected.bg"] = "#8fa1b3"
    default["library.selected.fg"] = "#eff1f5"
    default["library.scrollbar.width"] = "{image.scrollbar.width}"
    default["library.scrollbar.bg"] = "{image.bg}"
    default["library.scrollbar.fg"] = "{image.scrollbar.fg}"
    default["library.scrollbar.padding"] = "{image.scrollbar.padding}"
    default["library.border"] = "0px solid"
    # Thumbnail
    default["thumbnail.font"] = "{library.font}"
    default["thumbnail.fg"] = "{library.fg}"
    default["thumbnail.bg"] = "{image.bg}"
    default["thumbnail.padding"] = "20"
    default["thumbnail.selected.bg"] = "{library.selected.bg}"
    default["thumbnail.default.bg"] = "{statusbar.info}"
    default["thumbnail.error.bg"] = "{statusbar.error}"
    default["thumbnail.frame.fg"] = "{thumbnail.fg}"
    # Statusbar
    default["statusbar.font"] = "10pt Monospace"
    default["statusbar.bg"] = "#4f5b66"
    default["statusbar.fg"] = "#eff1f5"
    default["statusbar.error"] = "#bf616a"
    default["statusbar.warning"] = "#d08770"
    default["statusbar.info"] = "#96b5b4"
    default["statusbar.message_border"] = "2px solid"
    default["statusbar.padding"] = "4"
    # Completion
    default["completion.height"] = "16em"
    default["completion.fg"] = "{statusbar.fg}"
    default["completion.even.bg"] = "{statusbar.bg}"
    default["completion.odd.bg"] = "{statusbar.bg}"
    default["completion.selected.fg"] = "{library.selected.fg}"
    default["completion.selected.bg"] = "{library.selected.bg}"
    default["completion.scrollbar.width"] = "{image.scrollbar.width}"
    default["completion.scrollbar.bg"] = "{image.scrollbar.bg}"
    default["completion.scrollbar.fg"] = "{image.scrollbar.fg}"
    default["completion.scrollbar.padding"] = "{image.scrollbar.padding}"


def read(name):
    """Read style from styles file.

    Name:
        name of the style to read. Defines the filename to read.
    """
    filename = xdg.join_vimiv_config("styles/%s" % (name))
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


def clear():
    """Delete all styles."""
    _styles.clear()
