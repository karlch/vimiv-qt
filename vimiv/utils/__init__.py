# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Various utility functions."""

import functools
import inspect
import re
from contextlib import suppress
from typing import Callable, Optional, TypeVar

from PyQt5.QtCore import pyqtSlot


Number = TypeVar("Number", int, float)


def add_html(tag: str, text: str) -> str:
    """Surround text in a html tag.

    Args:
        tag: Tag to use, e.g. b.
        text: The text to surround.
    """
    return "<%s>%s</%s>" % (tag, text, tag)


def strip_html(text: str) -> str:
    """Strip all html tags from text.

    strip("<b>hello</b>") = "hello"

    Return:
        The stripped text.
    """
    stripper = re.compile("<.*?>")
    return re.sub(stripper, "", text)


def clamp(
    value: Number, minimum: Optional[Number], maximum: Optional[Number]
) -> Number:
    """Clamp a value so it does not exceed boundaries."""
    if minimum is not None:
        value = max(value, minimum)
    if maximum is not None:
        value = min(value, maximum)
    return value


def class_that_defined_method(method):
    """Return the class that defined a method.

    This is used by the decorators for statusbar and command, when the class is
    not yet created.
    """
    return getattr(inspect.getmodule(method), method.__qualname__.split(".")[0])


def is_method(func):
    """Return True if func is a method owned by a class.

    This is used by the decorators for statusbar and command, when the class is
    not yet created.
    """
    return "self" in inspect.signature(func).parameters


def cached_method(func):
    """Decorator to cache the result of a class method."""
    attr_name = "_lazy_" + func.__name__

    @property
    @functools.wraps(func)
    def _lazyprop(self):
        def inner(*args, **kwargs):
            # Store the result of the function to attr_name in first
            # evaluation, afterwards return the cached value
            if not hasattr(self, attr_name):
                setattr(self, attr_name, func(self, *args, **kwargs))
            return getattr(self, attr_name)

        return inner

    return _lazyprop


class AnnotationNotFound(Exception):
    """Raised if a there is no type annotation to use."""

    def __init__(self, name: str, function: Callable):
        message = "Missing type annotation for parameter '%s' in function '%s'" % (
            name,
            function.__qualname__,
        )
        super().__init__(message)


def _slot_args(argspec, function):
    """Create arguments for pyqtSlot from function arguments.

    Args:
        argspec: Function arguments retrieved via inspect.
        function: The python function for which the arguments are created.
    Return:
        List of types of the function arguments as arguments for pyqtSlot.
    """
    slot_args = []
    for argument in argspec.args:
        has_annotation = argument in argspec.annotations
        if argument == "self" and not has_annotation:
            continue
        if not has_annotation:
            raise AnnotationNotFound(argument, function)
        annotation = argspec.annotations[argument]
        slot_args.append(annotation)
    return slot_args


def _slot_kwargs(argspec):
    """Add return type to slot kwargs if it exists."""
    with suppress(KeyError):
        return_type = argspec.annotations["return"]
        if return_type is not None:
            return {"result": return_type}
    return {}


def slot(function):
    """Annotation based slot decorator using pyqtSlot.

    Syntactic sugar for pyqtSlot so the parameter types do not have to be repeated when
    there are type annotations.

    Example:
        @slot
        def function(self, x: int, y: int) -> None:
        ...
    """
    argspec = inspect.getfullargspec(function)
    slot_args, slot_kwargs = _slot_args(argspec, function), _slot_kwargs(argspec)
    pyqtSlot(*slot_args, **slot_kwargs)(function)
    return function
