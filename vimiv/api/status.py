# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""*Utilities to add status modules and retrieve status text*.

Status objects in vimiv, e.g. the statusbar displayed at the bottom, are
configurable using so called status modules. These are created using the
:func:`module` decorator.  As an example let's create a module that returns the
name of the current user::

        from vimiv.api import status

        @status.module("{username}")
        def username():
            return os.getenv("USER")

A new module '{username}' is now registered.

Any status object can retrieve the content of statusbar modules by calling
:func:`evaluate`. To get the content of our new "{username}" module prepended
by the text "user: " we run::

    updated_text = status.evaluate("user: {username}")

The occurance of '{username}' is then replaced by the outcome of the username()
function defined earlier.

If any other object requires the status to be updated, they should call
:func:`vimiv.api.status.update` passing the reason for the requested update as string.
"""

import functools
import re
from typing import Callable, TypeVar, Any, Dict

from PyQt5.QtCore import pyqtSignal, QObject

from vimiv.utils import cached_method, is_method, class_that_defined_method, log


Module = Callable[[], str]
# Module function is either a function with no arguments or a method which takes self
ModuleFunc = TypeVar("ModuleFunc", Callable[[], str], Callable[[Any], str])


_modules: Dict[str, "_Module"] = {}  # Dictionary storing all status modules
_module_expression = re.compile(r"\{.*?\}")  # Expression to match all status modules
_logger = log.module_logger(__name__)


class _Module:
    """Class to store function of one status module."""

    def __init__(self, func: Callable[..., str]):
        self._func = func

    def __call__(self) -> str:
        func = self._create_func(self._func)
        return func()

    def __repr__(self) -> str:
        return f"StatusModule('{self._func.__name__}')"

    @cached_method
    def _create_func(self, func: Callable[..., str]) -> Module:
        """Create function to call for a status module.

        This retrieves the instance of a class object for methods and sets it
        as first argument (the 'self' argument) of a lambda. For standard
        functions nothing is done.

        Returns:
            A function to be called without arguments.
        """
        _logger.debug("Creating function for status module '%s'", func.__name__)
        if is_method(func):
            cls = class_that_defined_method(func)
            return functools.partial(func, cls.instance)
        return func


def module(name: str) -> Callable[[ModuleFunc], ModuleFunc]:
    """Decorator to register a function as status module.

    The decorated function must return a string that can be displayed as
    status. When calling :func:`evaluate`, any occurance of ``name`` will be
    replaced by the return value of the decorated function.

    Args:
        name: Name of the module as set in the config file. Must start with '{'
            and end with '}' to allow differentiating modules from ordinary
            text.
    """

    def decorator(function: ModuleFunc) -> ModuleFunc:
        """Store function executable under module name."""
        if not name.startswith("{") or not name.endswith("}"):
            raise ValueError(
                f"Invalid name '{name}' for status module {function.__name__}"
            )
        _modules[name] = _Module(function)
        return function

    return decorator


def evaluate(text: str) -> str:
    """Evaluate the status modules and update text accordingly.

    Replaces all occurances of module names with the output of the
    corresponding function.

    Example:
        A module called {pwd} is associated with the function os.pwd. Assuming
        the output of os.pwd() is "/home/user/folder", the text 'Path: {pwd}'
        becomes 'Path: /home/user/folder'.

    Args:
        text: The text to evaluate.
    Returns:
        The updated text.
    """
    modules = _module_expression.findall(text)
    for module_name in modules:
        try:
            text = text.replace(module_name, _modules[module_name]())
        except KeyError:
            text = text.replace(module_name, "")
            _log_unknown_module(module_name)
    return text


@functools.lru_cache(None)
def _log_unknown_module(module_name: str) -> None:
    """Display log warning for unknown module.

    The lru_cache is used so each module is only logged once, not on every evaluation of
    the status text.

    Args:
        module_name: Module string that is unknown.
    """
    log.warning("Disabling unknown statusbar module '%s'", module_name)


class _Signals(QObject):
    """Simple QObject containing the update signal.

    Signals:
        update: Emitted when the status should be updated.
        clear: Emitted when any messages should be cleared.
    """

    update = pyqtSignal()
    clear = pyqtSignal()


signals = _Signals()


def update(reason: str = "") -> None:
    """Emit signal to update the current status.

    This function can be called when an update of the status is required. It
    is, for example, always called after a command was run.

    Args:
        reason: Reason of the update for logging.
    """
    if not reason:
        # TODO remove in v0.5.0
        _logger.warning("Not passing a reason to status.update is deprecated")
    _logger.debug("Updating status: %s", reason)
    signals.update.emit()


def clear(reason: str = "") -> None:
    """Emit signal to clear messages.

    This function can be called when any temporary logging messages should be cleared.

    Args:
        reason: Reason of the clearing for logging.
    """
    if not reason:
        # TODO remove in v0.5.0
        _logger.warning("Not passing a reason to status.clear is deprecated")
    _logger.debug("Clearing status messages: %s", reason)
    signals.clear.emit()
