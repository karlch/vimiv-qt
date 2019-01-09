# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Command storage and initialization decorators.

Module Attributes:
    registry: Dictionary to store commands in.

//

The user interacts with vimiv using commands. Utilities to create and store
commands are implemented in ``vimiv.commands.commands``.

Creating a new command is done using the ``register`` decorator, arguments are
added using the ``argument`` decorator. The command name is directly infered
from the function name, the functions docstring is used to document the
command. To understand this concept, lets add a simple command that prints
"hello earth" to the terminal::

    @commands.register()
    def hello_earth():
        print("hello earth")

This code snippet creates the command ``:hello-earth`` which does not accept
any arguments. To allow greeting other planets, let's add an argument
``name`` which defaults to earth::

    @commands.argument("name", optional=True, default="earth")
    @commands.register()
    def hello_planet(name="earth"):
        print("hello", name)

Now the command ``:hello-planet`` is created. When called without arguments, it
prints "hello earth" as before, but it is also possible to great other planets
by passing their name: ``:hello-planet --name=venus``.

It is possible for commands to support the special ``count`` argument.
``count`` is passed by the user either by prepending it to the command like
``:2next`` or by typing numbers before calling a keybinding. Let's update our
``:hello-planet`` command to support ``count`` by printing the greeting
``count`` times::

    @commands.argument("name", optional=True, default="earth")
    @commands.register(count=1)
    def hello_planet(name="earth", count=1):
        for i in range(count):
            print("hello", name)

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

In this case it probably makes sense to define a default keybinding for this
command.
"""

import argparse
import collections
import inspect
import logging

from vimiv.commands import cmdexc
from vimiv.modes import Modes
from vimiv.utils import (class_that_defined_method, cached_method, is_method,
                         objreg)


class Registry(collections.UserDict):
    """Dictionary to store commands of each mode."""

    def __init__(self):
        super().__init__()
        for mode in Modes:
            self[mode] = {}


registry = Registry()


def get(name, mode=Modes.GLOBAL):
    """Get one command object.

    Args:
        name: Name of the command to look for.
        mode: Mode in which to look for the command.
    Return:
        The Command object asserted with name and mode.
    """
    commands = registry[mode]
    if mode in [Modes.IMAGE, Modes.LIBRARY, Modes.THUMBNAIL]:
        commands.update(registry[Modes.GLOBAL])
    if name not in commands:
        raise cmdexc.CommandNotFound(
            "%s: unknown command for mode %s" % (name, mode.name))
    return commands[name]


class Args(argparse.ArgumentParser):
    """Store and parse command arguments using argparse."""

    def __init__(self, cmdname):
        """Create the argparse.ArgumentParser.

        Args:
            cmdname: Name of the command for which the arguments are stored.
        """
        super().__init__(prog=cmdname)

    def print_help(self):
        """Override help message to display in statusbar."""
        raise cmdexc.ArgumentError(self.format_usage().rstrip())

    def error(self, message):
        """Override error to raise an exception instead of calling sys.exit."""
        if message.startswith("argument"):  # Remove argument argname:
            message = " ".join(message.split(":")[1:])
        message = message.strip()
        message = " ".join(message.split())  # Remove multiple whitespace
        message = message.capitalize()
        raise cmdexc.ArgumentError(message)


class Command():
    """Skeleton for a command.

    Attributes:
        func: Corresponding executable to call.
        mode: Mode in which the command can be executed.
        name: Name of the command as string.
        count: Associated count. If it is not None, this count will be used as
            default and passing other counts is supported by the command.
        description: Description of the command for help.
        hide: Hide command from command line.
        hook: Function to run before executing the command.
    """

    def __init__(self, name, func, mode=Modes.GLOBAL,
                 count=None, description="", hide=False, hook=None):
        self.name = name
        self.func = func
        self.mode = mode
        self.count = count
        self.description = description
        self.hide = hide
        self.hook = hook if hook is not None else lambda *args: None

    def __call__(self, args, count):
        """Parse arguments and call func.

        Args:
            args: List of arguments for argparser to parse.
            count: Count passed to the command.
        """
        parsed_args = self.func.vimiv_args.parse_args(args)
        parsed_count = self._parse_count(count)
        kwargs = vars(parsed_args)
        # Add count for function to deal with
        if parsed_count is not None:
            kwargs["count"] = parsed_count
        func = self._create_func(self.func)
        func(**kwargs)

    def _parse_count(self, count):
        """Parse given count."""
        # Does not support count
        if self.count is None:
            return None
        # Use default
        if count == "":
            return self.count
        # Use count given
        return int(count)

    def __repr__(self):
        return "Command('%s', '%s')" % (self.name, self.func)

    @cached_method
    def _create_func(self, func):
        """Create function to call for a command function.

        This processes hooks and retrieves the instance of a class object for
        methods and sets it as first argument (the 'self' argument) of a
        lambda. For standard functions nothing is done.

        Returns:
            A function to be called with any keyword arguments.
        """
        logging.debug("Creating function for command '%s'", func.__name__)
        if is_method(func):
            cls = class_that_defined_method(func)
            instance = objreg.get(cls)
            return lambda **kwargs: (self.hook(instance),
                                     func(instance, **kwargs))
        return lambda **kwargs: (self.hook(), func(**kwargs))


def argument(argname, optional=False, **kwargs):
    """Decorator to update command a command argument.

    Args:
        argname: Name of the argument.
        optional: True if the argument optional, else it is positional.
        kwargs: kwargs to be passed to parser.parse_args.
    """
    argname = "--%s" % (argname) if optional else argname
    def decorator(func):
        func.vimiv_args.add_argument(argname, **kwargs)
        return func
    return decorator


def register(mode=Modes.GLOBAL, count=None, hide=False, hook=None):
    """Decorator to store a command in the registry.

    Args:
        mode: Mode in which the command can be executed.
        count: Associated count. If it is not None, this count will be used as
            default and passing other counts is supported by the command.
        hide: Hide command from command line.
        hook: Function to run before executing the command.
    """
    def decorator(func):
        name = _get_command_name(func)
        desc = _get_description(func, name)
        func.vimiv_args = Args(name)
        cmd = Command(name, func, mode=mode, count=count, description=desc,
                      hide=hide, hook=hook)
        registry[mode][name] = cmd
        return func
    return decorator


def _get_command_name(func):
    """Retrieve command name from name of function object."""
    return func.__name__.lower().replace("_", "-")


def _get_description(func, name):
    """Retrive the command description from function docstring.

    Args:
        func: Python function object to retrieve the docstring from.
        name: Name of the command to retrieve the description for.
    Return:
        The string description of the command.
    """
    try:
        return inspect.getdoc(func).split("\n")[0]
    except AttributeError:
        logging.error("Command %s for %s is missing docstring.", name, func)
    return ""
