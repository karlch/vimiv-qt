# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

"""Tests for vimiv.config.settings."""

import pytest

from vimiv.api import settings


@pytest.fixture()
def prompt_setting():
    """Fixture to retrieve a clean prompt setting."""
    yield settings.PromptSetting(
        "prompt",
        settings.PromptSetting.Options.ask,
        question_title="Title",
        question_body="What are we doing?",
    )


def test_init_setting():
    b = settings.BoolSetting("bool", True)
    assert b.default
    assert b.value


def test_check_default_after_change_for_setting():
    b = settings.BoolSetting("bool", True)
    b.value = False
    assert b.default


@pytest.mark.parametrize("value", (False, "False", "no"))
def test_set_bool_setting(value):
    b = settings.BoolSetting("bool", True)
    b.value = value
    assert not b.value
    assert not b


def test_toggle_bool_setting():
    b = settings.BoolSetting("bool", False)
    b.toggle()
    assert b.value


@pytest.mark.parametrize("value", (2, "2", 2.0))
def test_set_int_setting(value):
    i = settings.IntSetting("int", 1)
    i.value = value
    assert i.value == 2


def test_add_int_setting():
    i = settings.IntSetting("int", 2)
    i += 3
    assert i.value == 5


def test_multiply_int_setting():
    i = settings.IntSetting("int", 5)
    i *= 2
    assert i.value == 10


@pytest.mark.parametrize("value", (3.3, "3.3"))
def test_set_float_setting(value):
    f = settings.FloatSetting("float", 2.2)
    f.value = value
    assert f.value == pytest.approx(3.3)


def test_add_float_setting():
    f = settings.FloatSetting("float", 1.1)
    f += 0.3
    assert f.value == pytest.approx(1.4)


def test_multiply_float_setting():
    f = settings.FloatSetting("float", 4.2)
    f *= 0.5
    assert f.value == pytest.approx(2.1)


@pytest.mark.parametrize("value", (64, "64"))
def test_set_thumbnail_setting(value):
    t = settings.ThumbnailSizeSetting("thumb", 128)
    t.value = value
    assert t.value == 64


def test_fail_set_thumbnail_setting_non_int():
    t = settings.ThumbnailSizeSetting("thumb", 128)
    with pytest.raises(ValueError, match="Cannot convert 'any'"):
        t.value = "any"


def test_fail_set_thumbnail_setting_wrong_int():
    t = settings.ThumbnailSizeSetting("thumb", 128)
    with pytest.raises(ValueError, match="must be one of"):
        t.value = 13


@pytest.mark.parametrize(
    "start, up, expected",
    [(128, True, 256), (512, True, 512), (128, False, 64), (64, False, 64)],
)
def test_step_thumbnail_size(start, up, expected):
    t = settings.ThumbnailSizeSetting("thumb", start)
    t.step(up=up)
    assert t.value == expected


def test_set_str_setting():
    s = settings.StrSetting("string", "default")
    s.value = "new"
    assert s.value == "new"


def test_fail_get_unstored_setting():
    with pytest.raises(KeyError):
        settings.get("any")


@pytest.mark.parametrize(
    "value, expected",
    (
        ("true", settings.PromptSetting.Options.true),
        ("Yes", settings.PromptSetting.Options.true),
        ("1", settings.PromptSetting.Options.true),
        ("false", settings.PromptSetting.Options.false),
        ("NO", settings.PromptSetting.Options.false),
        ("0", settings.PromptSetting.Options.false),
        ("AsK", settings.PromptSetting.Options.ask),
    ),
)
def test_set_prompt_setting(prompt_setting, value, expected):
    prompt_setting.value = value
    assert prompt_setting.value == expected


@pytest.mark.parametrize("answer", (True, False))
def test_ask_prompt_setting(mocker, prompt_setting, answer):
    def ask_question(*args, **kwargs):
        return answer

    mocker.patch("vimiv.api.prompt.ask_question", ask_question)

    assert bool(prompt_setting) == answer


def test_set_order_setting():
    o = settings.OrderSetting("order", "alphabetical")
    o.value = "natural"
    assert o.value == "natural"


def test_set_order_setting_non_str():
    o = settings.OrderSetting("order", "alphabetical")
    with pytest.raises(ValueError, match="must be one of"):
        o.value = 1


def test_set_order_setting_non_valid():
    o = settings.OrderSetting("order", "alphabetical")
    with pytest.raises(ValueError, match="must be one of"):
        o.value = "invalid"


@pytest.mark.parametrize("reverse", [True, False])
@pytest.mark.parametrize(
    "ordering_name, values, expected_values",
    [
        ("alphabetical", ["a.j", "c.j", "b.j"], ["a.j", "b.j", "c.j"]),
        ("natural", ["a5.j", "a11.j", "a3.j"], ["a3.j", "a5.j", "a11.j"]),
    ],
)
def test_order_setting_sort(
    monkeypatch, ordering_name, values, expected_values, reverse
):
    monkeypatch.setattr(settings.sort.reverse, "value", reverse)
    o = settings.OrderSetting("order", ordering_name)
    sorted_values = o.sort(values)
    expected_values = expected_values[::-1] if reverse else expected_values
    assert sorted_values == expected_values


@pytest.mark.parametrize("reverse", [True, False])
@pytest.mark.parametrize("ignore_case", [True, False])
def test_order_setting_sort_none(monkeypatch, reverse, ignore_case):
    values = ["a5.j", "A6.j", "a11.j", "a3.j"]
    monkeypatch.setattr(settings.sort.reverse, "value", reverse)
    monkeypatch.setattr(settings.sort.ignore_case, "value", ignore_case)
    o = settings.OrderSetting("order", "none")
    sorted_values = o.sort(values)
    assert sorted_values == values


@pytest.mark.parametrize("ignore_case", [True, False])
def test_order_setting_sort_ignore_case(monkeypatch, ignore_case):
    monkeypatch.setattr(settings.sort.ignore_case, "value", ignore_case)
    o = settings.OrderSetting("order", "alphabetical")

    values = ["c.j", "B.j", "a.j", "D.j"]
    if ignore_case:
        expected_values = ["a.j", "B.j", "c.j", "D.j"]
    else:
        expected_values = ["B.j", "D.j", "a.j", "c.j"]

    sorted_values = o.sort(values)

    assert sorted_values == expected_values


def test_order_setting_sort_basename():
    o = settings.OrderSetting("order", "alphabetical")
    values = ["a/c.j", "c/b.j", "c/a.j"]
    sorted_values = o.sort(values)
    assert sorted_values == ["c/a.j", "c/b.j", "a/c.j"]
