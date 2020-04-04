# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions to format and retrieve text for the :help command."""

from contextlib import suppress

import vimiv
from vimiv import api
from vimiv.utils import log, add_html


@api.commands.register(mode=api.modes.MANIPULATE, name="help")
@api.commands.register(name="help")
def help_command(topic: str) -> None:
    """Show help on a command or setting.

    **syntax:** ``:help topic``

    positional arguments:
        * ``topic``: Either a valid :command or a valid setting name.

    .. hint:: For commands ``help :command`` is the same as ``command -h``.
    """
    topic = topic.lower().lstrip(":")
    general_topics = {
        "vimiv": _general_help,
        "wildcards": _wildcard_help,
    }
    with suppress(KeyError):
        return general_topics[topic]()
    with suppress(api.commands.CommandNotFound):
        command = api.commands.get(topic, mode=api.modes.current())
        # This raises an exception and leaves this command
        command(["-h"], "")
    with suppress(KeyError):
        return _setting_help(api.settings.get(topic))
    raise api.commands.CommandError(f"Unknown topic '{topic}'")


def _general_help() -> None:
    """Display general vimiv information."""
    log.info(
        "%s: %s\n\n"
        "Website: %s\n\n"
        "For an overview of keybindings, run :keybindings.\n"
        "To retrieve help on a command or setting run :help topic.",
        vimiv.__name__,
        vimiv.__description__,
        vimiv.__url__,
    )


def _setting_help(setting: api.settings.Setting) -> None:
    """Display information on this setting."""
    log.info(
        "%s: %s\n\nType: %s\nDefault: %s\nSuggestions: %s",
        setting.name,
        setting.desc,
        setting,
        setting.default,
        ", ".join(setting.suggestions()),
    )


def _wildcard_help() -> None:
    """Display information on various wildcards and their usage."""

    def format_table_row(wildcard: str, description: str) -> str:
        return (
            "<tr>"
            f"<td>{wildcard}</td>"
            f"<td style='padding-left: 2ex'>{description}</td>"
            "</tr>"
        )

    description = (
        "Symbols used to refer to paths or path-lists within vimiv. "
        "These work in addition to the standard unix-shell wildcards * and ?."
    )
    # TODO retrieve wildcards from commands module so we do not need to store them twice
    wildcards = (
        ("%", "currently focused path or image"),
        ("%f", "all paths in the current file list"),
        ("%m", "all marked paths"),
    )
    table = add_html("\n".join(format_table_row(w, d) for w, d in wildcards), "table")
    _format_help(title="wildcards", description=description, text=table)


def _format_help(*, title: str, description: str, text: str) -> None:
    header = add_html(title.capitalize(), "h3")
    log.info("%s\n%s<br>%s<br>", header, description, text)
