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
from typing import cast, Dict, Iterable, Tuple, Optional

from PyQt5.QtCore import QSortFilterProxyModel, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from vimiv.utils import log
from . import modes, settings


_logger = log.module_logger(__name__)


def get_module(text: str, mode: modes.Mode) -> "BaseFilter":
    """Return the completion module which is valid for a given command line text.

    Args:
        text: The current command line text.
        mode: Mode for which the module should be valid.
    Returns:
        A completion model providing completion options.
    """
    best_match, best_match_size = cast(BaseFilter, None), -1
    for required_text, module in _modules.items():
        if mode in module.sourceModel().modes:
            match_size = len(required_text)
            if text.startswith(required_text) and len(required_text) > best_match_size:
                best_match, best_match_size = module, match_size
    _logger.debug("Model '%s' for text '%s'", best_match.sourceModel(), text)
    return best_match


class BaseFilter(QSortFilterProxyModel):
    """Base filter used for completion filters."""

    def __init__(self) -> None:
        super().__init__()
        self.setFilterKeyColumn(-1)  # Also filter in descriptions
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)

    def refilter(self, text: str) -> None:
        """Filter completions based on text in the command line.

        This updates the text according to the ``filtertext`` method and updates the
        filter regular expression.

        Args:
            text: The current command line text.
        """
        text = self.filtertext(text)
        if settings.completion.fuzzy.value:
            text = "*".join(text)
        self.setFilterWildcard(text)

    def reset(self) -> None:
        self.setFilterRegExp("")

    def filtertext(self, text: str) -> str:
        """Update text for filtering.

        This default implementation strips command line prefixes and leading digits. If
        the child class requires additional logic, it should override this method.

        Args:
            text: The current command line text.
        Returns:
            The updated text used as completion filter.
        """
        return text.lstrip(":/?" + string.digits)

    def sourceModel(self) -> "BaseModel":
        # We know we are only using the BaseFilter with BaseModel
        return cast(BaseModel, super().sourceModel())


class BaseModel(QStandardItemModel):
    """Base model used for completion models.

    Attributes:
        column_widths: Tuple of floats [0..1] defining the width of each column.
        modes: Modes for which this completion model is valid.
    """

    def __init__(
        self,
        text: str,
        text_filter: Optional[BaseFilter] = None,
        column_widths: Tuple[float, ...] = (1,),
        valid_modes: Tuple[modes.Mode, ...] = modes.ALL,
    ):
        """Initialize class and create completion module.

        Args:
            text: The text in the commandline for which this module is valid.
            text_filter: Filter class used to filter valid completions.
            column_widths: Width of each column shown in the completion widget.
            valid_modes: Modes for which this completion model is valid.
        """
        super().__init__()
        self.column_widths = column_widths
        self.modes = valid_modes
        # Register module using the filter
        text_filter = text_filter if text_filter is not None else BaseFilter()
        text_filter.setSourceModel(self)
        _modules[text] = text_filter

    def __str__(self) -> str:
        return self.__class__.__qualname__

    def on_enter(self, text: str) -> None:
        """Called by the completer when this model is entered.

        This allows models to change their content accordingly.

        Args:
            text: The current text in the comand line.
        """

    def on_text_changed(self, text: str) -> None:
        """Called by the completer when the commandline text has changed.

        This allows models to change their content accordingly.

        Args:
            text: The current text in the comand line.
        """

    def set_data(self, data: Iterable[Tuple]) -> None:
        """Add rows to the model.

        Args:
            data: List of tuples containing the data for each row.
        """
        for item in data:
            row = (
                QStandardItem(" " + elem if i == 0 else elem)
                for i, elem in enumerate(item)
            )
            self.appendRow(row)
        self.sort(0)  # Sort according to the actual text


_modules: Dict[str, BaseFilter] = {}
