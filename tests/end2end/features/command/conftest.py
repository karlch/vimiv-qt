# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

import pytest

from vimiv.commands import aliases


@pytest.fixture(autouse=True)
def cleanup_aliases(cleanup_helper):
    """Fixture to delete any aliases that were created in this feature."""
    yield from cleanup_helper(aliases._aliases)
