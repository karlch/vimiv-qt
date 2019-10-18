# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest
import pytest_bdd as bdd

import vimiv.completion.completer
import vimiv.gui.completionwidget
from vimiv import api
from vimiv.completion import completionmodels


bdd.scenarios("completion.feature")


@pytest.fixture()
def completer():
    return api.objreg.get(vimiv.completion.completer.Completer)


@pytest.fixture()
def completionwidget():
    return api.objreg.get(vimiv.gui.completionwidget.CompletionView)


@bdd.then(bdd.parsers.parse("the completion model should be {model}"))
def check_completion_model(completer, model):
    models = {
        "command": completionmodels.CommandModel,
        "path": completionmodels.PathModel,
        "external": completionmodels.ExternalCommandModel,
        "settings": completionmodels.SettingsModel,
        "settings_option": completionmodels.SettingsOptionModel,
        "trash": completionmodels.TrashModel,
        "tag": completionmodels.TagModel,
    }
    assert isinstance(completer._proxy_model.sourceModel(), models[model])


@bdd.then(bdd.parsers.parse("the model mode should be {mode}"))
def check_completion_model_mode(completer, mode):
    assert api.modes.current() == api.modes.COMMAND  # Sanity check
    assert completer._cmd.mode == api.modes.get_by_name(mode)


@bdd.then("no completion should be selected")
def check_no_completion_selected(completionwidget):
    with pytest.raises(IndexError):
        completionwidget.row()


@bdd.then(bdd.parsers.parse("a possible completion should contain {text}"))
def check_selected_completion_text(completionwidget, text):
    model = completionwidget.model()
    completion_data = [
        model.index(row, column).data()
        for row in range(model.rowCount())
        for column in range(model.columnCount())
    ]
    completion_text = "\n".join(completion_data)
    assert text in completion_text


@bdd.then(bdd.parsers.parse("there should be {number:d} completion options"))
def check_number_completion_suggestions(completionwidget, number):
    model = completionwidget.model()
    assert model.rowCount() == number
