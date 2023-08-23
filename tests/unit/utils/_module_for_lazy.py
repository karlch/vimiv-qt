# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

"""Dummy module used for testing the lazy import mechanism."""

print(__name__)  # Side effect we can check for

RETURN_VALUE = 42


def function_of_interest():
    return RETURN_VALUE
