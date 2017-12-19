# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Tests for vimiv.utils.impaths."""

from unittest.mock import Mock

from vimiv.utils import impaths


def test_load_paths_into_storage(cleansetup):
    mockfunc = Mock()
    impaths.signals.new_image.connect(mockfunc)
    impaths.load(["a", "b"])
    mockfunc.assert_called_once()


def test_get_abspath_of_current_image(cleansetup):
    impaths.load(["a/b", "b/c"])
