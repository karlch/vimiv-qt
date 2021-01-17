# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions to format and retrieve text for the :help command."""

import contextlib

import vimiv
from vimiv import api
from vimiv.commands import wildcards
from vimiv.utils import log, add_html, format_html_table


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
    with contextlib.suppress(KeyError):
        return general_topics[topic]()
    with contextlib.suppress(api.commands.CommandNotFound):
        return _command_help(api.commands.get(topic, mode=api.modes.current()))
    with contextlib.suppress(KeyError):
        return _setting_help(api.settings.get(topic))
    raise api.commands.CommandError(f"Unknown topic '{topic}'")


def _general_help() -> None:
    """Display general vimiv information."""
    text = (
        f"<br>Website: {vimiv.__url__}<br><br>"
        "For an overview of keybindings, run :keybindings.<br>"
        "To retrieve help on a command, setting or other topic run :help topic."
    )
    _format_help(title=vimiv.__name__, description=vimiv.__description__, text=text)


# TODO Expose a public command class so the pylint suppression is no longer required
def _command_help(
    command: api.commands._Command,  # pylint: disable=protected-access
) -> None:
    """Display information on this command."""
    description = command.long_description.replace("\n", "<br>")
    _format_help(title=command.name, description=description)


def _setting_help(setting: api.settings.Setting) -> None:
    """Display information on this setting."""
    suggestions = ", ".join(setting.suggestions())
    content = [
        ("type", str(setting)),
        ("default", setting.default),
    ]
    if suggestions:
        content.append(("suggestions", suggestions))
    table = format_html_table(content)
    _format_help(title=setting.name, description=setting.desc, text=table)


def _wildcard_help() -> None:
    """Display information on various wildcards and their usage."""

    description = (
        "Symbols used to refer to paths or path-lists within vimiv. "
        "These work in addition to the standard unix-shell wildcards * and ?."
    )
    table = format_html_table(
        (wildcard.wildcard, wildcard.description) for wildcard in wildcards.INTERNAL
    )
    _format_help(title="wildcards", description=description, text=table)


def _format_help(*, title: str, description: str, text: str = None) -> None:
    """Helper function to unify formatting of help texts."""
    header = add_html(title, "h3")
    text = f"{text}<br>" if text is not None else ""
    log.info("%s\n%s<br>%s", header, description, text)
