# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.api.status."""

import pytest

from vimiv.api import status


@pytest.fixture()
def dummy_module():
    """Fixture to create and clean-up a valid status module."""
    name = "{dummy}"
    content = "dummy"

    @status.module(name)
    def dummy_method():
        return content

    yield name, content

    del status._modules[name]


def test_evaluate_status_module(dummy_module):
    name, content = dummy_module
    assert status.evaluate(f"Dummy: {name}") == f"Dummy: {content}"


def test_fail_add_status_module():
    with pytest.raises(ValueError):

        @status.module("wrong")
        def wrong():
            return "wrong"


def test_evaluate_unknown_module(mocker):
    name = "{unknown-module}"
    assert status.evaluate(f"Dummy: {name}") == "Dummy: "
