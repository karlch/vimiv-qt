#!/usr/bin/env python3

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.
# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

"""Generate reST documentation from source code docstrings."""

import inspect

from vimiv import vimiv
from vimiv.commands import commands
from vimiv.config import settings, keybindings
from vimiv.gui import statusbar
from vimiv.utils import objreg

import rstutils


def generate_statusbar_modules():
    """Generate table overview of statusbar modules."""
    print("generating statusbar modules...")
    filename = "docs/documentation/configuration/statusbar_modules.rstsrc"
    with open(filename, "w") as f:
        rstutils.write_header(f)
        rows = [("Module", "Description")]
        for name in sorted(statusbar._modules.keys()):
            func = statusbar._modules[name]._func
            name = name.strip("{}")
            desc = inspect.getdoc(func).split("\n")[0]
            rows.append((name, desc))
        rstutils.write_table(rows, f, title="Overview of statusbar modules")


def _write_command_description(cmds, mode, f):
    """Write description of docstring of commands to documentation file."""
    for name in sorted(cmds.keys()):
        cmd = cmds[name]
        f.write("\n.. _ref_%s_%s:\n\n" % (mode, name))
        rstutils.write_subsubsection(name, f)
        doc = inspect.getdoc(cmd.func)
        f.write("%s\n\n" % (doc))


def generate_commands():
    """Generate table overview and description of the commands."""
    print("generating commands...")
    with open("docs/documentation/commands_desc.rstsrc", "w") as f:
        rstutils.write_header(f)
        for mode, cmds in commands.registry.items():
            rstutils.write_subsection(mode.name.capitalize(), f)
            # Table of command overview
            rows = [("Command", "Description")]
            title = "Overview of %s commands" % (mode.name)
            for name in sorted(cmds.keys()):
                cmd = cmds[name]
                link = ":ref:`ref_%s_%s`" % (mode.name, name)
                rows.append((link, cmd.description))
            rstutils.write_table(rows, f, title=title)
            _write_command_description(cmds, mode.name, f)


def generate_settings():
    """Generate table overview of all settings."""
    print("generating settings...")
    settings.init_defaults()
    filename = "docs/documentation/configuration/settings_table.rstsrc"
    with open(filename, "w") as f:
        rstutils.write_header(f)
        rows = [("Setting", "Description")]
        for name in sorted(settings._storage.keys()):
            setting = settings._storage[name]
            if setting.desc:  # Otherwise the setting is meant to be hidden
                rows.append((name, setting.desc))
        rstutils.write_table(rows, f, title="Overview of settings")


def generate_keybindings():
    """Generate table overview of default keybindings."""
    print("generating keybindings...")
    filename = "docs/documentation/configuration/keybindings_table.rstsrc"
    with open(filename, "w") as f:
        rstutils.write_header(f)
        for mode, bindings in keybindings.items():
            rows = _gen_keybinding_rows(bindings)
            title = "Keybindings for %s mode" % (mode.name)
            rstutils.write_table(rows, f, title=title)


def _gen_keybinding_rows(bindings):
    """Generate rows for keybindings table."""
    rows = [("Keybinding", "Command")]
    for binding, command in bindings.items():
        rows.append(("\%s" % (binding), command))
    return rows


def generate_commandline_options():
    """Generate file including the command line options."""
    parser = vimiv.get_argparser()
    optionals, positionals, titles = _get_options(parser)
    # Synopsis
    filename_synopsis = "docs/manpage/synopsis.rstsrc"
    with open(filename_synopsis, "w") as f:
        synopsis_options = ["[%s]" % (title) for title in titles]
        synopsis = "**vimiv** %s" % (" ".join(synopsis_options))
        f.write(synopsis)
    # Options
    filename_options = "docs/manpage/options.rstsrc"
    with open(filename_options, "w") as f:
        rstutils.write_header(f)
        rstutils.write_section("positional arguments", f)
        f.write(positionals)
        rstutils.write_section("optional arguments", f)
        f.write(optionals)


def _get_options(parser):
    """Retrieve the options from the argument parser.

    Returns:
        optionals: Formatted string of optional arguments.
        positionals: Formatted string of positional arguments.
        titles: List containing all argument titles.
    """
    optionals = ""
    positionals = ""
    titles = []
    for action in parser._optionals._actions:
        if not action.option_strings:
            positionals += _format_positional(action, titles)
        else:
            optionals += _format_optional(action, titles)
    return optionals, positionals, titles


def _format_optional(action, titles):
    """Format optional argument neatly.

    Args:
        action: The argparser action.
        titles: List of titles to update with the title(s) of this argument.
    Returns:
        Formatted string of this argument.
    """
    _titles = _format_optional_title(action)
    titles.extend(_titles)
    title = ", ".join(_titles)
    desc = action.help
    return _format_option(title, desc)


def _format_positional(action, titles):
    """Format positional argument neatly.

    Args:
        action: The argparser action.
        titles: List of titles to update with the title of this argument.
    Returns:
        Formatted string of this argument.
    """
    title = "**%s**" % (action.metavar)
    titles.append(title)
    desc = action.help
    return _format_option(title, desc)


def _format_option(title, desc):
    """Format an option neatly.

    Args:
        title: The title of this option.
        desc: The help description of this option.
    """
    return "%s\n\n    %s\n\n" % (title, desc)


def _format_optional_title(action):
    """Format the title of an optional argument neatly.

    The title depends on the number of arguments this action requires.

    Args:
        action: The argparser action.
    Returns:
        Formatted title string of this argument.
    """
    formats = []
    for option in action.option_strings:
        if isinstance(action.metavar, str):  # One argument
            title = "**%s** *%s*" % (option, action.metavar)
        elif isinstance(action.metavar, tuple):  # Multiple arguments
            elems = ["*%s*" % (elem) for elem in action.metavar]
            title = "**%s** %s" % (option, " ".join(elems))
        else:  # No arguments
            title = "**%s**" % (option)
        formats.append(title)
    return formats


def generate_module(filename, obj):
    """Generate file from module docstring meant for website documentation."""
    print("generating module for", obj.__name__)
    docstr = inspect.getdoc(obj).split("//")[-1]
    with open(filename, "w") as f:
        rstutils.write_header(f)
        f.write(docstr)


if __name__ == "__main__":
    generate_statusbar_modules()
    generate_commands()
    generate_settings()
    generate_keybindings()
    generate_commandline_options()
    generate_module("docs/documentation/objreg.rstsrc", objreg)
    generate_module("docs/documentation/commands.rstsrc", commands)
    generate_module("docs/documentation/keybindings.rstsrc", keybindings)
    generate_module("docs/documentation/statusbar.rstsrc", statusbar)
