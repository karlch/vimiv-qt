# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest
import pytest_bdd as bdd

from vimiv.imutils import metadata


bdd.scenarios("metadata.feature")


@pytest.fixture
def metadatawidget():
    if metadata.has_metadata_support():
        from vimiv.gui.metadatawidget import MetadataWidget

        return MetadataWidget.instance
    raise ValueError("No metadata support for metadata tests")


@bdd.then("the metadata widget should be visible")
def check_metadata_widget_visible(metadatawidget):
    assert metadatawidget.isVisible()


@bdd.then("the metadata widget should not be visible")
def check_metadata_widget_not_visible(metadatawidget):
    assert not metadatawidget.isVisible()


@bdd.then(bdd.parsers.parse("the metadata text should contain '{text}'"))
def check_text_in_metadata(metadatawidget, text):
    assert text in metadatawidget.text()


@bdd.then(bdd.parsers.parse("the metadata text should not contain '{text}'"))
def check_text_not_in_metadata(metadatawidget, text):
    assert text not in metadatawidget.text()
