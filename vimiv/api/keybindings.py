# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""`Utilities to map commands to a sequence of keys`.

Adding a new default keybinding is done using the :func:`register` decorator.
This decorator requires the sequence of keys to bind to as first argument, the
command as second argument and, similar to :func:`vimiv.api.commands.register`
supports the ``mode`` keyword to define the mode in which the keybinding is
valid.

As an example, let's bind the ``:hello-earth`` command from before to the key
sequence ``ge``::

    from vimiv.api import commands, keybindings

    @keybindings.register("ge", "hello-earth")
    @commands.register()
    def hello_earth():
        print("hello earth")

If the keybinding requires passing any arguments to the command, these must be
passed as part of the command. For example, to great venus with ``gv`` and
earth with ``ge`` we could use::

    @keybindings.register("gv", "hello-planet --name=venus")
    @keybindings.register("ge", "hello-planet")
    @commands.register()
    def hello_planet(name: str = "earth"):
        print("hello", name)
"""

import functools
import re
from typing import Callable, Union, Tuple, Iterable, Iterator

from vimiv.utils import customtypes, trie

from . import commands, modes


def register(
    keybinding: Union[str, Iterable[str]], command: str, mode: modes.Mode = modes.GLOBAL
) -> Callable[[customtypes.FuncT], customtypes.FuncT]:
    """Decorator to add a new keybinding.

    Args:
        keybinding: Key sequence(s) to bind as string (Iterable of strings).
        command: Command to bind to.
        mode: Mode in which the keybinding is valid.
    """

    def decorator(function: customtypes.FuncT) -> customtypes.FuncT:
        if isinstance(keybinding, str):
            bind(keybinding, command, mode)
        else:
            for binding in keybinding:
                bind(binding, command, mode, override=False)
        return function

    return decorator


def bind(
    keybinding: str, command: str, mode: modes.Mode, override: bool = True
) -> None:
    """Store keybinding in registry.

    See config/configcommands.bind for the corresponding command.
    """
    # See https://github.com/python/mypy/issues/4975
    for submode in modes.GLOBALS if mode is modes.GLOBAL else (mode,):  # type: ignore
        bindings = _registry[submode]
        if not override and keybinding in bindings:
            raise ValueError(f"Duplicate keybinding for '{keybinding}'")
        bindings[keybinding] = command


def unbind(keybinding: str, mode: modes.Mode) -> None:
    """Remove keybinding from registry.

    See config/configcommands.unbind for the corresponding command.
    """
    # See https://github.com/python/mypy/issues/4975
    for submode in modes.GLOBALS if mode is modes.GLOBAL else (mode,):  # type: ignore
        try:
            del _registry[submode][keybinding]
        except KeyError:
            raise commands.CommandError(f"No binding found for '{keybinding}'")


class _BindingsTrie(trie.Trie):
    """Trie used for keybindings which ensures valid keysequences for special keys."""

    SPECIAL_KEY_RE = re.compile("<.*?>")

    def __setitem__(self, keybinding: str, command: str) -> None:  # type: ignore
        super().__setitem__(self.keysequence(keybinding), command)

    def __getitem__(self, keybinding: Iterable[str]) -> trie.Trie:
        if isinstance(keybinding, str):
            return super().__getitem__(self.keysequence(keybinding))
        return super().__getitem__(keybinding)

    def __delitem__(self, keybinding: Iterable[str]) -> None:
        if isinstance(keybinding, str):
            super().__delitem__(self.keysequence(keybinding))
        else:
            super().__delitem__(keybinding)

    @classmethod
    @functools.lru_cache(None)
    def keysequence(cls, keys: str) -> Tuple[str, ...]:
        """Split keys into tuple of individual keys handling special keys correctly."""

        def generator(keys: str) -> Iterator[str]:
            while keys:
                special_key_match = cls.SPECIAL_KEY_RE.match(keys)
                if special_key_match is not None:
                    special_key = special_key_match.group()
                    yield special_key
                    keys = keys[len(special_key) :]
                else:
                    yield keys[0]
                    keys = keys[1:]

        return tuple(generator(keys))


_registry = {mode: _BindingsTrie() for mode in modes.ALL}


def get(mode: modes.Mode) -> trie.Trie:
    """Return the keybindings of one specific mode."""
    return _registry[mode]


def items() -> Iterator[Tuple[modes.Mode, Iterable[Tuple[str, str]]]]:
    """Iterator to retrieve the sorted, unique bindings per mode.

    Bindings that are in the global modes will be associated with the global mode. All
    remaining bindings are part of their respective mode.
    """
    global_bindings = (
        set(get(modes.IMAGE)) & set(get(modes.LIBRARY)) & set(get(modes.THUMBNAIL))
    )

    def sort(bindings: Iterable[Tuple[str, str]]) -> Iterable[Tuple[str, str]]:
        """Sort by command, then keys."""
        return sorted(bindings, key=lambda x: tuple(reversed(x)))

    for mode in modes.ALL:
        if mode == modes.GLOBAL:
            yield mode, sort(global_bindings)
        elif mode in modes.GLOBALS:
            yield mode, sort(set(get(mode)) - global_bindings)
        else:
            yield mode, sort(get(mode))
