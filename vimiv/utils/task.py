# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Utilities to convert functions to tasks which can call non-GUI-blocking functions."""

import time
import types
from concurrent import futures
from contextlib import suppress
from functools import wraps

from PyQt5.QtCore import QCoreApplication, QEventLoop


def register(single=False):
    """Decorator to convert function into task that can call non-GUI-blocking functions.

    Usage:
        >>> @task.register()
        >>> def my_function():
        >>>     ...
        >>>     result = yield task.func(other_function, arg, kwarg=kwarg)
        >>>     ...

    Args:
        single: Only send the last non-blocking function result back to the generator.
    """

    def decorator(wrapped_func):
        wrapped_func.call_id = 0

        def advance(generator, local_id=None):
            if not isinstance(generator, types.GeneratorType):
                raise TypeError("task must wrap a generator")
            with suppress(StopIteration):
                result = next(generator)
                while True:
                    if local_id is not None and local_id != wrapped_func.call_id:
                        return
                    result = generator.send(result)

        @wraps(wrapped_func)
        def inner_all(*args, **kwargs):
            generator = wrapped_func(*args, **kwargs)
            advance(generator)

        @wraps(wrapped_func)
        def inner_single(*args, **kwargs):
            generator = wrapped_func(*args, **kwargs)
            wrapped_func.call_id += 1
            advance(generator, wrapped_func.call_id)

        if single:
            return inner_single
        return inner_all

    return decorator


def func(
    function,
    *args,
    executor_class=futures.ThreadPoolExecutor,
    future_timeout=0.01,
    **kwargs,
):
    """Non-GUI-blocking function call.

    Can be used by functions decorated with the :func:``register`` decorator to turn a
    regular function call into a non-GUI-blocking one.

    Usage:
        >>> # Regular call
        >>> result = myfunc(arg, kwarg=kwarg)
        >>> # Non-blocking call
        >>> result = yield task.func(myfunc, arg, kwarg=kwarg)

    Args:
        function: The blocking function converted into a non-block one.
        *args: Any arguments passed to the function.
        executor_class: Executor from futures module to use for async functionality.
        future_timeout: Time to wait for the function before giving control to the GUI.
        **kwargs: Any keyword arguments passed to the function.
    """
    with executor_class() as executor:
        future = executor.submit(function, *args, **kwargs)
        while True:
            try:
                result = future.result(future_timeout)
            except futures.TimeoutError:
                advance_gui(future_timeout)
            else:
                return result


def sleep(duration, executor_class=futures.ThreadPoolExecutor, future_timeout=0.01):
    """Non-GUI blocking sleep.

    See :func:``func`` for implementation details.

    Args:
        duration: The number of seconds to sleep.
        executor_class: Executor from futures module to use for async functionality.
        future_timeout: Time to wait for the function before giving control to the GUI.
    """
    func(
        time.sleep,
        duration,
        executor_class=executor_class,
        future_timeout=future_timeout,
    )


def advance_gui(maxtime):
    """Advance the Qt main loop for maxtime seconds."""
    maxtime_ms = int(maxtime * 1000)
    QCoreApplication.instance().processEvents(QEventLoop.AllEvents, maxtime_ms)
