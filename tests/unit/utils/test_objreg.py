# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Tests for vimiv.utils.objreg."""

from vimiv.utils import objreg


class Component:
    """Dummy class to register in the registry."""

    @objreg.register("component-name")
    def __init__(self):
        pass


def test_is_registered(cleansetup):
    Component()  # Register component
    assert isinstance(objreg.get("component-name"), Component)
