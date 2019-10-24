# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Pop-up window to display version information."""

from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton
from PyQt5.QtGui import QGuiApplication

import vimiv
from vimiv.widgets import PopUp


class VersionPopUp(PopUp):
    """Pop up that displays version information on initialization.

    Class Attributes:
        TITLE: Window title used for the pop up.
    """

    TITLE = f"{vimiv.__name__} - version"

    def __init__(self, parent=None):
        super().__init__(self.TITLE, parent=parent)
        self._init_content()
        self.show()

    def _init_content(self):
        """Initialize all widgets of the pop-up window."""
        layout = QVBoxLayout()
        layout.addWidget(QLabel(vimiv.version.detailed_info()))
        layout.addWidget(
            QLabel("Website: <a href='{url}'>{url}</a>".format(url=vimiv.__url__))
        )
        button = QPushButton("&Copy version info to clipboard")
        button.clicked.connect(self.copy_to_clipboard)
        button.setFlat(True)
        layout.addWidget(button)
        self.setLayout(layout)

    @staticmethod
    def copy_to_clipboard() -> None:
        """Copy version information to clipboard."""
        QGuiApplication.clipboard().setText(vimiv.version.info())
