# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

"""Module to patch vimiv decorators before import."""

import contextlib
import unittest.mock

_known_classes = set()


def mockregister(component_init):
    """Patch api.objreg.register to additionally store the known classes."""

    def inside(component, *args, **kwargs) -> None:
        component.__class__.instance = component
        _known_classes.add(component.__class__)
        component_init(component, *args, **kwargs)

    return inside


def mockregister_cleanup():
    for cls in _known_classes:
        # Instances stored as a global variable
        if cls.__qualname__ not in ("Mark", "ExternalRunner"):
            cls.instance = None


@contextlib.contextmanager
def apply():
    """Contextmanager to mock relevant vimiv decorators and restore state."""
    with unittest.mock.patch("vimiv.api.objreg.register", mockregister):
        yield
