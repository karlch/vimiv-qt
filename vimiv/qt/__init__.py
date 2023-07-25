# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Wrapper module around qt to support various python wrapper versions."""

import importlib
import enum
import os


class WRAPPERS(enum.Enum):
    """List of supported python Qt wrappers.

    Order matters as this is the order in which we check for them being installed if the
    wrapper is not defined by the user explicitly.
    """

    PyQt5 = "PyQt5"
    PyQt6 = "PyQt6"
    PySide6 = "PySide6"


_WRAPPERS_PYQT = [WRAPPERS.PyQt5, WRAPPERS.PyQt6]
_WRAPPER_NAMES = [wrapper.value for wrapper in WRAPPERS]
_WRAPPER_NAMES_STR = ", ".join(_WRAPPER_NAMES)

WRAPPER = None


def _select_wrapper():
    """Select a python Qt wrapper version based on environment variable and fallback."""
    env_var = "QT_SELECT"
    env_wrapper = os.environ.get(env_var)

    if env_wrapper is None:
        return _autoselect_wrapper()

    # Maps QT version number to corresponding wrapper
    # TODO extend 6 to include PySide6 once also included in _autoselect_wrapper()
    num_to_wrapper = {"5": WRAPPERS.PyQt5.value, "6": WRAPPERS.PyQt6.value}

    env_wrapper = num_to_wrapper.get(env_wrapper, env_wrapper)

    if env_wrapper not in _WRAPPER_NAMES:
        raise ImportError(
            f"Unknown wrapper {env_wrapper} set via environment variable {env_var}.\n"
            f"Valid options: {_WRAPPER_NAMES_STR}"
        )

    try:
        importlib.import_module(env_wrapper)
    except ImportError:
        raise ImportError(
            f"Could not import {env_wrapper} set via environment variable {env_var}.\n"
            f"Please install {env_wrapper} or use a different wrapper."
        )

    return WRAPPERS(env_wrapper)


def _autoselect_wrapper():
    """Select a python Qt wrapper version based on availability and enum order.

    We do not auto-detect PySide6 yet, as there are still multiple issues.
    """
    for wrapper in _WRAPPERS_PYQT:
        try:
            importlib.import_module(wrapper.value)
            return wrapper
        except ImportError:  # Raise later
            pass
    raise ImportError(f"No valid Qt wrapper found. Valid options: {_WRAPPER_NAMES_STR}")


WRAPPER = _select_wrapper()

USE_PYQT5 = WRAPPER == WRAPPERS.PyQt5
USE_PYQT6 = WRAPPER == WRAPPERS.PyQt6
USE_PYSIDE6 = WRAPPER == WRAPPERS.PySide6
