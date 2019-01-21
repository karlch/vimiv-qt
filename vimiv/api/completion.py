# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""*Utilities to work with completion modules*.

A completion module offers a model with options for command line completion and a filter
that decides which results are filtered depending on the text in the command line. All
completion models inherit from the :class:`BaseModel` class while the filters inherit
from :class:`BaseFilter`.

A completion module must define for which command line text it is valid. In addition, it
can provide a custom filter as well as custom column widths for the results shown. By
default there is only a single column which gets the complete width. Let's start with a
simple example::

    from vimiv.api import completion

    class UselessModel(completion.BaseModel):

        def __init__(self):
            super().__init__(":useless")  # Gets triggered when the command line text
                                          # starts with ":useless"
            data = [("useless %d" % (i),) for i in range(3)]
            self.set_data(data)

The model defined offers the completions "useless 0", "useless 1" and "useless 2" if the
command line text starts with ":useless".

Note:
    The data which was set is a sequence of tuples. The tuples are required as it is
    possible to have multiple columns in the completion widget.

To include additional information on the provided completion, further columns can be
added::

    class UselessModel(completion.BaseModel):

        def __init__(self):
            super().__init__(":useless", column_widths=(0.7, 0.3))
            data = [("useless %d" % (i), "Integer") for i in range(3)]
            self.set_data(data)

The offered completions now provide and additional description (which is always
"Integer") that is shown in a second column next to the actual completion. The
description column is set up to take 30 % of the total width while the completion takes
70 %.

For an overview of implemented models, feel free to take a look at the ones defined in
``vimiv.completion.completionmodels``.
"""

import string
from typing import cast, Dict, NamedTuple, Sequence, Tuple

from PyQt5.QtCore import QSortFilterProxyModel, QRegExp, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from . import modes


def get_module(text: str) -> "CompletionModule":
    """Return the completion module which is valid for a given command line text.

    Args:
        text: The current command line text.
    Returns:
        A completion model providing completion options.
    """
    best_match, best_match_size = cast(CompletionModule, None), -1
    for required_text, module in _modules.items():
        match_size = len(required_text)
        if text.startswith(required_text) and len(required_text) > best_match_size:
            best_match, best_match_size = module, match_size
    return best_match


class BaseFilter(QSortFilterProxyModel):
    """Base filter used for completion filters."""

    def __init__(self):  # type: ignore
        super().__init__()
        self.setFilterKeyColumn(-1)  # Also filter in descriptions

    def refilter(self, text: str) -> None:
        """Filter completions based on text in the command line.

        Must be implemented by the child classes.

        Args:
            text: The current command line text.
        """
        raise NotImplementedError(
            "BaseFilter.refilter must be implemented by child class"
        )

    def reset(self) -> None:
        self.setFilterRegExp("")

    def strip_text(self, text: str) -> str:
        """Strip text of characters ignored for filtering.

        This default implementation strips command line prefixes and leading digits. If
        the child class requires additional intelligence it should override this
        method.

        Args:
            text: The current command line text.
        Return:
            The stripped text used as completion filter.
        """
        return text.lstrip(":/").lstrip(  # Remove trailing ":" or "/"
            string.digits
        )  # Do not filter on counts


class TextFilter(BaseFilter):
    """Simple filter matching text in all columns."""

    def refilter(self, text: str) -> None:
        """Filter completions based on text in command line.

        Args:
            text: The current command line text.
        """
        text = self.strip_text(text)
        self.setFilterRegExp(QRegExp(text, Qt.CaseInsensitive))

    def reset(self) -> None:
        self.setFilterRegExp("")

    # def strip_text(self, text: str) -> str:
    #     """Strip text of characters ignored for filtering."""
    #     return (
    #         super().strip_text(text)
    #         .replace("open ", "")  # Still allow match inside word for open
    #         .replace("set ", "")  # Still allow match inside word for set
    #     )


class FuzzyFilter(TextFilter):
    """Simple filter fuzzy matching text in all columns."""

    def refilter(self, text: str) -> None:
        """Fuzzy filter completions based on text in command line.

        Args:
            text: The current command line text.
        """
        text = ".*".join(self._strip_text(text))
        self.setFilterRegExp(QRegExp(text, Qt.CaseInsensitive))


class BaseModel(QStandardItemModel):
    """Base model used for completion models.

    Attributes:
        column_widths: Tuple of floats [0..1] defining the width of each column.
        text_filter: Filter class used to filter valid completions.
    """

    def __init__(
        self,
        text: str,
        text_filter: BaseFilter = TextFilter(),
        column_widths: Tuple[float, ...] = (1,),
    ):
        """Initialize class and create completion module.

        Args:
            text: The text in the commandline for which this module is valid.
            text_filter: Filter class used to filter valid completions.
            column_widths: Width of each column shown in the completion widget.
        """
        super().__init__()
        self.column_widths = column_widths
        self.text_filter = text_filter
        _modules[text] = CompletionModule(self, text_filter)  # Register module

    def on_enter(self, text: str, mode: modes.Mode) -> None:
        """Called by the completer when the commandline is entered.

        This allows models to change their content accordingly.

        Args:
            text: The current text in the comand line.
            mode: Mode from which the commandline was entered.
        """

    def on_text_changed(self, text: str) -> None:
        """Called by the completer when the commandline text has changed.

        This allows models to change their content accordingly.

        Args:
            text: The current text in the comand line.
        """

    def set_data(self, data: Sequence[Tuple]) -> None:
        """Add rows to the model.

        Args:
            data: List of tuples containing the data for each row.
        """
        for item in data:
            row = [QStandardItem(elem) for elem in item]
            self.appendRow(row)
        self.sort(0)  # Sort according to the actual text


class CompletionModule(NamedTuple):
    Model: BaseModel
    Filter: BaseFilter


_modules: Dict[str, CompletionModule] = {}
