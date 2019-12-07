# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Implementation of a trie datastructure.

See e.g. https://en.wikipedia.org/wiki/Trie for more details.
"""

from typing import NamedTuple, Iterable, Optional, Iterator, Tuple, Dict, List

from . import log

KeyT = Iterable[str]
IterResultT = Iterator[Tuple[str, str]]


_logger = log.module_logger(__name__)


class Trie:
    """Implementation of a trie datastructure using dictionaries.

    Attributes:
        children: Dictionary containing all child trie nodes if any.
        key: Full key in the root trie of this node if it is an leaf node.
        value: Value stored in this node if it is an leaf node.
    """

    __slots__ = "children", "key", "value"

    def __init__(self) -> None:
        self.children: Dict[str, Trie] = {}
        self.key: Optional[str] = None
        self.value: Optional[str] = None

    def __setitem__(self, key: KeyT, value: str) -> None:
        """Add a key, value pair to the trie logging a warning on possible clashes."""
        key = tuple(key)
        node = self
        for elem in key:
            if elem not in node.children:
                if node.key is not None:
                    _logger.warning(
                        "%s is hidden by shorter key %s", "".join(key), node.key
                    )
                node.children[elem] = Trie()
            node = node.children[elem]
        if node.children:
            _logger.warning("%s hides longer keys", "".join(key))
        node.key = "".join(key)
        node.value = value

    def __getitem__(self, key: KeyT) -> "Trie":
        """Retrieve the node matching key from the trie."""
        node = self
        for elem in key:
            node = node.children[elem]
        return node

    def __contains__(self, key: KeyT):
        return not self.match(key).is_no_match

    def __iter__(self):
        """Iterate over all key, value pairs in the leaf nodes."""
        if self.value is None:
            for child in self.children.values():
                yield from child
        else:
            yield self.key, self.value

    def __delitem__(self, key: KeyT):
        """Delete a key from the trie.

        Any nodes that become empty through this operation are removed from the trie.
        This is at least the corresponding leaf node, but may also involve up to all
        parents if this key is the only leaf node starting with the first element of
        key.
        """
        key = tuple(key)
        for elem, node in zip(reversed(key), reversed(self._getnodes(key))):
            del node.children[elem]
            if node.children or node.value:
                break

    def update(self, **kwargs):
        """Add all key, value pairs from keyword arguments to the trie."""
        for key, value in kwargs.items():
            self[key] = value

    def match(self, key: KeyT) -> "TrieMatch":
        """Try to match the given key to a node in the trie.

        There are three cases:
            1) If the key is not in the trie, an empty TrieMatch is returned.
            2) If the key maps to a leaf node, the TrieMatch is filled with the value of
               the leaf.
            3) If the key maps to a node with children, the TrieMatch is filled with an
               iterator to the key, value pairs of all children.
        """
        try:
            node = self[key]
        except KeyError:
            return TrieMatch()
        if node.key is not None:
            return TrieMatch(value=node.value)
        return TrieMatch(partial=iter(node))

    def _getnodes(self, key: KeyT) -> List["Trie"]:
        """Return all nodes that make up key.

        For example, if the key is 'abc', the corresponding nodes 'a', 'b' and 'c' are
        returned.
        """
        node = self
        nodes = []
        for elem in key:
            try:
                nodes.append(node)
                node = node.children[elem]
            except KeyError:
                raise KeyError(key) from None
        return nodes


class TrieMatch(NamedTuple):
    """Helper class as result for Trie.match, see Trie.match for details."""

    value: Optional[str] = None
    partial: Optional[IterResultT] = None

    @property
    def is_full_match(self):
        return self.value is not None

    @property
    def is_partial_match(self):
        return self.partial is not None

    @property
    def is_no_match(self):
        return self.partial is self.value is None
