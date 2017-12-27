# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Filter classes for the completion widget."""

import string

from PyQt5.QtCore import QSortFilterProxyModel, QRegExp, Qt


class TextFilter(QSortFilterProxyModel):
    """Simple filter matching text in all columns."""

    def __init__(self):
        super().__init__()
        self.setFilterKeyColumn(-1)  # Also filter in descriptions

    def refilter(self, text):
        """Filter completions based on text in command line.

        Args:
            text: The current command line text.
        """
        # Remove trailing ":" or "/"
        text = text.lstrip(":/")
        # Do not filter on counts
        text = text.lstrip(string.digits)
        # Still allow match inside word for open
        text = text.replace("open ", "")
        # Still allow match inside word for set
        text = text.replace("set ", "")
        regex = QRegExp(text, Qt.CaseInsensitive)
        self.setFilterRegExp(regex)

    def reset(self):
        self.setFilterRegExp("")
