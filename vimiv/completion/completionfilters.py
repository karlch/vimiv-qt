# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Filter classes for the completion widget."""

import string

from PyQt5.QtCore import QSortFilterProxyModel, QRegExp, Qt


class TextFilter(QSortFilterProxyModel):
    """Simple filter matching text in all columns."""

    def __init__(self):
        super().__init__()
        self.setFilterKeyColumn(-1)  # Also filter in descriptions

    def refilter(self, text: str) -> None:
        """Filter completions based on text in command line.

        Args:
            text: The current command line text.
        """
        text = self._strip_text(text)
        self.setFilterRegExp(QRegExp(text, Qt.CaseInsensitive))

    def reset(self) -> None:
        self.setFilterRegExp("")

    @staticmethod
    def _strip_text(text: str) -> str:
        """Strip text of characters ignored for filtering."""
        return (
            text.lstrip(":/")  # Remove trailing ":" or "/"
            .lstrip(string.digits)  # Do not filter on counts
            .replace("open ", "")  # Still allow match inside word for open
            .replace("set ", "")  # Still allow match inside word for set
        )


class FuzzyFilter(TextFilter):
    """Simple filter fuzzy matching text in all columns."""

    def refilter(self, text: str) -> None:
        """Fuzzy filter completions based on text in command line.

        Args:
            text: The current command line text.
        """
        text = ".*".join(self._strip_text(text))
        self.setFilterRegExp(QRegExp(text, Qt.CaseInsensitive))
