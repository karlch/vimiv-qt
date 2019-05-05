# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Plugin utilities and default plugins."""

import importlib
import logging
import os
import sys
from types import ModuleType
from typing import Dict, List

from vimiv.utils import xdg


_app_plugin_directory = os.path.dirname(__file__)
_user_plugin_directory = xdg.join_vimiv_data("plugins")
_active_plugins: List[str] = []
_loaded_plugins: Dict[str, ModuleType] = {}


def load() -> None:
    """Load all active plugins."""
    logging.debug("Loading plugins...")
    sys.path.insert(0, _app_plugin_directory)
    sys.path.insert(0, _user_plugin_directory)
    app_plugins = _get_plugins(_app_plugin_directory)
    logging.debug("Available app plugins: %s", ", ".join(app_plugins))
    user_plugins = _get_plugins(_user_plugin_directory)
    logging.debug("Available user plugins: %s", ", ".join(user_plugins))
    for plugin in _active_plugins:
        if plugin in app_plugins:
            _load_plugin(plugin, _app_plugin_directory)
        elif plugin in user_plugins:
            _load_plugin(plugin, _user_plugin_directory)
        else:
            logging.error("Unable to find plugin '%s'", plugin)
    logging.debug("Plugin loading completed")


def cleanup() -> None:
    """Clean up all active plugins.

    This calls the cleanup function for all loaded plugins and is called before vimiv is
    closed.
    """
    logging.debug("Cleaning up plugins")
    for name, module in _loaded_plugins.items():
        try:
            # AttributeError is caught afterwards, the module may or may not define
            # cleanup
            module.cleanup()  # type: ignore
            logging.debug("Cleaned up '%s'", name)
        except AttributeError:
            logging.debug("Plugin '%s' does not define cleanup()", name)


def set_active_plugins(plugins: List[str]) -> None:
    """Set the list of active plugins."""
    _active_plugins.extend(plugins)


def _load_plugin(name: str, directory: str) -> None:
    """Load a single plugin.

    Args:
        name: Name of the plugin as python module.
        directory: Directory in which the python module is located.
    """
    logging.debug("Loading plugin '%s' from '%s'", name, directory)
    try:
        module = importlib.import_module(name, directory)
    except ImportError as e:
        logging.error("Importing plugin '%s': %s", name, str(e))
        return
    try:
        # AttributeError is caught afterwards, the module may or may not define init
        module.init()  # type: ignore
        logging.debug("Initialized '%s'", name)
    except AttributeError:
        logging.debug("Plugin '%s' does not define init()", name)
    logging.debug("Loaded '%s' successfully", name)
    _loaded_plugins[name] = module


def _get_plugins(directory: str) -> List[str]:
    """Retrieve all plugin names inside a directory."""
    try:
        return sorted(
            path.replace(".py", "")
            for path in os.listdir(directory)
            if _is_plugin(os.path.join(directory, path))
        )
    except FileNotFoundError:
        return []


def _is_plugin(path: str) -> bool:
    """Check if a path is a possible plugin."""
    if os.path.isfile(path):
        is_python_module = path.endswith(".py")
        is_hidden = os.path.basename(path).startswith("_")
        return is_python_module and not is_hidden
    if os.path.isdir(path):
        return "__init__.py" in os.listdir(path)
    return False
