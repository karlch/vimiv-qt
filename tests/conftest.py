# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Fixtures for pytest."""

import os

import pytest


CI = "CI" in os.environ

# fmt: off
PLATFORM_MARKERS = (
    ("ci", CI, "Only run on ci"),
    ("ci_skip", not CI, "Skipped on ci"),
)
# fmt: on


def apply_platform_markers(item):
    """Apply markers that skip tests depending on the current platform."""
    for marker_name, fulfilled, reason in PLATFORM_MARKERS:
        marker = item.get_closest_marker(marker_name)
        if not marker or fulfilled:
            continue
        skipif = pytest.mark.skipif(
            not fulfilled, *marker.args, reason=reason, **marker.kwargs
        )
        item.add_marker(skipif)


def pytest_collection_modifyitems(items):
    """Handle custom markers via pytest hook."""
    for item in items:
        apply_platform_markers(item)


@pytest.fixture
def cleanup_helper():
    """Fixture to keep vimiv registries clean.

    Returns a contextmanager that resets the state of a dictionary to the initial state
    before running tests.
    """

    def cleanup(init_dict, keyupdate=lambda x: x):
        init_content = {key: dict(value) for key, value in init_dict.items()}
        yield
        new_content = {key: dict(value) for key, value in init_dict.items()}
        for key, valuedict in new_content.items():
            for elem in valuedict:
                if elem not in init_content[key]:
                    del init_dict[key][keyupdate(elem)]

    return cleanup
