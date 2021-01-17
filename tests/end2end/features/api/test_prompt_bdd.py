# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest_bdd as bdd

from vimiv import api


bdd.scenarios("prompt.feature")


@bdd.given("I ask a question and answer with <key>", target_fixture="prompt_response")
def answer_question(answer_prompt, key):
    answer_prompt(key)
    return api.prompt.ask_question(title="end2end-question", body="Hello there?")


@bdd.then(bdd.parsers.parse("I expect <answer> as answer"))
def check_prompt(prompt_response, answer):
    answer = answer.lower()
    if answer in ("true", "yes", "1"):
        assert prompt_response
    elif answer in ("false", "no", "0"):
        assert not prompt_response
    elif answer == "none":
        assert prompt_response is None
    else:
        raise ValueError(f"Unexpected prompt answer '{answer}'")
