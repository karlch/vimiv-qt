# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Various utility functions."""

import functools
import inspect
import re
from abc import ABCMeta
import typing

from PyQt5.QtCore import Qt, pyqtSlot, QRunnable, QThreadPool, QProcess, QTimer
from PyQt5.QtGui import QPixmap, QColor, QPainter

from .customtypes import AnyT, FuncT, FuncNoneT, NumberT

# Different location under PyQt < 5.11
try:
    from PyQt5.sip import wrappertype
except ImportError:  # pragma: no cover  # Covered in a different tox env during CI
    from sip import wrappertype  # type: ignore


def add_html(text: str, *tags: str) -> str:
    """Surround text html tags.

    Args:
        text: The text to surround.
        tags: Tuple of tags to use, e.g. "b", "i".
    """
    for tag in tags:
        text = f"<{tag}>{text}</{tag}>"
    return text


def wrap_style_span(style: str, text: str) -> str:
    """Surround text in a html style span tag.

    Args:
        style: The css style content to use.
        text: The text to surround.
    """
    return f"<span style='{style};'>{text}</span>"


def strip_html(text: str) -> str:
    """Strip all html tags from text.

    strip("<b>hello</b>") = "hello"

    Returns:
        The stripped text.
    """
    stripper = re.compile("<.*?>")
    return re.sub(stripper, "", text)


def escape_html(text: str) -> str:
    return text.replace("<", "&lt;").replace(">", "&gt;")


def escape_glob(text: str) -> str:
    r"""Escape special characters prefixed by \ for glob using [character]."""

    def escape_char(match):
        char = match.group()[-1]
        return f"[{char}]"

    return re.sub(r"\\[\*\?\[\]]", escape_char, text)


def contains_any(
    sequence: typing.Iterable[AnyT], elems: typing.Union[typing.Iterable[AnyT], AnyT]
) -> bool:
    """Return True if the sequence contains any of the elems."""
    if not sequence:
        return False
    try:
        elems = typing.cast(typing.Iterable[AnyT], elems)
        iter(elems)
        return bool(set(sequence) & set(elems))
    except TypeError:
        return typing.cast(AnyT, elems) in sequence


def clamp(
    value: NumberT, minimum: typing.Optional[NumberT], maximum: typing.Optional[NumberT]
) -> NumberT:
    """Clamp a value so it does not exceed boundaries."""
    if minimum is not None:
        value = max(value, minimum)
    if maximum is not None:
        value = min(value, maximum)
    return value


def parameter_names(function: typing.Callable) -> typing.Tuple[str, ...]:
    """Fast implementation of getting the parameter names of a function.

    This will fail for functions supporting *args or **kwargs. Usually this is not a
    problem as the functions we wish to inspect are static.
    """
    code = function.__code__
    return code.co_varnames[: code.co_argcount]


def class_that_defined_method(method):
    """Return the class that defined a method.

    This is used by the decorators for statusbar and command, when the class is
    not yet created.
    """
    return getattr(inspect.getmodule(method), method.__qualname__.split(".")[0])


def is_method(func: typing.Callable) -> bool:
    """Return True if func is a method owned by a class.

    This is used by the decorators for statusbar and command, when the class is
    not yet created.
    """
    return "self" in parameter_names(func)


def cached_method(func):
    """Decorator to cache the result of a class method."""
    attr_name = "_lazy_" + func.__name__

    @functools.wraps(func)
    def inner(self, *args, **kwargs):
        # Store the result of the function to attr_name in first
        # evaluation, afterwards return the cached value
        if not hasattr(self, attr_name):
            setattr(self, attr_name, func(self, *args, **kwargs))
        return getattr(self, attr_name)

    return inner


class AnnotationNotFound(Exception):
    """Raised if a there is no type annotation to use."""

    def __init__(self, name: str, function: typing.Callable):
        message = (
            f"Missing type annotation for parameter '{name}' "
            f"in function '{function.__qualname__}'"
        )
        super().__init__(message)


def slot(function: FuncT) -> FuncT:
    """Annotation based slot decorator using pyqtSlot.

    Syntactic sugar for pyqtSlot so the parameter types do not have to be repeated when
    there are type annotations.

    Example:
        @slot
        def function(self, x: int, y: int) -> None:
        ...
    """
    annotations = typing.get_type_hints(function)
    args = _slot_args(function, annotations)
    kwargs = _slot_kwargs(annotations)
    return pyqtSlot(*args, **kwargs)(function)


def _slot_args(function, annotations):
    """Create arguments for pyqtSlot from function arguments.

    Args:
        function: The python function for which the arguments are created.
        annotations: Function type annotations.
    Returns:
        List of types of the function arguments as arguments for pyqtSlot.
    """
    slot_args = []
    for parameter in parameter_names(function):
        annotation = annotations.get(parameter, None)
        if parameter == "self" and annotation is None:
            continue
        if annotation is None:
            raise AnnotationNotFound(parameter, function)
        slot_args.append(annotation)
    return slot_args


def _slot_kwargs(annotations):
    """Add return type to slot kwargs if it exists."""
    return_type = annotations.get("return", None)
    return {} if return_type is None else {"result": return_type}


class GenericRunnable(QRunnable):
    """Generic QRunnable to run an arbitrary function on a QThreadPool."""

    def __init__(self, function: typing.Callable, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self) -> None:  # pragma: no cover  # This is in parallel in Qt
        self.function(*self.args, **self.kwargs)


def asyncrun(
    function: typing.Callable, *args, pool: QThreadPool = None, **kwargs
) -> None:
    """Run function with args and kwargs in parallel on a QThreadPool."""
    pool = pool if pool is not None else Pool.get()
    runnable = GenericRunnable(function, *args, **kwargs)
    pool.start(runnable)


def asyncfunc(pool: QThreadPool = None) -> typing.Callable[[FuncNoneT], FuncNoneT]:
    """Decorator to run function in parallel on a QThreadPool."""

    def decorator(function: FuncNoneT) -> FuncNoneT:
        @functools.wraps(function)
        def inner(*args: typing.Any, **kwargs: typing.Any) -> None:
            asyncrun(function, *args, pool=pool, **kwargs)

        # Mypy seems to disapprove the *args, **kwargs, but we just wrap the function
        return inner  # type: ignore

    return decorator


class Pool:
    """Class to handle thread pools.

    All created thread pools are stored to allow clearing and waiting for every pool
    consistently. QThreadPool instances should only be created using this class, never
    indirectly.

    Class Attributes:
        _threadpoools: List of all created thread pools.
    """

    _threadpools = [QThreadPool.globalInstance()]

    @staticmethod
    def get(*, globalinstance: bool = True) -> QThreadPool:
        """Return a thread pool to work with.

        Args:
            globalinstance: Return the Qt application thread pool instead of a new one.
        """
        if globalinstance:
            return QThreadPool.globalInstance()
        threadpool = QThreadPool()
        Pool._threadpools.append(threadpool)
        return threadpool

    @staticmethod
    def wait(timeout: int = -1) -> None:
        """Wait for all thread pools with the given timeout."""
        for pool in Pool._threadpools:
            pool.waitForDone(timeout)

    @staticmethod
    def clear() -> None:
        """Clear all thread pools."""
        for pool in Pool._threadpools:
            pool.clear()


def flatten(list_of_lists: typing.Iterable[typing.Iterable[AnyT]]) -> typing.List[AnyT]:
    """Flatten a list of lists into a single list with all elements."""
    return [elem for sublist in list_of_lists for elem in sublist]


def split(a: typing.List[AnyT], n: int) -> typing.Iterator[typing.List[AnyT]]:
    """Split list into n parts of approximately equal length.

    See https://stackoverflow.com/questions/2130016 for details.
    """
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(n))


def recursive_split(
    text: str, separator: str, updater: typing.Callable[[str], str]
) -> typing.List[str]:
    """Recursively split a string at separator applying an update callable.

    The string is split into parts and the update callable is applied to each part. The
    function is then called again on the updated text until no more separators remain.
    """
    splits = updater(text).split(separator)
    if len(splits) == 1:  # Updater did not add any new separators
        return splits
    nested = [recursive_split(part, separator, updater) for part in splits]
    return flatten(nested)


def remove_prefix(text: str, prefix: str) -> str:
    """Remove a prefix of a given string."""
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


def escape_ws(text: str, whitespace: str = " ", escape_char: str = "\\\\") -> str:
    r"""Escape whitespace in a given string.

    Example:
        >>> escape_ws("some spaced text")
        some\\ spaced\\ text

    Args:
        text: The text to escape whitespace in.
        whitespace: All characters that are treated as whitespace.
        escape_char: The character prepended to whitespace for escaping.
    Returns:
        Text with the whitespace escaped.
    """
    # First part matches all whitespace characters that are not prepended by escape_char
    # Second part replaces with the escape_char and the whitespace character
    return re.sub(rf"(?<!{escape_char})([{whitespace}])", rf"{escape_char}\1", text)


def unescape_ws(text: str, whitespace: str = " ", escape_char: str = "\\\\") -> str:
    r"""Undo escaping of whitespace in a given string.

    Example:
        >>> unescape_ws("some\\ spaced\\ text")
        some spaced text

    Args:
        text: The text to undo escaping of whitespace in.
        whitespace: All characters that are treated as whitespace.
        escape_char: The character prepended to whitespace for escaping.
    Returns:
        Text with the whitespace escaping undone.
    """
    # First part matches all whitespace characters that are prepended by escape_char
    # Second part replaces with the whitespace character
    return re.sub(rf"{escape_char}([{whitespace}])", r"\1", text)


def create_pixmap(
    color: str = "#FFFFFF",
    frame_color: str = "#000000",
    size: int = 256,
    frame_size: int = 0,
) -> QPixmap:
    """Draw pixmap with frame and inner color.

    Args:
        color: Name of the inner color in hex format.
        frame_color: Name of the frame color in hex format.
        size: Total size of the pixmap in px.
        frame_size: Size of the frame to draw in px.
    """
    # Initialize
    pixmap = QPixmap(size, size)
    painter = QPainter(pixmap)
    painter.setPen(Qt.NoPen)
    # Frame
    painter.setBrush(QColor(frame_color))
    painter.drawRect(pixmap.rect())
    # Inner
    painter.setBrush(QColor(color))
    x = y = frame_size
    width = height = pixmap.width() - 2 * frame_size
    painter.drawRect(x, y, width, height)
    return pixmap


def run_qprocess(cmd: str, *args: str, cwd=None) -> str:
    """Run a shell command synchronously using QProcess.

    Args:
        cmd: The command to run.
        args: Any arguments passed to the command.
        cwd: Directory of the command to run in.
    Returns:
        The standard output of the command.
    Raises:
        OSError on failure.
    """
    process = QProcess()
    if cwd is not None:
        process.setWorkingDirectory(cwd)
    process.start(cmd, args)
    if not process.waitForFinished():
        raise OSError("Error waiting for process")
    if process.exitStatus() != QProcess.NormalExit or process.exitCode() != 0:
        stderr = str(process.readAllStandardError(), "utf-8").strip()  # type: ignore
        raise OSError(stderr)
    return str(process.readAllStandardOutput(), "utf-8").strip()  # type: ignore


def is_optional_type(typ: typing.Any) -> bool:
    """Return True if typ is of type Optional."""
    origin = getattr(typ, "__origin__", None)
    types = getattr(typ, "__args__", ())
    return origin is typing.Union and isinstance(None, types)


def type_of_optional(typ: typing.Type) -> typing.Any:
    """Return T if typ is of type Optional[T]."""
    types = getattr(typ, "__args__", ())
    for elem in types:
        if not isinstance(elem, type(None)):
            return elem
    raise TypeError(f"{typ} is not of Optional type")


class AbstractQObjectMeta(wrappertype, ABCMeta):
    """Metaclass to allow setting to be an ABC as well as a QObject."""


def throttled(*, delay_ms: int):
    """Decorator to throttle function and only execute the final call after delay_ms.

    The implementation uses a QTimer to wait for the delay and therefore does not block
    the GUI. The final function call is executed upon timeout.
    """

    def decorator(func):
        throttle = Throttle(func, delay_ms=delay_ms)

        @functools.wraps(func)
        def inner(*args, **kwargs):
            """Additional wrapper required to correctly treat self."""
            throttle(*args, **kwargs)

        return inner

    return decorator


class Throttle(QTimer):
    """Timer class used as throttle for the throttled decorator.

    Class Attributes:
        throttles: List of all created instances.

    Attributes:
        _func: The throttled function wrapped.
        _args: Args and kwargs of the last function call if any.
    """

    throttles: typing.List["Throttle"] = []

    def __init__(self, func, *, delay_ms: int):
        super().__init__()
        self._func = func
        self._args = None
        self.setInterval(delay_ms)
        self.setSingleShot(True)
        self.throttles.append(self)

        def process():
            args, kwargs = self._args
            self._func(*args, **kwargs)
            self._args = None

        self.timeout.connect(process)

    def __call__(self, *args, **kwargs):
        """Store arguments of function call and (re-)start the timer."""
        if self.isActive():
            self.stop()
        self._args = args, kwargs
        self.start()

    @classmethod
    def unthrottle(cls):
        """Unthrottle all functions by setting timer interval to zero."""
        for throttle in cls.throttles:
            throttle.setInterval(0)

    @classmethod
    def stop_all(cls):
        """Stop all running throttles."""
        for throttle in cls.throttles:
            throttle.stop()
