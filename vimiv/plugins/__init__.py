# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""`Interface to load and initialize plugins`.

Plugins are python modules that are either in ``vimiv/plugins/`` (app plugins) or
``$XDG_DATA_HOME/vimiv/plugins/`` (user plugins). A possible path is to write a plugin
in its own git repository and let the user to clone that repository into
``$XDG_DATA_HOME/vimiv/plugins/``. It can then be activated in the configuration file.
A simple example to get an idea of the plugin structure is realized in the demo plugin
``vimiv/plugins/demo.py``.

There are three main components a plugin can make use of to interact with vimiv:

* The application api imported via ``from vimiv import api``
* The ``init`` function of the plugin which gets called as soon as the plugin is
  loaded. It receives the information string as first argument which contains the
  additional information supplied by the user in the configuration file after the plugin
  name. This can be used to receive simple information from the user.
* The ``cleanup`` function of the plugin which gets called when the vimiv application
  exits.

.. hint::

    It is considered good practice to add ``*args, **kwargs`` to the ``init`` and
    ``cleanup`` function of any plugin. This allows additional information to be passed
    via these functions at any time without breaking the plugin.

.. note::

    Using any other imports from vimiv besides the api module is not considered stable
    and may break at any point without warning. If you require functionality that is not
    within the api, please open an issue to discuss this. This helps the api grow and
    keeps plugins stable.

.. warning::

    Before the release of version 1.0 there may be changes to the api although it is
    tried to keep them as minimial as possible. Any breaking changes will be announced
    in advance to allow plugins to adapt.

The plugin loading process can be summarized by the following steps:

#. The 'PLUGINS' section of the configuration file is iterated over. Keys defined are
   the names of the plugins that should be loaded later, values can be arbitrary
   additional information.
#. After setting up the main application, the defined plugins are loaded by the
   :func:`load` function. During loading the ``init`` function of the plugin is called.
#. Before the application is quit, the ``cleanup`` function of all loaded plugins is
   called.

----------------------------------------------------------------------------------------

Module Attributes:
    _app_plugin_directory: Directory in which plugins shipped with vimiv are located.
    _user_plugin_directory: Directory in which user-installed plugins are located.
    _plugins: Dictionary mapping plugin names to additional information as defined in
        the configuration file.
    _loaded_plugins: Dictionary mapping loaded plugin names to the loaded python module.
"""

import importlib
import os
import sys
from types import ModuleType
from typing import Dict, List

from vimiv.utils import xdg, log


_app_plugin_directory = os.path.dirname(__file__)
_user_plugin_directory = xdg.vimiv_data_dir("plugins")
_plugins: Dict[str, str] = {
    "print": "default"
}  # key: name, value: additional information
_loaded_plugins: Dict[str, ModuleType] = {}  # key:name, value: loaded module
_logger = log.module_logger(__name__)


def load() -> None:
    """Load plugins defined.

    If no plugins are passed to the function all active plugins are loaded.

    Args:
        plugins: Plugin names to load.
    """
    _logger.debug("Loading plugins...")
    sys.path.insert(0, _app_plugin_directory)
    sys.path.insert(0, _user_plugin_directory)
    app_plugins = _get_plugins(_app_plugin_directory)
    _logger.debug("Available app plugins: %s", ", ".join(app_plugins))
    user_plugins = _get_plugins(_user_plugin_directory)
    _logger.debug("Available user plugins: %s", ", ".join(user_plugins))
    for plugin, info in _plugins.items():
        if plugin in app_plugins:
            _load_plugin(plugin, info, _app_plugin_directory)
        elif plugin in user_plugins:
            _load_plugin(plugin, info, _user_plugin_directory)
        else:
            _logger.debug("Unable to find plugin '%s', ignoring", plugin)
    _logger.debug("Plugin loading completed")


def cleanup() -> None:
    """Clean up all loaded plugins.

    This calls the cleanup function for all loaded plugins and is called before vimiv is
    closed.
    """
    _logger.debug("Cleaning up plugins")
    for name, module in _loaded_plugins.items():
        try:
            # AttributeError is caught afterwards, the module may or may not define
            # cleanup
            module.cleanup()  # type: ignore
            _logger.debug("Cleaned up '%s'", name)
        except AttributeError:
            _logger.debug("Plugin '%s' does not define cleanup()", name)


def add_plugins(**plugins: str) -> None:
    """Add plugins to the dictionary of plugins.

    Args:
        plugins: Dictionary of plugin names with metadata to add to plugins.
    """
    _plugins.update(plugins)


def get_plugins() -> Dict[str, str]:
    """Retrieve dictionary containing active plugin names and additional information."""
    return dict(_plugins)


def _load_plugin(name: str, info: str, directory: str) -> None:
    """Load a single plugin.

    Args:
        name: Name of the plugin as python module.
        info: Additional information string passed to the plugin's init.
        directory: Directory in which the python module is located.
    """
    _logger.debug("Loading plugin '%s' from '%s'", name, directory)
    try:
        module = importlib.import_module(name, directory)
    except (ImportError, SyntaxError) as e:
        log.error("Importing plugin '%s': %s", name, str(e))
        return
    try:
        # AttributeError is caught afterwards, the module may or may not define init
        module.init(info)  # type: ignore
        _logger.debug("Initialized '%s'", name)
    except AttributeError:
        _logger.debug("Plugin '%s' does not define init()", name)
    _logger.debug("Loaded '%s' successfully", name)
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
