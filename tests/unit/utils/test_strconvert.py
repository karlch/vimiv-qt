# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils.strconvert."""

import pytest

from vimiv.utils import strconvert


@pytest.mark.parametrize("text", ["YES", "YeS", "yes", "TRUE", "True", "true", "1"])
def test_to_true_bool(text):
    assert strconvert.to_bool(text) is True


@pytest.mark.parametrize("text", ["NO", "No", "no", "FALSE", "False", "false", "0"])
def test_to_false_bool(text):
    assert strconvert.to_bool(text) is False


@pytest.mark.parametrize("text", ["2", "Any", "42.42", "-", "*"])
def test_fail_to_bool(text):
    with pytest.raises(strconvert.ConversionError, match="Cannot convert"):
        strconvert.to_bool(text)


def test_fail_to_bool_non_str_argument():
    with pytest.raises(AssertionError, match="Must be converting str"):
        strconvert.to_bool(12)


@pytest.mark.parametrize("text", [str(i) for i in range(0, 10)])
def test_to_int(text):
    assert strconvert.to_int(text) == int(text)
    assert strconvert.to_int(text) == int(text)


@pytest.mark.parametrize("text", [str(i) for i in range(2, -5, -1)])
def test_to_negative_int(text):
    assert strconvert.to_int(text, allow_sign=True) == int(text)


@pytest.mark.parametrize("text", ["hello", "12x12", "[12]", "0.1"])
def test_fail_to_int(text):
    with pytest.raises(strconvert.ConversionError, match="Cannot convert"):
        strconvert.to_int(text)


@pytest.mark.parametrize("text", [str(i) for i in range(-1, -5, -1)])
def test_fail_negative_to_int(text):
    with pytest.raises(ValueError, match="not allowed"):
        strconvert.to_int(text)


@pytest.mark.parametrize("text", ["0", "2", "42.42", "0.111"])
def test_to_float(text):
    assert strconvert.to_float(text) == float(text)


@pytest.mark.parametrize("text", ["2", "0", "-42.42", "-2.42"])
def test_to_negative_float(text):
    assert strconvert.to_float(text, allow_sign=True) == float(text)


@pytest.mark.parametrize("text", ["hello", "12x12", "[12]"])
def test_fail_to_float(text):
    with pytest.raises(strconvert.ConversionError, match="Cannot convert"):
        strconvert.to_float(text)


@pytest.mark.parametrize("text", ["-1", "-2", "-42.42", "-0.111"])
def test_fail_negative_to_float(text):
    with pytest.raises(ValueError, match="not allowed"):
        strconvert.to_float(text)
