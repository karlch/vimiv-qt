# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils.lazy."""

import functools
import sys

import pytest

from vimiv.utils import lazy

MODULE_NAME = "_module_for_lazy"


@pytest.fixture(autouse=True)
def clear_imported_module():
    """Fixture to clean the module lru_cache and the imported module."""
    yield
    lazy.Module.factory.cache_clear()
    if MODULE_NAME in sys.modules:
        del sys.modules[MODULE_NAME]


@pytest.fixture()
def module():
    """Fixture to return a lazy imported module."""
    yield lazy.import_module(MODULE_NAME)


def test_lazy_import_is_lazy(module, capsys):
    """Ensure the module is not executed upon import."""
    captured = capsys.readouterr()
    assert MODULE_NAME not in captured.out


def test_lazy_imported_module(module, capsys):
    """Ensure the module works as expected when used."""
    assert module.function_of_interest() == module.RETURN_VALUE
    captured = capsys.readouterr()
    assert MODULE_NAME in captured.out


def test_lazy_module_single_instance(module):
    """Ensure we only create a single instance per module name."""
    module_second_import = lazy.import_module(MODULE_NAME)
    assert module_second_import is module


@pytest.mark.parametrize("name", ("not_a_valid_module", "not_a_valid_module.submodule"))
@pytest.mark.parametrize("optional", (True, False))
def test_lazy_import_nonexisting_module(name, optional):
    importfunc = functools.partial(lazy.import_module, name, optional=optional)
    if optional:
        assert importfunc() is None
    else:
        with pytest.raises(ModuleNotFoundError, match=name):
            importfunc()
