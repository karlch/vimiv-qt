# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""*Utilities to work with completion modules*.

A completion module offers a model with options for command line completion and a filter
that decides which results are filtered depending on the text in the command line. All
completion models inherit from the :class:`BaseModel` class.

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

import re
from typing import cast, Dict, Iterable, Tuple

from PyQt5.QtCore import QSortFilterProxyModel, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from vimiv.utils import log
from . import modes, settings


_logger = log.module_logger(__name__)


def get_model(text: str, mode: modes.Mode) -> "BaseModel":
    """Return the completion model which is valid for a given command line text.

    Args:
        text: The current command line text.
        mode: Mode for which the module should be valid.
    Returns:
        A completion model providing completion options.
    """
    best_match, best_match_size = cast(BaseModel, None), -1
    for required_text, model in _models.items():
        if mode in model.modes:
            match_size = len(required_text)
            if text.startswith(required_text) and len(required_text) > best_match_size:
                best_match, best_match_size = model, match_size
    _logger.debug("Model '%s' for text '%s'", best_match, text)
    return best_match


class FilterProxyModel(QSortFilterProxyModel):
    """Proxy model to filter completions from a model using a regular expression.

    Class Attributes:
        FILTER_RE: Regular expression used to separate prefix, unmatched and command.
            The command and prefix are used for matching, the unmatched part is ignored
            and includes additional whitespace and the count.

    Attributes:
        unmatched: Unmatched part of the commandline text to insert when accepting a
            completion.
        _empty: Empty completion model used as fallback.
    """

    FILTER_RE = re.compile(r"(.)( *\d* *)(.*)")

    def __init__(self) -> None:
        super().__init__()
        self.setFilterKeyColumn(-1)  # Also filter in descriptions
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.unmatched = ""
        self._empty = BaseModel("")

    def refilter(self, text: str) -> None:
        """Filter completions based on text in the command line.

        The regular expression used for filtering:
        * Matches prefix
        * Ignores whitespace between prefix and the command
        * Ignores count between prefix and command

        For usual completion:
        * Matches all words of the command before the last one exactly
        * Matches inside the last word of the command

        For fuzzy completion:
        * Matches all characters in the command

        Args:
            text: The current command line text.
        """
        match = self.FILTER_RE.match(text)
        if match is None:  # Only happens when there is no prefix
            self.reset()
            return
        prefix, self.unmatched, command = match.groups()
        if settings.completion.fuzzy.value:
            self._set_fuzzy_completion_regex(prefix, command)
        else:
            self._set_completion_regex(prefix, command)

    def _set_completion_regex(self, prefix: str, command: str) -> None:
        """Set regular expression for filtering completions.

        Prefix and all words except for the last one in the command are matched exactly.
        The last word in the command must only be matched inside.

        Args:
            prefix: Current command line prefix character.
            command: Current command text in the command line.
        """
        parts = command.split()
        if len(parts) > 1:
            prefix = prefix + " ".join(parts[:-1])
            command = parts[-1]
        regex = prefix + f" *.*{command}.*"
        self.setFilterRegExp(regex)

    def _set_fuzzy_completion_regex(self, prefix: str, command: str) -> None:
        self.setFilterRegExp(".*".join(prefix + command))

    def reset(self) -> None:
        """Reset regular expression, unmatched string and source model."""
        self.setFilterRegExp("")
        self.unmatched = ""
        self.setSourceModel(self._empty)

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
        column_widths: Tuple[float, ...] = (1,),
        valid_modes: Tuple[modes.Mode, ...] = modes.ALL,
    ):
        """Initialize class and create completion module.

        Args:
            text: The text in the commandline for which this module is valid.
            column_widths: Width of each column shown in the completion widget.
            valid_modes: Modes for which this completion model is valid.
        """
        super().__init__()
        self.column_widths = column_widths
        self.modes = valid_modes
        _models[text] = self

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
        self.clear()
        for item in data:
            row = (
                QStandardItem(" " + elem if i == 0 else elem)
                for i, elem in enumerate(item)
            )
            self.appendRow(row)
        self.sort(0)  # Sort according to the actual text


_models: Dict[str, BaseModel] = {}
