# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

import os

import pytest_bdd as bdd

from vimiv.api._mark import Tag


bdd.scenarios("mark.feature")


@bdd.when("I remove the delete permissions")
def remove_delete_permission(mocker):
    mocker.patch("os.remove", side_effect=PermissionError)
    mocker.patch("shutil.rmtree", side_effect=PermissionError)


@bdd.when(bdd.parsers.parse("I create the tag '{name}' with permissions '{mode:o}'"))
def create_tag_with_permission(name, mode):
    with Tag(name, read_only=False):
        pass
    path = Tag.path(name)
    os.chmod(path, 0o000)


@bdd.when(bdd.parsers.parse("I insert an empty line into the tag file {name}"))
def insert_empty_lines_into_tag_file(name):
    assert os.path.isfile(Tag.path(name)), f"Tag file {name} does not exist"
    with open(Tag.path(name), "a", encoding="utf-8") as f:
        f.write("\n")


@bdd.then(bdd.parsers.parse("the tag file {name} should exist with {n_paths:d} paths"))
def check_tag_file(name, n_paths):
    assert os.path.isfile(Tag.path(name)), f"Tag file {name} does not exist"
    with Tag(name, "r") as tag:
        paths = tag.read()
    assert len(paths) == n_paths


@bdd.then(bdd.parsers.parse("the tag file {name} should not contain any empty lines"))
def check_tag_file_no_empty_line(name):
    assert os.path.isfile(Tag.path(name)), f"Tag file {name} does not exist"
    with open(Tag.path(name), "r", encoding="utf-8") as f:
        assert all(line.strip() for line in f)


@bdd.then(bdd.parsers.parse("the tag file {name} should not exist"))
def check_tag_file_not_exists(name):
    assert not os.path.exists(Tag.path(name))
