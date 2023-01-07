# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import os

import pytest
import pytest_bdd as bdd

import vimiv.gui.completionwidget
from vimiv.utils import trash_manager


bdd.scenarios("completion.feature")


@pytest.fixture()
def completionwidget():
    return vimiv.gui.completionwidget.CompletionView.instance


@pytest.fixture()
def completiondata(completionwidget):
    model = completionwidget.model()
    return [
        [model.index(row, column).data() for column in range(model.columnCount())]
        for row in range(model.rowCount())
    ]


@bdd.then("no completion should be selected")
def check_no_completion_selected(completionwidget):
    assert not completionwidget.selectedIndexes()


@bdd.then(bdd.parsers.parse("a possible completion should contain {text}"))
def check_available_completion_text(completiondata, text):
    completion_text = "\n".join(" ".join(row) for row in completiondata)
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


@bdd.then(
    bdd.parsers.parse("the trash completion for '{basename}' should show the trashinfo")
)
def check_show_deletion_date(completiondata, basename):
    original_path, deletion_date = trash_manager.trash_info(basename)
    # Space for formatting and remove seconds
    expected_date = deletion_date.replace("T", " ")[:-3]
    expected_dir = os.path.dirname(original_path)
    for completion_text, completion_dir, completion_date in completiondata:
        completion_basename = completion_text.replace(":undelete ", "")
        if completion_basename == basename:
            assert expected_date == completion_date
            assert expected_dir == completion_dir
            break
    else:
        assert False, f"Completion for '{basename}' not found"
