# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""*Storage system for objects*.

The object registry is a storage system for long-lived objects. These objects
are stored and identified using their type. Therefore every stored object must
be unique in its type and only one instance of each type can be stored. It is
mainly used by commands as well as statusbar modules to retrieve the ``self``
argument for methods that require an instance of the class.

To register a new class in the object registry, the
:func:`register` decorator can be used as following::

    from vimiv.api import objreg

    class MyLongLivedClass:

        @objreg.register
        def __init__(self):
            ...

The class is then stored in the object registry once the first instance was
created. To retrieve instance of the class, the :func:`get`
function can be used::

    my_instance = objreg.get(MyLongLivedClass)
"""

import collections
import logging
from typing import Any


def register(component_init):
    """Decorator to store a component in the object registry.

    This decorates the ``__init__`` function of the component to register. The
    object is stored in the registry right after ``__init__`` was called.

    Args:
        component_init: The ``__init__`` function of the component.
    """
    def inside(component, *args, **kwargs):
        """The decorated ``__init__`` function.

        Args:
            component: Corresponds to self.
        """
        component_init(component, *args, **kwargs)
        _registry.store(component)
    return inside


def get(obj_type: type) -> Any:
    """Retrieve a component from the registry.

    Args:
        obj_type: Type of the component to get.
    Return:
        The instance of the object in the registry.
    """
    return _registry[obj_type]


class _Registry(collections.UserDict):
    """Storage class for vimiv components."""

    def store(self, component):
        """Store one component in the registry.

        This is used instead of __setitem__ as the key to store the component
        with can be calculated from the component itself. Calls
        __setitem__(_key(component), component).

        Args:
            component: The object to store.
        """
        key = self._key(component)
        logging.debug("Registering object '%r'", component)
        self[key] = component

    @staticmethod
    def _key(obj):
        """Use object type as unique key to store the object intance."""
        return type(obj)


_registry = _Registry()  # The registry used to store the vimiv components
