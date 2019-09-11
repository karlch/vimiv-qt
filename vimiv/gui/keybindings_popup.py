# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Pop-up window to display keybindings of current mode."""

from typing import List, Tuple, Iterator

from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QLayout, QLineEdit

import vimiv
from vimiv import api, utils
from vimiv.config import styles
from vimiv.widgets import PopUp


_logger = utils.log.module_logger(__name__)


class KeybindingsPopUp(PopUp):
    """Pop up that displays keybinding information.

    All available keybindings are displayed with the corresponding command. It is
    possible to search through the commands using the line edit.

    Class Attributes:
        TITLE: Window title used for the pop up.

    Attributes:
        _bindings_color: Color used to highlight the keybindings.
        _highlight_color: Color used to highlight matching search results.
        _labels: List of labels to display keybinding-command text per column.
        _search: Line edit widget to search for commands.
    """

    TITLE = f"{vimiv.__name__} - keybindings"

    # fmt: off
    STYLESHEET = PopUp.STYLESHEET + """
    QLineEdit {
        font: {statusbar.font};
        background-color: {statusbar.bg};
        color: {statusbar.fg};
        border: 0px solid;
        padding: {statusbar.padding};
    }
    """
    # fmt: on

    def __init__(self, columns: int = 2, parent=None):
        super().__init__(self.TITLE, parent=parent)

        self._bindings_color = styles.get("keybindings.bindings.color")
        self._highlight_color = styles.get("keybindings.highlight.color")
        self._labels: List[QLabel] = []
        self._search = QLineEdit()

        self._search.setPlaceholderText("search")

        layout = QVBoxLayout()
        layout.setSizeConstraint(QLayout.SetFixedSize)
        content_layout = QHBoxLayout()
        for _ in range(columns):
            label = QLabel()
            self._labels.append(label)
            content_layout.addWidget(label)
        layout.addLayout(content_layout)
        layout.addWidget(self._search)
        self.setLayout(layout)

        self._search.textChanged.connect(self._update_text)
        for mode in api.modes.ALL:
            mode.entered.connect(self._update_text)

        self._update_text()
        self._search.setFocus()
        self.show()

    @property
    def text(self) -> str:
        """Complete keybinding/command text displayed in all columns."""
        return "\n".join(label.text() for label in self._labels)

    @property
    def column_count(self) -> int:
        """Number of columns to split the bindings in."""
        return len(self._labels)

    def column_bindings(self) -> Iterator[List[Tuple[str, str]]]:
        """Return html-safe keybindings for each column sorted by command name."""
        bindings = api.keybindings.get(api.modes.current())
        formatted_bindings = [
            (utils.escape_html(binding), command)
            for binding, command in sorted(bindings.items(), key=lambda x: x[1])
        ]
        return utils.split(formatted_bindings, self.column_count)

    def column_text(
        self, search: str, highlight: str, bindings: List[Tuple[str, str]]
    ) -> str:
        """Return the formatted keybinding-command text for one column.

        Args:
            search: Current search string.
            highlight: Search string wrapped in a highlight color span.
            bindings: List of bindings to put into this column
        """
        text = ""
        for binding, command in bindings:
            if search:
                command = command.replace(search, highlight)
            text += (
                "<tr>"
                f"<td style='color: {self._bindings_color}'>{binding}</td>"
                f"<td style='padding-left: 2ex'>{command}</td>"
                "</tr>"
            )
        return text

    def highlighted_search_str(self, search: str) -> str:
        """Current search string wrapped in a highlight color span."""
        return utils.wrap_style_span(f"color: {self._highlight_color}", search)

    def _update_text(self, search: str = None) -> None:
        """Update keybinding-command text for all columns.

        This retrieves all keybindings for the current mode, splits them upon the
        available columns and formats them neatly. If there is a search, then the
        matching command parts are highlighted.

        Args:
            search: Current search string from the line edit.
        """
        search = search if search is not None else self._search.text()
        search = search.strip()
        highlight = self.highlighted_search_str(search)

        for label, bindings in zip(self._labels, self.column_bindings()):
            label.setText(self.column_text(search, highlight, bindings))
