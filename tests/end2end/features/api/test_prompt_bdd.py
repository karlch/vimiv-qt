# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest_bdd as bdd

from vimiv import api


bdd.scenarios("prompt.feature")


@bdd.given(bdd.parsers.parse("I ask a question and press <key>"))
def answer_question(qtbot, answer_prompt, key):
    answer_prompt(key)
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
