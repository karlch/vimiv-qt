# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Sanity tests for keybindings."""

import re

from collections import defaultdict
from typing import Dict

from vimiv import vimiv


def test_short_binding_hides_longer_bindings():
    for bindings_dict in vimiv.api.keybindings._registry.values():
        _test_short_binding_hides_longer_bindings(bindings_dict)


def _test_short_binding_hides_longer_bindings(bindings_dict: Dict[str, str]):
    """Ensure no short keybinding overrides a longer one.

    For example having both a binding for P and for Pp would raise an AssertionError as
    the shorter binding (P) would make it impossible to trigger the longer one (Pp).
    """
    bindings_per_startkey = defaultdict(list)
    for binding in bindings_dict:
        first_key = _get_first_key(binding)
        bindings_per_startkey[first_key].append(binding)
    for letter, bindings in bindings_per_startkey.items():
        lengths = map(len, bindings)
        msg = "Conflicts for bindings %s found" % (", ".join(bindings))
        assert len(set(lengths)) == 1, msg


def _get_first_key(binding: str) -> str:
    """Retrieve the first key in a keybinding."""
    if binding.startswith("<"):  # Special keys like <Return>
        match = re.search("<.+>", binding)
        if match is not None:
            return match.group()
    return binding[0]  # Regular keys like a
