# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Storage system for objects.

The components stored here are interfaced in various places all over the code
and stay alive for a longer period of time.
"""

import collections
import logging


class Registry(collections.UserDict):
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
        logging.debug("Registering object '%s'", component)
        self[key] = component

    @staticmethod
    def _key(obj):
        return type(obj)


# The registry used to store the vimiv components
_registry = Registry()


def register(component_init):
    """Store a component in the registry.

    Decorator around the __init__ function of the component.

    Args:
        component_init: The __init__ function of the component.
    """
    def inside(component, *args, **kwargs):
        """The decorated __init__ function.

        Args:
            component: Corresponds to self.
        """
        component_init(component, *args, **kwargs)
        _registry.store(component)
    return inside


def register_object(obj):
    """Store an object in the registry."""
    _registry.store(obj)


def get(obj):
    """Get a component from the registry.

    Args:
        name: Identifier of the component to receive.
    Return:
        The object in the registry.
    """
    return _registry[obj]
