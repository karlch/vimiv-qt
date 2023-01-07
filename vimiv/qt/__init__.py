# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Wrapper module around qt to support various python wrapper versions."""

import importlib
import enum


class WRAPPERS(enum.Enum):
    PyQt5 = "PyQt5"


WRAPPER = None


def _autoselect_wrapper():
    """Select a python Qt wrapper version based on availability and enum order."""
    for wrapper in WRAPPERS:
        try:
            importlib.import_module(wrapper.value)
            print(f"Successfully selected Qt wrapper: '{wrapper.value}'")
            return wrapper
        except ImportError:
            print(f"Qt wrapper '{wrapper.value}' not found")
    options = ", ".join(wrapper.value for wrapper in WRAPPERS)
    raise ImportError(f"No valid Qt wrapper found. Valid options: {options}")


WRAPPER = WRAPPER if WRAPPER else _autoselect_wrapper()

USE_PYQT5 = WRAPPER == WRAPPERS.PyQt5
