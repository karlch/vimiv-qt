# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Various small functions that don't really fit into an own module."""

import re


def add_html(tag, text):
    """Surround text in a html tag.

    Args:
        tag: Tag to use, e.g. b.
        text: The text to surround.
    """
    return "<%s>%s</%s>" % (tag, text, tag)


def strip_html(text):
    """Strip all html tags from text.

    strip("<b>hello</b>") = "hello"

    Return:
        The stripped text.
    """
    stripper = re.compile('<.*?>')
    return re.sub(stripper, '', text)


def clamp(value, minimum, maximum):
    """Clamp a value so it does not exceed boundaries."""
    if minimum is not None:
        value = max(value, minimum)
    if maximum is not None:
        value = min(value, maximum)
    return value
