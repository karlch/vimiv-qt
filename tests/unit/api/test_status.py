# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.api.status."""

import pytest

from vimiv.api import status


def test_add_status_module():
    @status.module("{dummy}")
    def dummy_method():
        return "dummy"

    assert status.evaluate("Dummy: {dummy}") == "Dummy: dummy"
    del status._modules["{dummy}"]  # Cleanup


def test_fail_add_status_module():
    with pytest.raises(status.InvalidModuleName):

        @status.module("wrong")
        def wrong():
            return "wrong"
