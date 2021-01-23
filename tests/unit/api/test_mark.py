# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.api._mark."""

import collections
import os
import re

import pytest

from vimiv import api
from vimiv.api._mark import Mark, Tag


@pytest.fixture
def mark(qtbot, mocker, monkeypatch):
    instance = Mark()
    mocker.patch.object(instance, "marked")
    mocker.patch.object(instance, "unmarked")
    mocker.patch("vimiv.utils.files.is_image", return_value=True)
    yield instance
    # TODO think about a proper mocking method
    Mark.instance = api.mark  # Reset objreg instance to the one from api


@pytest.fixture(autouse=True)
def tagdir(tmp_path, mocker):
    tmp_tagdir = tmp_path / "tags"
    tmp_tagdir.mkdir()
    mocker.patch.object(Tag, "dirname", return_value=str(tmp_tagdir))
    yield str(tmp_tagdir)


@pytest.fixture
def tagwrite(tagdir):
    paths = ["first", "second"]
    name = "test"
    with Tag(name, read_only=False) as tag:
        tag.write(paths)
    path = os.path.join(tagdir, name)
    yield collections.namedtuple("tagwrite", ["path", "content"])(path, paths)


def test_mark_single_image(mark):
    mark.mark(["image"])
    assert mark.is_marked("image")
    mark.marked.emit.assert_called_once_with("image")


def test_mark_multiple_images(mark):
    images = ["image1", "image2"]
    mark.mark(images)
    for image in images:
        assert mark.is_marked(image)
        mark.marked.emit.assert_any_call(image)


def test_mark_action_toggle(mark):
    mark.mark(["image"])
    mark.mark(["image"])
    assert not mark.is_marked("image")
    mark.unmarked.emit.assert_called_once_with("image")


def test_mark_action_mark(mark):
    mark.mark(["image"], action=Mark.Action.Mark)
    mark.mark(["image"], action=Mark.Action.Mark)
    assert mark.is_marked("image")
    mark.marked.emit.assert_called_once_with("image")


def test_mark_action_unmark(mark):
    mark.mark(["image"])
    mark.mark(["image"], action=Mark.Action.Unmark)
    mark.mark(["image"], action=Mark.Action.Unmark)
    assert not mark.is_marked("image")
    mark.unmarked.emit.assert_called_once_with("image")


def test_mark_clear(mark):
    mark.mark(["image"])
    mark.mark_clear()
    assert not mark.is_marked("image")
    mark.unmarked.emit.assert_called_once_with("image")


def test_mark_restore(mark):
    mark.mark(["image"])
    mark.mark_clear()
    mark.mark_restore()
    assert mark.is_marked("image")
    mark.marked.emit.assert_called_with("image")


def test_tag_write(tagwrite):
    assert os.path.isfile(tagwrite.path)


def test_tag_write_header(tagwrite):
    with open(tagwrite.path, "r") as f:
        comment_lines = [line for line in f if line.startswith(Tag.COMMENTCHAR)]
    assert "vimiv tag file" in comment_lines[0]
    date_re = re.compile(r"# created: \d\d\d\d-\d\d-\d\d \d\d:\d\d")
    assert (
        date_re.match(comment_lines[1]) is not None
    ), f"date not found in {comment_lines[1]}"


def test_tag_write_paths(tagwrite):
    with open(tagwrite.path, "r") as f:
        path_lines = [
            line.strip() for line in f if not line.startswith(Tag.COMMENTCHAR)
        ]
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


@pytest.mark.parametrize("parts", [("tag",), ("category", "tag")])
def test_tag_delete(mark, parts):
    basename = parts[0]
    name = os.path.join(*parts)
    tagpath = Tag.path(name)
    os.makedirs(os.path.dirname(tagpath), exist_ok=True, mode=0o700)
    with open(Tag.path(name), "w") as f:
        f.write("My tag content")
    mark.tag_delete(basename)
    assert not os.path.exists(Tag.path(basename))
