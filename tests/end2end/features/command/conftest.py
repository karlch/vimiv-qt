# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest

from vimiv.commands import aliases


@pytest.fixture(autouse=True)
def cleanup_aliases(cleanup_helper):
    """Fixture to delete any aliases that were created in this feature."""
    yield from cleanup_helper(aliases._aliases)
