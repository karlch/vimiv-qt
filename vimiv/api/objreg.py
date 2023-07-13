# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""*Storage system for objects*.

The object registry is a storage system for long-lived objects. These objects are stored
and identified using their type. Therefore every stored object must be unique in its
type and only one instance of each type can be stored. Purpose of this registry is to
define an interface used by commands as well as statusbar modules to retrieve the
``self`` argument for methods that require an instance of the class.

To register a new class for this purpose, the
:func:`register` function can be used as following::

    from vimiv.api import objreg

    class MyLongLivedClass:

        def __init__(self):
            ...
            objreg.register(self)

This class is now ready to provide commands and statusbar modules using the regular
decorators. In principle, you can now retrieve the instance of the class via::

    my_instance = MyLongLivedClass.instance

This is not recommended though and considered an implementation detail. The preferred
method is to keep track of the instance otherwise.
"""

import functools
from typing import Any, Callable, Optional

from vimiv.utils import log, is_method, class_that_defined_method
from vimiv.utils.customtypes import AnyT

_logger = log.module_logger(__name__)


def register(arg: Any) -> Optional[Callable]:
    """Register a new instance for the object registry."""
    # New implementation, the class instance must be passed
    if not hasattr(arg, "__code__"):
        component = arg
        cls = component.__class__
        _logger.debug("Registering '%s.%s'", cls.__module__, cls.__qualname__)
        cls.instance = component
        return None

    # Old implementation using register as decorator
    # TODO remove before releasing v1.0.0
    _logger.warning(
        "\nUsing @api.objreg.register as decorator in '%s' is deprecated "
        "and will be removed in v1.0.0.\n"
        "Please use api.objreg.register(self) within the __init__ instead.",
        arg.__module__,
    )

    component_init = arg

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


def _call_with_instance(func: Callable[..., AnyT], *args: Any, **kwargs: Any) -> AnyT:
    """Call function with current objreg instance as self argument if it is a method."""
    cls = __get_class(func)
    if cls is not None:
        return func(cls.instance, *args, **kwargs)
    return func(*args, **kwargs)


@functools.lru_cache(None)
def __get_class(func: Callable) -> Any:
    """Helper method to retrieve the class defining func if any.

    We define this simple wrapper to be able to cache this as it is called for every
    command / status module and should thus be as fast as possible.
    """
    if is_method(func):
        _logger.debug("Retrieving instance from objreg for '%s'", func.__qualname__)
        return class_that_defined_method(func)
    return None
