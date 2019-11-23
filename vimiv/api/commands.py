# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""`Command storage and initialization`.

The user interacts with vimiv using commands. Creating a new command is done
using the :func:`register` decorator. The command name is directly infered from
the function name, the functions docstring is used to document the command. The
arguments supported by the command are also deduced by inspecting the arguments
the function takes. To understand these concepts, lets add a simple command
that prints "hello earth" to the terminal::

    from vimiv.api import commands

    @commands.register()
    def hello_earth():
        print("hello earth")

This code snippet creates the command ``:hello-earth`` which does not accept
any arguments. To allow greeting other planets, let's add an argument
``name`` which defaults to earth::

    @commands.register()
    def hello_planet(name: str = "earth"):
        print("hello", name)

Now the command ``:hello-planet`` is created. When called without arguments, it
prints "hello earth" as before, but it is also possible to great other planets
by passing their name: ``:hello-planet --name=venus``.

.. hint::

    Type annotating the arguments is required as the type annotation is passed
    to the argument parser as type of the argument.

It is possible for commands to support the special ``count`` argument.
``count`` is passed by the user either by prepending it to the command like
``:2next`` or by typing numbers before calling a keybinding. Let's update our
``:hello-planet`` command to support ``count`` by printing the greeting
``count`` times::

    @commands.register()
    def hello_planet(name: str = "earth", count: int = 1):
        for i in range(count):
            print("hello", name)

Another special argument is the ``paths`` argument. It will perform unix-style pattern
matching using the ``glob`` module on each path given and return a list of matched
paths. An example of this in action is the ``:open`` command defined in ``vimiv.app``.

Each command is valid for a specific mode, the default being global. To supply
the mode, add it to the register decorator::

    @commands.register(mode=Modes.IMAGE)
    def ...

In general commands are usable by keybindings and in the command line. If it
makes no sense for a command to be visible in the command line, e.g. the
``:command`` command which enters the command line, the hide option can be
passed::

    @commands.register(hide=True)
    def ...

In this case it is probably smart to define a default keybinding for the
command.
"""

import argparse
import glob
import inspect
import os
import typing
from contextlib import suppress
from functools import partial

from vimiv.utils import (
    class_that_defined_method,
    cached_method,
    is_method,
    flatten,
    log,
    customtypes,
    escape_glob,
)

from . import modes


_logger = log.module_logger(__name__)


def register(
    mode: modes.Mode = modes.GLOBAL, hide: bool = False, store: bool = True,
) -> typing.Callable[[customtypes.FuncT], customtypes.FuncT]:
    """Decorator to store a command in the registry.

    Args:
        mode: Mode in which the command can be executed.
        hide: Hide command from command line.
        store: Save command to allow repeating with '.'.
    """

    def decorator(func: customtypes.FuncT) -> customtypes.FuncT:
        _Command(func, mode=mode, hide=hide, store=store)
        return func

    return decorator


def get(name: str, mode: modes.Mode = modes.GLOBAL) -> "_Command":
    """Get one command object.

    Args:
        name: Name of the command to look for.
        mode: Mode in which to look for the command.
    Returns:
        The Command object asserted with name and mode.
    """
    commands = _registry[mode]
    if mode in modes.GLOBALS:
        commands.update(_registry[modes.GLOBAL])
    try:
        return commands[name]
    except KeyError:
        raise CommandNotFound(f"{name}: unknown command for mode {mode.name}")


class ArgumentError(Exception):
    """Raised if a command was called with wrong arguments."""


class CommandError(Exception):
    """Raised if a command failed to run correctly."""


class CommandWarning(Exception):
    """Raised if a command wants to show the user a warning."""


class CommandInfo(Exception):
    """Raised if a command wants to show the user an info."""


class CommandNotFound(Exception):
    """Raised if a command does not exist for a specific mode."""


# Dictionary storing the command dictionary for each mode
_registry: typing.Dict[modes.Mode, typing.Dict[str, "_Command"]] = {
    mode: {} for mode in modes.ALL
}


def items(mode: modes.Mode) -> typing.ItemsView[str, "_Command"]:
    """Retrieve all items in the commands registry for iteration.

    Args:
        mode: The mode for which the commands are valid.
    Returns:
        typing.ItemsView allowing iteration over items.
    """
    return _registry[mode].items()


def exists(name: str, mode: modes.Mode) -> bool:
    """Check if a command exists in the registry.

    Args:
        name: Name of the command to check for.
        mode: The mode for which the command is valid.
    Returns:
        True if the command exists.
    """
    return name in _registry[mode]


class _CommandArguments(argparse.ArgumentParser):
    """Store and parse command arguments using argparse."""

    def __init__(self, cmdname: str, description: str, function: typing.Callable):
        """Create the argparse.ArgumentParser.

        Args:
            cmdname: Name of the command for which the arguments are stored.
            description: Description of the command to print in help
            function: Function to inspect for arguments.
        """
        super().__init__(prog=cmdname, description=description)
        for argument in inspect.signature(function).parameters.values():
            self._add_argument(argument)

    def print_help(self, _file: typing.IO = None) -> typing.NoReturn:
        """Override help message to display in statusbar."""
        raise CommandInfo(self.description)

    def parse_args(self, args: typing.List[str]) -> argparse.Namespace:  # type: ignore
        """Override parse_args to sort and flatten paths list in addition."""
        parsed_args = super().parse_args(args)
        with suppress(AttributeError):
            parsed_args.paths = [
                os.path.abspath(path) for path in sorted(flatten(parsed_args.paths))
            ]
        return parsed_args

    def error(self, message: str) -> typing.NoReturn:
        """Override error to raise an exception instead of calling sys.exit."""
        if message.startswith("argument"):  # Remove argument argname:
            message = " ".join(message.split(":")[1:])
        message = message.strip()
        message = " ".join(message.split())  # Remove multiple whitespace
        message = message.capitalize()
        raise ArgumentError(message)

    def _add_argument(self, argument: inspect.Parameter) -> None:
        """Add an argument to argparse created from an inspect parameter."""
        optional = argument.default != inspect.Parameter.empty
        name = self._argument_name(argument, optional)
        # Dealt with later as we do not have an instance yet
        if name == "self":
            return
        kwargs = self._gen_kwargs(argument, optional)
        self.add_argument(name, **kwargs)

    @staticmethod
    def _argument_name(argument: inspect.Parameter, optional: bool) -> str:
        """Create argument name from inspect parameter."""
        name = argument.name.replace("_", "-")
        return f"--{name}" if optional else name

    @staticmethod
    def _gen_kwargs(
        argument: inspect.Parameter, optional: bool
    ) -> typing.Dict[str, typing.Any]:
        """Create keyword arguments for argparse from inspect parameter.

        This checks for the type and possible default arguments and applies
        'nargs': '*' if the type is a List.
        """
        argtype = argument.annotation
        if argument.name == "paths":
            return {
                "type": lambda x: glob.glob(
                    os.path.expanduser(escape_glob(x)), recursive=True
                ),
                "nargs": "+",
            }
        if argtype == typing.List[str]:
            return {"type": str, "nargs": "*"}
        if optional and argtype is bool:
            return {"action": "store_true"}
        if optional:
            return {"type": argtype, "default": argument.default}
        return {"type": argtype}


# The class is still rather simple but many things need to be stored for various places
class _Command:  # pylint: disable=too-many-instance-attributes
    """Skeleton for a command.

    Attributes:
        name: Name of the command as string.
        func: Corresponding executable to call.
        mode: Mode in which the command can be executed.
        hide: Hide command from command line.
        store: Save command to allow repeating with '.'.
        description: Brief command description.

        _argparser: Argument parser used when the command is called.
        _long_description: Full command description.
    """

    def __init__(
        self,
        func: typing.Callable,
        mode: modes.Mode = modes.GLOBAL,
        hide: bool = False,
        store: bool = True,
    ):
        self._argparser: typing.Optional[_CommandArguments] = None
        self.name = _get_command_name(func)
        self.func = func
        self.mode = mode
        self.hide = hide
        self.store = store
        # Retrieve description from docstring
        docstr = inspect.getdoc(func)
        if docstr is None:
            log.error("Command %s for %s is missing docstring.", self.name, func)
            self.description = self.long_description = ""
        else:
            self.description = docstr.split("\n", maxsplit=1)[0]
            self.long_description = docstr
        # Store command in the global registry
        _registry[mode][self.name] = self

    def __call__(self, args: typing.List[str], count: str) -> None:
        """Parse arguments and call func.

        Args:
            args: List of arguments for argparser to parse.
            count: Count passed to the command.
        """
        parsed_args = self.argparser.parse_args(args)
        kwargs = vars(parsed_args)
        self._parse_count(count, kwargs)
        func = self._create_func(self.func)
        func(**kwargs)

    @property
    def argparser(self) -> _CommandArguments:
        """The initialized argument parser.

        This is used so the parser is lazily created upon first command call.
        """
        if self._argparser is None:
            self._argparser = _CommandArguments(
                self.name, self.long_description, self.func
            )
        return self._argparser

    def _parse_count(self, count: str, kwargs: typing.Dict[str, typing.Any]) -> None:
        """Add count to kwargs if supported."""
        if "count" in kwargs and count:
            kwargs["count"] = int(count)

    def __repr__(self) -> str:
        return f"Command('{self.name}', '{self.func}')"

    @cached_method
    def _create_func(self, func: typing.Callable) -> typing.Callable:
        """Create function to call for a command function.

        This retrieves the instance of a class object for methods and sets it as first
        argument (the 'self' argument) of a lambda. For standard functions nothing is
        done.

        Returns:
            A function to be called with any keyword arguments.
        """
        _logger.debug("Creating function for command '%s'", func.__name__)
        if is_method(func):
            cls = class_that_defined_method(func)
            instance = cls.instance
            return partial(func, instance)
        return func


def _get_command_name(func: typing.Callable) -> str:
    """Retrieve command name from name of function object."""
    return func.__name__.lower().replace("_", "-")
