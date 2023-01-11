# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest
import pytest_bdd as bdd

from vimiv.gui import metadatawidget


bdd.scenarios("metadata.feature")


@pytest.fixture
def metadata():
    return metadatawidget.MetadataWidget.instance


@bdd.then("the metadata widget should be visible")
def check_metadata_widget_visible(metadata):
    assert metadata.isVisible()


@bdd.then("the metadata widget should not be visible")
def check_metadata_widget_not_visible(metadata):
    assert not metadata.isVisible()


@bdd.then(bdd.parsers.parse("the metadata text should contain '{text}'"))
def check_text_in_metadata(metadata, text):
    assert text in metadata.text()


@bdd.then(bdd.parsers.parse("the metadata text should not contain '{text}'"))
def check_text_not_in_metadata(metadata, text):
    assert text not in metadata.text()
