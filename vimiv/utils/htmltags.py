# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Functions to manipulate html tags of text."""

import re



def add(tag, text):
    """Surround text in a html tag.

    Args:
        tag: Tag to use, e.g. b.
        text: The text to surround.
    """
    return "<%s>%s</%s>" % (tag, text, tag)


def strip(text):
    """Strip all html tags from text.

    strip("<b>hello</b>") = "hello"

    Return:
        The stripped text.
    """
    stripper = re.compile('<.*?>')
    return re.sub(stripper, '', text)
