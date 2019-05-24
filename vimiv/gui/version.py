# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Pop-up window to display version information."""

from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtGui import QGuiApplication

import vimiv
from vimiv import api
from vimiv.config import styles
from vimiv.version import info, detailed_info


@api.commands.register()
def version(copy: bool = False) -> None:
    """Show a pop-up with version information.

    optional arguments:
        * ``copy``: Copy version information to clipboard instead.
    """
    if copy:
        copy_to_clipboard()
    else:
        VersionPopUp()


def copy_to_clipboard() -> None:
    """Copy version information to clipboard."""
    QGuiApplication.clipboard().setText(info())


class VersionPopUp(QDialog):
    """Pop up that displays version information on initialization.

    Class Attributes:
        TITLE: Window title used for the pop up.
        URL: Url to the vimiv website.
    """

    STYLESHEET = """
    QDialog {
        background: {image.bg};
    }
    QLabel {
        color: {statusbar.fg};
        font: {library.font}
    }
    QPushButton {
        font: {statusbar.font};
        background-color: {statusbar.bg};
        border: 0px;
        padding: 4px;
        color: {statusbar.fg};
    }
    QPushButton:pressed {
        background-color: {library.selected.bg};
    }
    """

    TITLE = f"{vimiv.__name__} - version"
    URL = "https://karlch.github.io/vimiv-qt/"

    def __init__(self):
        super().__init__()
        self._init_content()
        self.setWindowTitle(self.TITLE)
        styles.apply(self)
        self.exec_()

    def _init_content(self):
        """Initialize all widgets of the pop-up window."""
        layout = QVBoxLayout()
        layout.addWidget(QLabel(detailed_info()))
        layout.addWidget(
            QLabel("Website: <a href='{url}'>{url}</a>".format(url=self.URL))
        )
        button = QPushButton("&Copy version info to clipboard")
        button.clicked.connect(copy_to_clipboard)
        button.setFlat(True)
        layout.addWidget(button)
        self.setLayout(layout)
