# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tools to help with migration from the deprecated gtk version."""

import os
import shutil
from typing import NamedTuple, Optional, List

from . import xdg


class XdgDirectories(NamedTuple):
    """Storage class for the relevant vimiv xdg directories."""

    cache_dir: Optional[str]
    config_dir: Optional[str]
    data_dir: Optional[str]


def gtk_version_installed() -> bool:
    """Check if the gtk version is installed."""
    gtk_config_path = xdg.vimiv_config_dir("vimivrc")
    return os.path.isfile(gtk_config_path)


def run() -> None:
    """Run backup and migration if the gtk version is installed."""
    if not gtk_version_installed():
        return
    print("Trying to migrate existing gtk configuration...")
    backup_dirs = backup()
    if backup_dirs.data_dir is not None:  # Error creating backup
        migrate_tags(backup_dirs.data_dir)


def backup() -> XdgDirectories:
    """Create a backup of all gtk vimiv directories."""
    backup_str = "-gtk-backup"
    backup_dirs: List[Optional[str]] = []
    for dirname in (
        xdg.vimiv_cache_dir(),
        xdg.vimiv_config_dir(),
        xdg.vimiv_data_dir(),
    ):
        try:
            backup_dirname = dirname + backup_str
            shutil.move(dirname, backup_dirname)
            print(f"... Created backup of '{dirname}' at '{backup_dirname}'")
            backup_dirs.append(backup_dirname)
        except OSError as e:
            print(f"... Error backing up {dirname}: {e}")
            backup_dirs.append(None)
    return XdgDirectories(*backup_dirs)


def migrate_tags(gtk_data_dir: str) -> None:
    """Migrate gtk tag file to the new path.

    Args:
        gtk_data_dir: Path to the old gtk data directory.
    """
    gtk_tagdir = os.path.join(gtk_data_dir, "Tags")
    if os.path.isdir(gtk_tagdir):
        shutil.copytree(gtk_tagdir, xdg.vimiv_data_dir("tags"))
        print("... Moved tag directory")
