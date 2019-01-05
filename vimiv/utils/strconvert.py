# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions to convert strings to different types."""


class ConversionError(Exception):
    """Raised if a string cannot be converted to the expected type."""

    def __init__(self, text, value):
        """Call the parent with a generalized message.

        Args:
            text: String that was supposed to be converted.
            value: String name of the python type that could not be converted.
        """
        message = "Cannot convert %s to %s" % (text, value)
        super().__init__(message)


def is_str(function):
    """Simple decorator to check if the argument passed is of type str."""
    def inner(text, *args, **kwargs):
        """Decorated function.

        Args:
            text: The text to be converted.
        """
        message = "Must be converting str, not %s" % (type(text))
        assert isinstance(text, str), message
        return function(text, *args, **kwargs)
    return inner


@is_str
def to_bool(text):
    """Convert text to bool."""
    text = text.lower()
    if text in ["yes", "true", "1"]:
        return True
    if text in ["no", "false", "0"]:
        return False
    raise ConversionError(text, "bool")


@is_str
def to_int(text, allow_sign=False):
    """Convert text to int."""
    try:
        int_val = int(text)
    except ValueError:
        raise ConversionError(text, "int")
    if int_val < 0 and not allow_sign:
        raise ValueError("Negative numbers not allowed")
    return int_val


@is_str
def to_float(text, allow_sign=False):
    """Convert text to float."""
    try:
        float_val = float(text)
    except ValueError:
        raise ConversionError(text, "float")
    if float_val < 0 and not allow_sign:
        raise ValueError("Negative numbers not allowed")
    return float_val
