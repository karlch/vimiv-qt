# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""TODO"""

import logging

from vimiv.utils import (objreg, cached_method, is_method,
                         class_that_defined_method)


_modules = {}


class InvalidModuleNameError(Exception):
    """Exception raised if the name of a statusbar module is invalid."""


class Module():
    """Class to store function of one statusbar module."""

    def __init__(self, func):
        self._initialized = False
        self._func = func

    def __call__(self):
        func = self._create_func(self._func)
        return func()

    def __repr__(self):
        return "StatusbarModule('%s')" % (self._func.__name__)

    @cached_method
    def _create_func(self, func):
        """Create function to call for a statusbar module.

        This retrieves the instance of a class object for methods and sets it
        as first argument (the 'self' argument) of a lambda. For standard
        functions nothing is done.

        Returns:
            A function to be called without arguments.
        """
        logging.debug("Creating function for statusbar module '%s'",
                      func.__name__)
        if is_method(func):
            cls = class_that_defined_method(func)
            instance = objreg.get(cls)
            return lambda: func(instance)
        return func


def module(name):
    """Decorator to register a command as a statusbar module.

    Args:
        name: Name of the module as set in the config file.
    """
    def decorator(function):
        """Store function executable under module name."""
        if not name.startswith("{") or not name.endswith("}"):
            message = "Invalid name '%s' for statusbar module %s" % (
                name, function.__name__)
            raise InvalidModuleNameError(message)
        _modules[name] = Module(function)

        def inner(*args):
            """Run the function."""
            return function(*args)
        return inner

    return decorator


def evaluate(text):
    """Evaluate modules and update text accordingly.

    Replaces all occurances of module names with the output of the
    corresponding function.

    Example:
        A module called {pwd} is associated with the function os.pwd. Assuming
        the output of os.pwd() is "/home/foo/bar", the text 'Path: {pwd}'
        becomes 'Path: /home/foo/bar'.

    Args:
        text: The text to evaluate.
    Return:
        The updated text.
    """
    for name, mod in _modules.items():
        if name in text:
            text = text.replace(name, mod())
    return text
