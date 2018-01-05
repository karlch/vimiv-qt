# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest
import pytest_bdd as bdd

from vimiv.completion import completionmodels
from vimiv.utils import objreg


bdd.scenarios("completion.feature")


@bdd.then(bdd.parsers.parse("the completion model should be {model}"))
def check_completion_model(model):
    completer = objreg.get("completer")
    models = {"command": completionmodels.command,
              "path": completionmodels.paths,
              "external": completionmodels.external,
              "settings": completionmodels.settings,
              "trash": completionmodels.trash,}
    assert completer._modelfunc == models[model]


@bdd.then(bdd.parsers.parse("the model mode should be {mode}"))
def check_completion_model_mode(mode):
    completer = objreg.get("completer")
    assert completer._mode == mode


@bdd.then("no completion should be selected")
def check_no_completion_selected():
    compwidget = objreg.get("completion")
    with pytest.raises(IndexError):
        compwidget.row()
