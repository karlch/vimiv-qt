# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tools to help with migration from the deprecated gtk version."""

import os
import shutil
from typing import NamedTuple, Optional, List

from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget

import vimiv
from vimiv.widgets import PopUp

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
    WelcomePopUp.gtk_installed = True


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


def run_welcome_popup(parent: QWidget = None) -> None:
    """Show pop up at startup if the gtk version was installed."""
    if WelcomePopUp.gtk_installed:
        WelcomePopUp(parent=parent)


class WelcomePopUp(PopUp):
    """Pop up that displays a short welcome message for users coming from gtk."""

    gtk_installed = False

    def __init__(self, parent=None):
        super().__init__(f"{vimiv.__name__} - welcome to qt", parent=parent)
        url = "https://karlch.github.io/vimiv-qt/documentation/migrating.html"
        gh_url = "https://github.com/karlch/vimiv-qt/issues"
        layout = QVBoxLayout()
        label = QLabel()
        label.setText(
            "<h2>Welcome to the new qt version!</h2>"
            "Looks like this is your first time running the new qt version.<br>"
            "Following is some information to get you started.<br>"
            "Much more details on migration are "
            f"<a href='{url}'>available online</a>.<br><br>"
            "A backup of your vimiv directories was created and your tags have been<br>"
            "migrated. Keybindings and commands have largely changed, so<br>"
            "unfortunately any custom changes are not automatically ported. The<br>"
            "online documentation should help you migrating. Sorry for the<br>"
            "inconvenience. I hope the large improvements here will outweigh the<br>"
            "extra work of migration.<br><br>"
            "If you have any problems or questions, do not hesitate to<br>"
            f"<a href='{gh_url}'>open an issue on github</a> or to "
            "<a href='mailto:karlch@protonmail.com'>contact me directly</a>.<br><br>"
            "To show this message again, run ':welcome-to-qt'."
        )
        layout.addWidget(label)
        self.setLayout(layout)
        self.show()
