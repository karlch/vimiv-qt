# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest
import pytest_bdd as bdd

from vimiv.gui import metadata_widget


bdd.scenarios("metadata.feature")


@pytest.fixture
def metadata():
    yield metadata_widget.MetadataWidget.instance


@bdd.then("the metadata widget should be visible")
def check_metadata_widget_visible(metadata):
    assert metadata.isVisible()


@bdd.then("the metadata widget should not be visible")
def check_metadata_widget_not_visible(metadata):
    assert not metadata.isVisible()
