#!/usr/bin/env python3

"""Generate reST documentation from source code docstrings."""

import collections
import inspect
import importlib
import os
import sys
import textwrap
from typing import Any, Dict, List, NamedTuple

# Startup is imported to create all the commands and keybindings via their decorators
from vimiv import api, parser, startup  # pylint: disable=unused-import
from vimiv.imutils import immanipulate  # pylint: disable=unused-import
from vimiv.gui import manipulate  # pylint: disable=unused-import

from rstutils import RSTFile


def generate_status_modules():
    """Generate table overview of status modules."""
    print("generating statusbar modules...")
    filename = "docs/documentation/configuration/status_modules.rstsrc"
    with RSTFile(filename) as f:
        rows = [("Module", "Description")]
        for name in sorted(api.status._modules.keys()):
            func = api.status._modules[name]._func
            name = name.strip("{}")
            desc = inspect.getdoc(func).split("\n")[0]
            rows.append((name, desc))
        f.write_table(rows, title="Overview of status modules", widths="30 70")


def _write_command_description(cmds, mode, f):
    """Write description of docstring of commands to documentation file."""
    for name in sorted(cmds.keys()):
        cmd = cmds[name]
        f.write("\n.. _ref_%s_%s:\n\n" % (mode, name))
        f.write_subsubsection(name)
        doc = inspect.getdoc(cmd.func)
        f.write("%s\n\n" % (doc))


def generate_commands():
    """Generate table overview and description of the commands."""
    print("generating commands...")
    with RSTFile("docs/documentation/commands_desc.rstsrc") as f:
        for mode, cmds in api.commands._registry.items():
            f.write_subsection(mode.name.capitalize())
            # Table of command overview
            rows = [("Command", "Description")]
            title = "Overview of %s commands" % (mode.name)
            for name in sorted(cmds.keys()):
                cmd = cmds[name]
                link = ":ref:`ref_%s_%s`" % (mode.name, name)
                rows.append((link, cmd.description))
            f.write_table(rows, title=title, widths="25 75")
            _write_command_description(cmds, mode.name, f)


def generate_settings():
    """Generate table overview of all settings."""
    print("generating settings...")
    filename = "docs/documentation/configuration/settings_table.rstsrc"
    with RSTFile(filename) as f:
        rows = [("Setting", "Description", "Default", "Type")]
        for name in sorted(api.settings._storage.keys()):
            setting = api.settings._storage[name]
            if setting.desc:  # Otherwise the setting is meant to be hidden
                default = str(setting.default)
                if len(default) > 20:  # Cut very long defaults (exif)
                    default = default[:17] + "..."
                rows.append((name, setting.desc, default, setting.typ.__name__))
        f.write_table(rows, title="Overview of settings", widths="20 60 15 5")


def generate_keybindings():
    """Generate table overview of default keybindings."""
    print("generating keybindings...")
    filename = "docs/documentation/configuration/keybindings_table.rstsrc"
    with RSTFile(filename) as f:
        for mode, bindings in api.keybindings.items():
            rows = _gen_keybinding_rows(bindings)
            title = "Keybindings for %s mode" % (mode.name)
            f.write_table(rows, title=title, widths="20 80")


def _gen_keybinding_rows(bindings):
    """Generate rows for keybindings table."""
    header = [("Keybinding", "Command")]
    rows = [(rf"\{binding}", command) for binding, command in bindings]
    return header + rows


def generate_commandline_options():
    """Generate file including the command line options."""

    argparser = parser.get_argparser()
    arguments = _get_arguments(argparser)

    # Synopsis Man Page
    filename_synopsis = "docs/manpage/synopsis.rstsrc"
    with open(filename_synopsis, "w", encoding="utf-8") as f:
        f.write(_generate_synopsis(arguments, emph="*", sep=r"\ \|\ "))

    # Synopsis Documentation
    filename_synopsis = "docs/documentation/cl_options/synopsis.rstsrc"
    with open(filename_synopsis, "w", encoding="utf-8") as f:
        raw_synopsis_doc = _generate_synopsis(arguments)
        synopsis_doc = "\n ".join(textwrap.wrap(raw_synopsis_doc, width=79))
        f.write(f".. code-block::\n\n {synopsis_doc}")

    # Command Listing
    groups = collections.defaultdict(list)
    for arg in arguments:
        groups[arg.group].append(arg)

    # Command Listing Man Page
    filename_options = "docs/manpage/options.rstsrc"
    with RSTFile(filename_options) as f:
        _generate_cli_man(groups, f)

    # Command Listing Documentation
    filename_options = "docs/documentation/cl_options/options.rstsrc"
    with RSTFile(filename_options) as f:
        _generate_cli_doc(groups, f)


class ParserArgument(NamedTuple):
    """Storage class for a single command line argument."""

    group: str
    longname: str
    shortname: str
    metavar: Any
    description: str

    @property
    def is_positional(self):
        return self.longname is self.shortname is None

    def get_names(self, formatter: str) -> List[str]:
        """Retrieve list of long and shortname which are not None."""
        return [
            self._format(name, formatter)
            for name in [self.longname, self.shortname]
            if name is not None
        ]

    def get_metavar(self, formatter: str) -> str:
        """Retrieve metavar."""
        if self.metavar is None:
            return ""
        if isinstance(self.metavar, tuple):
            return " ".join(self._format(e, formatter) for e in self.metavar)
        return self._format(self.metavar, formatter)

    def get_name_metavar(
        self, name_formatter: str, metavar_formatter: str
    ) -> List[str]:
        """Retrieve all not-none names and append metavar."""
        names = self.get_names(name_formatter)
        metavar = self.get_metavar(metavar_formatter)
        lst = names if names else [metavar]
        return [f"{e} {metavar}" if metavar else e for e in lst]

    def _format(self, element: str, formatter: str) -> str:
        """Wrap the element into the format string."""
        return formatter + element + formatter


def _get_arguments(argparser: parser.argparse.ArgumentParser) -> List[ParserArgument]:
    """Retrieve all arguments from the passed argparser.

    Args:
        argparser: Argument parser where the arguments get extracted from.

    Returns:
        List of ParserArgument where each element represents one argument of the parser.
    """

    def argument_from_action(group, action):
        if len(action.option_strings) == 2:
            shortname, longname = action.option_strings
        elif len(action.option_strings) == 1:
            longname = action.option_strings[0]
            shortname = None
        else:
            longname = shortname = None
        return ParserArgument(
            group=group.title,
            longname=longname,
            shortname=shortname,
            metavar=action.metavar,
            description=action.help,
        )

    return [
        argument_from_action(group, action)
        for group in argparser._action_groups
        for action in group._group_actions
    ]


def _generate_synopsis(arguments: List[ParserArgument], emph: str = "", sep="|") -> str:
    """Generate formatted synopsis of vimiv.

    Args:
        arguments: List of instances of ParserArgument.
        emph: Character used for emphasis.
        sep: String used to separate different versions of the same argument, e.g. -o
            and --output.
    Returns:
        Formatted synopsis for the man page.
    """
    emph2 = 2 * emph
    synopsis = f"{emph2}vimiv{emph2}"
    for arg in arguments:
        if arg.is_positional:
            synopsis += f" [{arg.get_metavar(emph2)}]"
        else:
            command = sep.join(arg.get_name_metavar(emph2, emph))
            synopsis += f" [{command}]"
    return synopsis


def _generate_cli_man(groups: Dict[str, List[ParserArgument]], f: RSTFile) -> None:
    """Generate commands listing with man page formatting.

    Args:
        groups: List of ParserArgument sorted by their respective group.
        f: RSTFile to write to.
    """
    for group in groups.keys():
        arguments = groups[group]

        f.write_section(group.upper())
        for arg in arguments:
            if arg.is_positional:
                f.write(f"{arg.get_metavar('**')}\n\n\t{arg.description}\n\n")
            else:
                f.write(f"{', '.join(arg.get_name_metavar('**', '*'))}\n\n")
                f.write(f"\t{arg.description}\n\n")


def _generate_cli_doc(groups: Dict[str, List[ParserArgument]], f: RSTFile) -> None:
    """Generate commands listing with documentation formatting.

    Args:
        groups: List of ParserArgument sorted by their respective group.
        f: RSTFile to write to.
    """
    for group in groups.keys():
        arguments = groups[group]

        rows = [("Command", "Description")]
        for arg in arguments:
            if arg.is_positional:
                name = arg.get_metavar("``")
            else:
                name = ", ".join(f"``{e}``" for e in arg.get_name_metavar("", ""))
            rows.append((name, arg.description))
        f.write_table(rows, title=group.capitalize(), widths="50 50")


def generate_plugins():
    """Generate overview table of default plugins."""
    print("generating default plugins...")

    filename = "docs/documentation/configuration/default_plugins.rstsrc"
    plugins_directory = "vimiv/plugins"
    sys.path.insert(0, plugins_directory)

    plugin_names = sorted(
        [
            filename.replace(".py", "")
            for filename in os.listdir(plugins_directory)
            if not filename.startswith("_") and filename.endswith(".py")
        ]
    )

    def get_plugin_description(name):
        module = importlib.import_module(name, plugins_directory)
        docstring = inspect.getdoc(module)
        return docstring.split("\n")[0].strip(" .")

    rows = [("Name", "Description")]
    for name in plugin_names:
        rows.append((name, get_plugin_description(name)))

    with RSTFile(filename) as f:
        f.write_table(rows, title="Overview of default plugins", widths="20 80")


if __name__ == "__main__":
    generate_status_modules()
    generate_commands()
    generate_settings()
    generate_keybindings()
    generate_commandline_options()
    generate_plugins()
