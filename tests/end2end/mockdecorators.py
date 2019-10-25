# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Module to patch vimiv decorators before import."""

from unittest import mock

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
        # Mark instance is stored as a global variable in api
        if "Mark" not in cls.__qualname__:
            cls.instance = None


mock.patch("vimiv.utils.cached_method", lambda x: x).start()
mock.patch("vimiv.api.objreg.register", mockregister).start()
