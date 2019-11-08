# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.api._mark."""

import os
import re
from collections import namedtuple

import pytest

from vimiv.api._mark import Mark, Tag


@pytest.fixture
def mark(qtbot, mocker):
    instance = Mark()
    instance.marked = mocker.Mock()
    instance.unmarked = mocker.Mock()
    instance.watch()
    mocker.patch("vimiv.utils.files.is_image", return_value=True)
    yield instance


@pytest.fixture(autouse=True)
def tagdir(tmpdir, mocker):
    tmp_tagdir = tmpdir.mkdir("tags")
    mocker.patch("vimiv.utils.xdg.join_vimiv_data", return_value=tmp_tagdir)
    yield tmp_tagdir


@pytest.fixture
def tagwrite(tagdir):
    paths = ["first", "second"]
    name = "test"
    with Tag(name, read_only=False) as tag:
        tag.write(paths)
    path = os.path.join(tagdir, name)
    yield namedtuple("tagwrite", ["path", "content"])(path, paths)


def test_mark_single_image(mark):
    mark.mark(["image"])
    assert "image" in mark._marked
    assert mark.marked.called_once_with("image")


def test_mark_multiple_images(mark):
    mark.mark(["image1", "image2"])
    assert "image1" in mark._marked
    assert "image2" in mark._marked
    assert mark.marked.called_with("image1")
    assert mark.marked.called_with("image2")


def test_toggle_mark(mark):
    mark.mark(["image"])
    mark.mark(["image"])
    assert "image" not in mark._marked
    assert mark.unmarked.called_once_with("image")


def test_mark_clear(mark):
    mark.mark(["image"])
    mark.mark_clear()
    assert "image" not in mark._marked
    assert mark.unmarked.called_once_with("image")


def test_mark_restore(mark):
    mark.mark(["image"])
    mark.mark_clear()
    mark.mark_restore()
    assert "image" in mark._marked
    assert mark.marked.called_with("image")


def test_tag_write(tagwrite):
    assert os.path.isfile(tagwrite.path)


def test_tag_write_header(tagwrite):
    with open(tagwrite.path, "r") as f:
        comment_lines = [l for l in f if l.startswith(Tag.COMMENTCHAR)]
    assert "vimiv tag file" in comment_lines[0]
    date_re = re.compile(r"# created: \d\d\d\d-\d\d-\d\d \d\d:\d\d")
    assert (
        date_re.match(comment_lines[1]) is not None
    ), f"date not found in {comment_lines[1]}"


def test_tag_write_paths(tagwrite):
    with open(tagwrite.path, "r") as f:
        path_lines = [l.strip() for l in f if not l.startswith(Tag.COMMENTCHAR)]
    for path in tagwrite.content:
        assert path in path_lines


def test_tag_write_append_paths(tagwrite):
    all_paths = tagwrite.content + ["third"]
    with Tag(tagwrite.path, read_only=False) as tag:
        tag.write(all_paths)
    with Tag(tagwrite.path, read_only=True) as tag:
        read_paths = tag.read()
    assert len(set(read_paths)) == len(read_paths), "Append created duplicates"
    assert sorted(read_paths) == sorted(all_paths), "Append wrote wrong content"


def test_tag_read(tagwrite):
    with Tag(tagwrite.path, read_only=True) as tag:
        paths = tag.read()
    for path in tagwrite.content:
        assert path in paths
