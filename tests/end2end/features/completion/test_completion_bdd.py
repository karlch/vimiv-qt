# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest
import pytest_bdd as bdd

import vimiv.gui.completionwidget


bdd.scenarios("completion.feature")


@pytest.fixture()
def completionwidget():
    return vimiv.gui.completionwidget.CompletionView.instance


@bdd.then("no completion should be selected")
def check_no_completion_selected(completionwidget):
    assert not completionwidget.selectedIndexes()


@bdd.then(bdd.parsers.parse("a possible completion should contain {text}"))
@bdd.then("a possible completion should contain <text>")
def check_available_completion_text(completionwidget, text):
    model = completionwidget.model()
    completion_data = [
        model.index(row, column).data()
        for row in range(model.rowCount())
        for column in range(model.columnCount())
    ]
    completion_text = "\n".join(completion_data)
    assert text in completion_text


@bdd.then(bdd.parsers.parse("there should be {number:d} completion option"))
@bdd.then(bdd.parsers.parse("there should be {number:d} completion options"))
def check_number_completion_suggestions(completionwidget, number):
    model = completionwidget.model()
    assert model.rowCount() == number


@bdd.then(bdd.parsers.parse("the completion row number {row:d} should be selected"))
def check_selected_completion_row(completionwidget, row):
    if row == -1:
        row = completionwidget.model().rowCount() - 1
    assert completionwidget.row() == row
