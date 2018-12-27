#!/usr/bin/env python3

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.
# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

"""Generate reST documentation from source code docstrings."""

import inspect

# Used to generate list of commands and statusbar modules
import vimiv.startup  # pylint: disable=unused-import
from vimiv.commands import commands
from vimiv.config import settings
from vimiv.gui import statusbar

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


if __name__ == "__main__":
    generate_statusbar_modules()
    generate_commands()
    generate_settings()
