# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

from PyQt5.QtCore import QTimer, Qt

import pytest_bdd as bdd

import vimiv.gui.prompt
from vimiv import api


bdd.scenarios("prompt.feature")


def get_prompt(mainwindow):
    """Retrieve the current prompt widget."""
    widgets = mainwindow.findChildren(vimiv.gui.prompt.Prompt)
    assert len(widgets) == 1, "Wrong number of prompts found"
    return widgets[0]


@bdd.given(bdd.parsers.parse("I ask a question and press <key>"))
def answer_question(qtbot, mainwindow, key):
    # We define ask and answer in one fixture to avoid a blocking prompt
    keys = {
        "y": Qt.Key_Y,
        "n": Qt.Key_N,
        "<return>": Qt.Key_Return,
        "<escape>": Qt.Key_Escape,
    }
    try:
        qkey = keys[key]
    except KeyError:
        raise KeyError(
            f"Unexpected prompt key '{key}', expected one of: {', '.join(keys)}"
        )

    def click_prompt_key():
        prompt = get_prompt(mainwindow)
        qtbot.keyClick(prompt, qkey)

    QTimer.singleShot(0, lambda: qtbot.waitUntil(click_prompt_key))
    yield api.prompt.ask_question(title="end2end-question", body="Hello there?")


@bdd.then(bdd.parsers.parse("I expect <answer> as answer"))
def check_prompt(answer_question, answer):
    answer = answer.lower()
    if answer in ("true", "yes", "1"):
        assert answer_question
    elif answer in ("false", "no", "0"):
        assert not answer_question
    elif answer == "none":
        assert answer_question is None
    else:
        raise ValueError(f"Unexpected prompt answer '{answer}'")
