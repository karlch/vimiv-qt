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


# The registry used to store the vimiv components
_registry = Registry()


def register(name):
    """Store a component in the registry.

    Args:
        name: Name used to identify the component.
    """
    def decorator(component_init):
        """Decorator around the __init__ function of the component."""
        def inside(component, *args, **kwargs):
            # The first argument is always self and can be used to register the
            # component
            if name not in _registry:
                component_init(component, *args, **kwargs)
                _registry[name] = component
                logging.debug("Registered %s in objreg", name)
            else:
                logging.error("%s already registered in objreg", name)
        return inside
    return decorator


def register_object(name, obj):
    """Store an object in the registry."""
    _registry[name] = obj


def get(name):
    """Get a component from the registry.

    Args:
        name: Identifier of the component to receive.
    Return:
        The object in the registry.
    """
    return _registry[name]


def delete(name):
    """Delete one object from the registry."""
    del _registry[name]


def clear():
    """Delete all objects from the registry."""
    _registry.clear()
