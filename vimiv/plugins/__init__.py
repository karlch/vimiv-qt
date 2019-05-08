# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""`Interface to load and initialize plugins`.

Plugins are python modules that are either in ``vimiv/plugins/`` (app plugins) or
``$XDG_DATA_HOME/vimiv/plugins/`` (user plugins). A simple example to get an idea of the
plugin structure is realized in the demo plugin ``vimiv/plugins/demo.py``.

There are three main components a plugin can make use of to interact with vimiv:

* The application api imported via ``from vimiv import api``
* The ``init`` function of the plugin which gets called as soon as the plugin is
  loaded
* The ``cleanup`` function of the plugin which gets called when the vimiv application
  exits.
"""

import importlib
import logging
import os
import sys
from types import ModuleType
from typing import Dict, List

from vimiv.utils import xdg


_app_plugin_directory = os.path.dirname(__file__)
_user_plugin_directory = xdg.join_vimiv_data("plugins")
_plugins: Dict[str, str] = {}  # key: name, value: additional information
_loaded_plugins: Dict[str, ModuleType] = {}  # key:name, value: loaded module


def load() -> None:
    """Load all active plugins."""
    logging.debug("Loading plugins...")
    sys.path.insert(0, _app_plugin_directory)
    sys.path.insert(0, _user_plugin_directory)
    app_plugins = _get_plugins(_app_plugin_directory)
    logging.debug("Available app plugins: %s", ", ".join(app_plugins))
    user_plugins = _get_plugins(_user_plugin_directory)
    logging.debug("Available user plugins: %s", ", ".join(user_plugins))
    for plugin in _plugins:
        if plugin in app_plugins:
            _load_plugin(plugin, _app_plugin_directory)
        elif plugin in user_plugins:
            _load_plugin(plugin, _user_plugin_directory)
        else:
            logging.debug("Unable to find plugin '%s', ignoring", plugin)
    logging.debug("Plugin loading completed")


def cleanup() -> None:
    """Clean up all loaded plugins.

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


def add_plugins(**plugins: str) -> None:
    """Add plugins to the dictionary of plugins.

    Args:
        plugins: Dictionary of plugin names with metadata to add to plugins.
    """
    _plugins.update(plugins)


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
