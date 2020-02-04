# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Provides the import_module function for lazy importing."""

import sys
import importlib.util
from functools import lru_cache
from types import ModuleType
from typing import Any, Optional


class Module:
    """Wrapper class for a lazy-loaded module.

    Attributes:
        fullname: Full name of the wrapped module.

        _module: The imported module once loaded.
    """

    def __init__(self, fullname: str):
        self.fullname = fullname
        self._module: Optional[ModuleType] = None

    @classmethod
    @lru_cache(None)
    def factory(cls, fullname: str, *, optional: bool = False) -> Optional["Module"]:
        """Create a new class instance for the module defined by fullname.

        If optional is True, None is returned if the module cannot be found instead of
        raising ModuleNotFoundError. This method is cached so we only create one
        instance per name of a module.
        """
        try:
            found = importlib.util.find_spec(fullname)
        except ModuleNotFoundError:  # Raised when we import e.g. optional.submodule
            found = None
        if found is None:
            if optional:
                return None
            raise ModuleNotFoundError(f"No module named '{fullname}'")
        return cls(fullname)

    @property
    def module(self) -> ModuleType:
        """The imported wrapped module."""
        if self._module is None:
            self._module = importlib.import_module(self.fullname)
        return self._module

    def __getattr__(self, name: str) -> Any:
        """Retrieve attributes from the wrapped module."""
        return getattr(self.module, name)

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}({self.fullname})"


def import_module(fullname: str, *, optional: bool = False) -> Any:
    """Lazy import a module by its full name.

    If the module was already imported, returns it from sys.modules. Otherwise returns a
    lazy Module instance. See Module.factory for the creation details.
    """
    try:
        return sys.modules[fullname]
    except KeyError:
        return Module.factory(fullname, optional=optional)
