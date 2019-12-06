# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils.trie"""

import itertools
import random
import string

import pytest

import vimiv.utils.trie


@pytest.fixture
def trie():
    yield vimiv.utils.trie.Trie()


@pytest.mark.parametrize(
    "key, value", [("a", "value"), ("abc", "value"), (("a", "bc"), "value")]
)
def test_setitem(trie, key, value):
    trie[key] = value
    node = trie
    for elem in key:
        assert elem in node.children
        node = node.children[elem]
    assert node.value == value
    assert node.key == "".join(key)


def test_setitem_raises_for_hidden_key(trie):
    """Ensure we cannot add keys with a base that is a full match."""
    key1 = "key"
    key2 = key1 + "1"
    trie[key1] = "value"
    with pytest.raises(ValueError):
        trie[key2] = "value"


def test_setitem_raises_for_hiding_key(trie):
    """Ensure we cannot add keys with a base shorter than a full match."""
    key1 = "key"
    key2 = key1 + "1"
    trie[key2] = "value"
    with pytest.raises(ValueError):
        trie[key1] = "value"


def test_iter(trie):
    def random_str(k: int = 3):
        return "".join(random.choices(string.ascii_lowercase, k=k))

    starting_dict = {random_str(): random_str() for i in range(10)}
    trie.update(**starting_dict)
    for key, value in trie:
        assert starting_dict.pop(key) == value
    assert not starting_dict  # All elements iterated over


def test_fullmatch(trie):
    key, value = "abc", "value"
    trie[key] = value
    result = trie.match(key)
    assert result.is_full_match
    assert result.value == value


def test_partialmatch(trie):
    base_key = "abc"
    expected = {f"{base_key}{i:d}": f"value{i:d}" for i in range(3)}
    trie.update(**expected)
    trie[base_key.upper()] = "anything_not_expected"
    result = trie.match(base_key)
    assert result.is_partial_match
    assert dict(result.partial) == expected


def test_nomatch(trie):
    trie["abc"] = "value"
    result = trie.match("abcd")
    assert result.is_no_match


def test_contains_match(trie):
    key = "abc"
    trie[key] = "value"
    for i, _ in enumerate(key, start=1):
        assert key[:i] in trie


def test_contains_nomatch(trie):
    trie["abc"] = "value"
    assert "abcd" not in trie


def test_delitem_destroys_empty_nodes(trie):
    key = "abc"
    trie[key] = "value"
    del trie[key]
    assert not trie.children


def test_delitem_keeps_nonempty_nodes(trie):
    keys = ["abc" + char for char in "def"]
    value = "value"
    for key in keys:
        trie[key] = value
    del trie[keys[0]]
    assert list(trie) == list(zip(keys[1:], itertools.repeat(value)))
