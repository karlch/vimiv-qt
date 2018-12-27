# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest
import pytest_bdd as bdd

from vimiv.completion import completionmodels, completer
from vimiv.gui import completionwidget
from vimiv.modes import modehandler, Modes


bdd.scenarios("completion.feature")


@bdd.then(bdd.parsers.parse("the completion model should be {model}"))
def check_completion_model(model):
    models = {"command": completionmodels.command,
              "path": completionmodels.paths,
              "external": completionmodels.external,
              "settings": completionmodels.settings,
              "trash": completionmodels.trash}
    assert completer.instance()._modelfunc == models[model]


@bdd.then(bdd.parsers.parse("the model mode should be {mode}"))
def check_completion_model_mode(mode):
    assert modehandler.current() == Modes.COMMAND  # Sanity check
    assert modehandler.last() == Modes.get_by_name(mode)


@bdd.then("no completion should be selected")
def check_no_completion_selected():
    with pytest.raises(IndexError):
        completionwidget.instance().row()
