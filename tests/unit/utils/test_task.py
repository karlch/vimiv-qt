# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Unit tests for vimiv.utils.task."""

import functools
import time
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool

import pytest

from vimiv.utils import task


def test_retrieve_from_task_func(qtbot):
    """Ensure the async function returns the value back to the generator."""
    expected = 42

    def helper():
        return expected

    @task.register()
    def local_task():
        value = yield task.func(helper)
        assert value == expected

    local_task()


def test_retrieve_multiple_from_task_func(qtbot):
    """Ensure the async function returns multiple values back to the generator."""
    expected = 42
    n_yields = 5

    def helper(i):
        return i * expected

    expected_values = [i * expected for i in range(n_yields)]
    values = []

    @task.register()
    def local_task():
        for i in range(n_yields):
            value = yield task.func(helper, i)
            values.append(value)

    local_task()
    assert values == expected_values


def test_fail_wrapping_non_generator():
    """Ensure wrapping a function that is not a generator fails."""

    @task.register()
    def anything():
        """Function that is not a generator."""

    with pytest.raises(TypeError, match="must wrap a generator"):
        anything()


def test_task_sleep(qtbot):
    """Ensure async sleep takes as long as expected in the task."""

    @task.register()
    def local_task():
        start = time.time()
        duration = 0.001
        yield task.sleep(duration)
        elapsed = time.time() - start
        assert elapsed >= duration

    local_task()


@pytest.mark.parametrize("n_calls", (1, 16))
@pytest.mark.flaky
def test_call_single_task_once(qtbot, n_calls):
    """Ensure single type tasks only continue for the last scheduled task."""
    repeat_task(n_calls, single=True)


@pytest.mark.parametrize("n_calls", (1, 16))
@pytest.mark.flaky
def test_call_task_multiple(qtbot, n_calls):
    """Ensure multiple type tasks continue for all scheduled tasks."""
    repeat_task(n_calls, single=False)


def repeat_task(n_times, single=False):
    """Helper function to repeat a task n_times."""
    sleep_duration = 0.001
    future_timeout = sleep_duration / 10
    calls = []

    @task.register(single=single)
    def local_task(number):
        yield task.sleep(sleep_duration, future_timeout=future_timeout)
        calls.append(number)

    with ThreadPool(n_times) as pool:
        pool.map(local_task, range(n_times))

    # Only the last call for single mode, all of them otherwise
    expected = [n_times - 1] if single else list(range(n_times))
    assert sorted(calls) == expected, f"Error for single={single}"
