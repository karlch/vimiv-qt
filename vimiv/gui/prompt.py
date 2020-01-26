# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Blocking prompt widget asking the user a question."""

from PyQt5.QtCore import Qt, QEventLoop
from PyQt5.QtWidgets import QLabel

from vimiv import api, utils
from vimiv.config import styles


_logger = utils.log.module_logger(__name__)


class Prompt(QLabel):
    """Blocking prompt widget asking the user a question.

    The prompt is initialized with a question and displays the question, its title and
    the valid keybindings. Calling ``run`` blocks the UI until a valid keybinding to
    answer/abort the question was given.

    Class Attributes:
        BINDINGS: Valid keybindings to answer/abort the question.

    Attributes:
        question: Question object defining title, question and answer.
        loop: Event loop used to block the UI.
    """

    STYLESHEET = """
    QLabel {
        font: {prompt.font};
        color: {prompt.fg};
        background-color: {prompt.bg};
        padding: {prompt.padding};
        border-top-right-radius: {prompt.border_radius};
        border-top: {prompt.border} {prompt.border.color};
        border-right: {prompt.border} {prompt.border.color};
    }
    """

    BINDINGS = (
        ("y", "Yes"),
        ("n", "No"),
        ("<return>", "No"),
        ("<escape>", "Abort"),
    )

    def __init__(self, question: api.prompt.Question, *, parent):
        super().__init__(parent=parent)
        self.question = question
        self.loop = QEventLoop()

        styles.apply(self)
        header = f"<h3>{question.title}</h3>{question.body}"
        self.setText(header + self.bindings_table())
        _logger.debug("Initialized %s", self)

        self.setFocus()
        self.adjustSize()
        self.raise_()
        self.show()

    def __str__(self):
        return f"prompt for '{self.question.title}'"

    @classmethod
    def bindings_table(cls):
        """Return a formatted html table with the valid keybindings."""
        bindings = "".join(
            "<tr>"
            f"<td><b>{utils.escape_html(binding)}</b></td>"
            f"<td style='padding-left: 2ex'>{command}</td>"
            "</tr>"
            for binding, command in cls.BINDINGS
        )
        return f"<table>{bindings}</table>"

    def run(self):
        """Run the blocking event loop."""
        _logger.debug("Running blocking %s", self)
        self.loop.exec_()

    def update_geometry(self, _width: int, bottom: int):
        y = bottom - self.height()
        self.setGeometry(0, y, self.width(), self.height())

    def leave(self, *, answer=None):
        """Leave the prompt by answering the question and quitting the loop."""
        _logger.debug("Leaving %s with '%s'", self, answer)
        self.question.answer = answer
        self.loop.quit()
        self.loop.deleteLater()
        self.deleteLater()
        api.modes.current().widget.setFocus()

    def keyPressEvent(self, event):
        """Leave the prompt on a valid key binding."""
        if event.key() == Qt.Key_Y:
            self.leave(answer=True)
        elif event.key() in (Qt.Key_N, Qt.Key_Return):
            self.leave(answer=False)
        elif event.key() == Qt.Key_Escape:
            self.leave()

    def focusOutEvent(self, event):
        """Leave the prompt without answering when unfocused."""
        if self.loop.isRunning():
            self.leave()
        super().focusOutEvent(event)
