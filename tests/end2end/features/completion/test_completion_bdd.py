# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest
import pytest_bdd as bdd

from vimiv import api
from vimiv.apimodules import completer
from vimiv.completion import completionmodels
from vimiv.gui import completionwidget


bdd.scenarios("completion.feature")


@bdd.then(bdd.parsers.parse("the completion model should be {model}"))
def check_completion_model(model):
    models = {
        "command": completionmodels.CommandModel,
        "path": completionmodels.PathModel,
        "external": completionmodels.ExternalCommandModel,
        "settings": completionmodels.SettingsModel,
        "settings_option": completionmodels.SettingsOptionModel,
        "trash": completionmodels.TrashModel,
    }
    assert isinstance(completer.instance().proxy_model.sourceModel(), models[model])


@bdd.then(bdd.parsers.parse("the model mode should be {mode}"))
def check_completion_model_mode(mode):
    assert api.modes.current() == api.modes.COMMAND  # Sanity check
    assert completer.instance()._cmd.mode == api.modes.get_by_name(mode)


@bdd.then("no completion should be selected")
def check_no_completion_selected():
    with pytest.raises(IndexError):
        completionwidget.instance().row()
