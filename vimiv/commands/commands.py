# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Command storage, initialization decorators and execution.

Module Attributes:
    _registry: Dictionary to store commands in.
"""

import argparse
import collections

from vimiv.commands import cmdexc
from vimiv.modes import modereg
from vimiv.utils import objreg


class Registry(collections.UserDict):
    """Dictionary to store commands of each mode."""

    def __init__(self):
        super().__init__()
        for mode in modereg.modes:
            self[mode] = {}


registry = Registry()


def clear():
    """Clear all commands registered.

    Used mainly to have a possibility to clean up in tests.
    """
    for dictionary in registry.values():
        dictionary.clear()


def get(name, mode="global"):
    """Get one command object.

    Args:
        name: Name of the command to look for.
        mode: Mode in which to look for the command.
    Return:
        The Command object asserted with name and mode.
    """
    commands = registry[mode]
    if mode in ["image", "library"]:
        commands.update(registry["global"])
    if name not in commands:
        raise cmdexc.CommandNotFound(
            "%s: unknown command for mode %s" % (name, mode))
    return commands[name]


class Args(argparse.ArgumentParser):
    """Store and parse command arguments using argparse."""

    def __init__(self, cmdname, description=""):
        """Create the argparse.ArgumentParser.

        Args:
            cmdname: Name of the command for which the arguments are stored.
            description: Description of the command for error messages.
        """
        super().__init__(prog=cmdname, description=description)

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

        _instance: Object to be passed to func as self argument if any.
    """

    def __init__(self, name, func, instance=None, mode="global"):
        self.name = name
        self.func = func
        self._instance = instance
        self.mode = mode

    def __call__(self, args):
        """Parse arguments and call func."""
        parsed_args = self.func.vimiv_args.parse_args(args)
        kwargs = vars(parsed_args)
        if self._instance:
            obj = objreg.get(self._instance)
            self.func(obj, **kwargs)
        else:
            self.func(**kwargs)


class argument:  # pylint: disable=invalid-name
    """Decorator to update command a command argument.

    As a class with "wrong" name it is cleaner to implement.

    Attributes:
        _argname: Name of the argument.
        _kwargs: kwargs to be passed to parser.parse_args.
    """

    def __init__(self, argname, optional=False, **kwargs):
        self._argname = "--%s" % (argname) if optional else argname
        self._kwargs = kwargs

    def __call__(self, func):
        func.vimiv_args.add_argument(self._argname, **self._kwargs)
        return func


class register:  # pylint: disable=invalid-name
    """Decorator to register a new command.

    As a class with "wrong" name it is cleaner to implement.

    Attributes:
        _instance: The object from the object registry to be used as "self".
        _mode: Mode in which the command can be executed.
    """

    def __init__(self, instance=None, mode="global"):
        self._instance = instance
        self._mode = mode

    def __call__(self, func):
        name = func.__name__.lower().replace("_", "-")
        func.vimiv_args = Args(name)
        cmd = Command(name, func, instance=self._instance, mode=self._mode)
        registry[self._mode][name] = cmd
        return func
