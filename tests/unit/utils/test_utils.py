# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils"""

import inspect
import os
import typing
from typing import get_type_hints

from PyQt5.QtCore import pyqtSignal, QObject, QByteArray

import pytest

from vimiv import utils


@pytest.fixture()
def cached_method_cls(mocker):
    """Fixture to retrieve a class with mock utilities and a cached method."""

    class CachedMethodCls:

        RESULT = 42

        def __init__(self):
            self.mock = mocker.Mock(return_value=self.RESULT)

        @utils.cached_method
        def method(self):
            return self.mock()

    yield CachedMethodCls()


def test_add_html():
    assert utils.add_html("hello", "b") == "<b>hello</b>"


def test_add_html_multiple():
    assert utils.add_html("hello", "b", "i") == "<i><b>hello</b></i>"


def test_strip_html():
    assert utils.strip_html("<b>hello</b>") == "hello"


def test_wrap_style_span():
    assert (
        utils.wrap_style_span("color: red", "text")
        == "<span style='color: red;'>text</span>"
    )


@pytest.mark.parametrize("n_rows", (1, 5))
def test_format_html_table(n_rows):
    # Format by hand
    iterable = list(range(n_rows))
    row = "<tr><td>{num}</td><td style='padding-left: 2ex'>{numsq}</td></tr>"
    text = "\n".join(row.format(num=num, numsq=num ** 2) for num in iterable)
    expected = "<table>" + text + "</table>"
    # Format using function
    content = [(f"{num:d}", f"{num**2:d}") for num in iterable]
    result = utils.format_html_table(content)
    # Ensure equal
    assert result == expected


@pytest.mark.parametrize("escaped", (True, False))
def test_replace_unless_escaped(escaped):
    pattern = " "
    repl = "&nbsp;"
    text = f"before{pattern}after"
    if escaped:
        expected = text
        text = text.replace(pattern, rf"\{pattern}")
    else:
        expected = text.replace(pattern, repl)
    assert utils.replace_unless_escaped(pattern, repl, text) == expected


@pytest.mark.parametrize(
    "sequence, elems, expected",
    [
        ("abc", "a", True),
        ("abc", "d", False),
        ("abc", "bc", True),
        (range(5), 4, True),
        (range(5), 10, False),
        (range(5), (2, 3), True),
        ("", "52", False),
        ("imag*", "*?[]", True),
    ],
)
def test_contains_any(sequence, elems, expected):
    assert utils.contains_any(sequence, elems) == expected


@pytest.mark.parametrize("joinchar", (", ", ":"))
@pytest.mark.parametrize("iterable", (range(4), "abcd"))
def test_quotedjoin(iterable, joinchar):
    iterable = list(iterable)
    quoted_iterable = ("'" + str(elem) + "'" for elem in iterable)
    expected = joinchar.join(quoted_iterable)
    assert expected == utils.quotedjoin(iterable, joinchar=joinchar)


@pytest.mark.parametrize("char", "*?[]")
def test_glob_escape(char):
    assert utils.escape_glob(rf"test{char}.jpg") == f"test{char}.jpg"
    assert utils.escape_glob(rf"test\{char}.jpg") == f"test[{char}].jpg"


def test_clamp_with_min_and_max():
    assert utils.clamp(2, 0, 5) == 2
    assert utils.clamp(2, 3, 5) == 3
    assert utils.clamp(2, 0, 1) == 1


def test_clamp_with_max():
    assert utils.clamp(2, None, 5) == 2
    assert utils.clamp(2, None, 1) == 1


def test_clamp_with_min():
    assert utils.clamp(2, 0, None) == 2
    assert utils.clamp(2, 3, None) == 3


def test_clamp_with_none():
    assert utils.clamp(2, None, None) == 2


@pytest.mark.parametrize("function", (utils.is_method, utils.clamp, utils.flatten))
def test_parameter_names(function):
    signature = inspect.signature(function)
    assert utils.parameter_names(function) == tuple(signature.parameters)


@pytest.mark.parametrize("type_hint", ("int", int))
def test_slot(type_hint):
    class Dummy(QObject):

        signal = pyqtSignal(int)

        def __init__(self):
            super().__init__()
            self.value = 0

    dummy = Dummy()

    @utils.slot
    def test(x: type_hint):
        dummy.value = x

    dummy.signal.connect(test)
    dummy.signal.emit(42)
    assert dummy.value == 42


def test_slot_ignore_self():
    def test(self, name: str):
        ...

    slot_args = utils._slot_args(test, get_type_hints(test))
    assert slot_args == [str]


def test_slot_add_returntype():
    def test(self, name: str) -> str:
        ...

    slot_kwargs = utils._slot_kwargs(get_type_hints(test))
    assert slot_kwargs == {"result": str}


def test_slot_fails_without_type_annotations():
    with pytest.raises(utils.AnnotationNotFound):

        @utils.slot
        def dummy(x):  # pylint: disable=unused-variable
            """Dummy function to check for raising the exception."""
            ...


def test_flatten():
    list_of_lists = [[1, 2], [3, 4]]
    assert utils.flatten(list_of_lists) == [1, 2, 3, 4]


def test_recursive_split():
    def updater(text):
        """Return a text containing two numbers decremented by one, break at 0.

        This results in doubling the number of numbers in every iteration and
        decrementing all numbers by one. Eventually 2**(N - 1) zeros are left.
        """
        number = int(text) - 1
        if number > 0:
            return f"{number}.{number}"
        return "0"

    for number in range(1, 6):
        expected = ["0"] * 2 ** (number - 1)
        assert utils.recursive_split(str(number), ".", updater) == expected


def test_remove_prefix():
    assert utils.remove_prefix("start hello", "start") == " hello"


def test_remove_prefix_not_found():
    assert utils.remove_prefix("start hello", "starter") == "start hello"


@pytest.mark.parametrize(
    "formattext",
    ("in{char}between", "many{char}of{char}them", "{char}prepending", "trailing{char}"),
)
@pytest.mark.parametrize("char", (" ", r"\\"))
def test_escape_unescape_chars(formattext, char):
    text = formattext.format(char=char)
    expected = formattext.format(char="\\" + char)
    _run_escape_unescape(text, char, expected)


def test_escape_unescape_multiple_chars():
    text = "a text:with\tsome;characters"
    expected = "a\\ text\\:with\\\tsome\\;characters"
    chars = " :;\t"
    _run_escape_unescape(text, chars, expected)


def _run_escape_unescape(text, chars, expected):
    escaped = utils.escape_chars(text, chars)
    assert expected == escaped
    unescaped = utils.unescape_chars(escaped, chars)
    assert unescaped == text


def test_cached_method_result(cached_method_cls):
    # First is the initial call
    assert cached_method_cls.method() == cached_method_cls.RESULT
    # Second is the cached result
    assert cached_method_cls.method() == cached_method_cls.RESULT


def test_cached_calls_expensive_once(cached_method_cls):
    cached_method_cls.method()
    cached_method_cls.method()
    cached_method_cls.mock.assert_called_once()


def test_qbytearray_to_str():
    text = "text"
    qbytearray = QByteArray(text.encode())
    assert utils.qbytearray_to_str(qbytearray) == text


def test_run_qprocess():
    assert utils.run_qprocess("pwd") == os.getcwd()


def test_run_qprocess_in_other_dir(tmpdir):
    directory = str(tmpdir.mkdir("directory"))
    assert utils.run_qprocess("pwd", cwd=directory) == directory


@pytest.mark.parametrize(
    "command, args", (("NoTaCoMmAnD", []), ("ls", ["--not-a-flag-for-ls"]))
)
def test_fail_run_qprocess_raises_oserror(command, args):
    with pytest.raises(OSError):
        utils.run_qprocess(command, *args)


@pytest.mark.parametrize("typ", (int, float, str, bool))
def test_is_optional_type(typ):
    optional_type = typing.Optional[typ]
    assert utils.is_optional_type(optional_type)
    assert not utils.is_optional_type(typ)


@pytest.mark.parametrize("typ", (int, float, str, bool))
def test_type_of_optional(typ):
    optional_type = typing.Optional[typ]
    assert utils.type_of_optional(optional_type) == typ


def test_fail_type_of_optional():
    with pytest.raises(TypeError, match="is not of Optional type"):
        assert utils.type_of_optional(int)


@pytest.mark.parametrize("n_calls", (1, 16, 1000))
def test_call_throttled_function_once(qtbot, n_calls):
    """Ensure throttled function is only executed for the call."""
    calls = []

    @utils.throttled(delay_ms=1)
    def local_task(call_id):
        nonlocal calls
        calls.append(call_id)

    def check_calls():
        assert calls == [n_calls]

    for i in range(1, n_calls + 1):
        local_task(i)

    qtbot.waitUntil(check_calls)
