# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest_bdd as bdd

from vimiv.qt.gui import QPixmap

from vimiv import startup


bdd.scenarios("symlink.feature")


@bdd.given("I open the symlink test directory")
def open_symlink_test_directory(tmp_path):
    """Create a test directory with symlink(s) and open the base directory in vimiv.

    Structure:
    ├── lnstem -> stem
    └── stem
        └── leaf
    """
    base_directory = tmp_path / "directory"
    stem_directory = base_directory / "stem"
    leaf_directory = stem_directory / "leaf"
    leaf_directory.mkdir(parents=True)
    stem_symlink = base_directory / "lnstem"
    stem_symlink.symlink_to(stem_directory)
    argv = [str(base_directory)]
    args = startup.setup_pre_app(argv)
    startup.setup_post_app(args)


@bdd.given("I open the symlink image test directory")
def open_symlink_image_test_directory(tmp_path):
    """Create a test directory with symlink(s) and open the child directory in vimiv.

    Structure:
    ├── image.jpg
    └── child
        └── ln.jpg -> ../image.jpg
    """
    base_directory = tmp_path / "directory"
    base_image_path = base_directory / "image.jpg"
    child_directory = base_directory / "child"
    child_image_path = child_directory / "ln.jpg"
    child_directory.mkdir(parents=True)
    QPixmap(300, 300).save(str(base_image_path))
    child_image_path.symlink_to(base_image_path)
    argv = [str(child_directory)]
    args = startup.setup_pre_app(argv)
    startup.setup_post_app(args)
