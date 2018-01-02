# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
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


def clamp(value, maximum, minimum):
    """Clamp a value so it does not exceed boundaries."""
    if maximum is not None:
        value = min(value, maximum)
    if minimum is not None:
        value = max(value, minimum)
    return value
