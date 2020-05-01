# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""*Storage system for objects*.

The object registry is a storage system for long-lived objects. These objects are stored
and identified using their type. Therefore every stored object must be unique in its
type and only one instance of each type can be stored. Purpose of this registry is to
define an interface used by commands as well as statusbar modules to retrieve the
``self`` argument for methods that require an instance of the class.

To register a new class for this purpose, the
:func:`register` decorator can be used as following::

    from vimiv.api import objreg

    class MyLongLivedClass:

        @objreg.register
        def __init__(self):
            ...

This class is now ready to provide commands and statusbar modules using the regular
decorators. In principle, you can now retrieve the instance of the class via::

    my_instance = MyLongLivedClass.instance

This is not recommended though and considered an implementation detail. The preferred
method is to keep track of the instance otherwise.
"""

import functools
from typing import Any, Callable

from vimiv.utils import log, is_method, class_that_defined_method

_logger = log.module_logger(__name__)


def register(component_init: Callable) -> Callable:
    """Decorator to register a class for the object registry.

    This decorates the ``__init__`` function of the class to register. The object is
    stored in the registry right after ``__init__`` was called.

    Args:
        component_init: The ``__init__`` function of the component.
    """

    def inside(component: Any, *args: Any, **kwargs: Any) -> None:
        """The decorated ``__init__`` function.

        Args:
            component: Corresponds to self.
        """
        cls = component.__class__
        _logger.debug("Registering '%s.%s'", cls.__module__, cls.__qualname__)
        cls.instance = component
        component_init(component, *args, **kwargs)

    return inside


@functools.lru_cache(None)
def _apply_instance(func: Callable) -> Callable:
    """Apply instance as self argument to func if func is a method."""
    if is_method(func):
        _logger.debug(
            "Applying self from instance in objreg to '%s'", func.__qualname__
        )
        cls = class_that_defined_method(func)
        return functools.partial(func, cls.instance)
    return func
