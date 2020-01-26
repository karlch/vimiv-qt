# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Prompt the user for a question."""

import typing

from PyQt5.QtCore import QObject, pyqtSignal

from vimiv.utils import log


_logger = log.module_logger(__name__)


class Question:
    """Storage class for a question to the user.

    Attributes:
        title: Title of the question.
        body: Sentence body representing the actual question.
        answer: Answer given by the user if any.
    """

    def __init__(self, *, title: str, body: str):
        self.title = title
        self.body = body
        self.answer = None

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(title={self.title}, body={self.body})"


class _Bridge(QObject):
    """Message bridge using the signal-slot infrastructure.

    Signals:
        question_asked: Emitted when a question to the user was asked.
            arg1: The Question instance storing all information on the question.
    """

    question_asked = pyqtSignal(Question)


def ask_question(*, title: str, body: str) -> typing.Any:
    """Prompt the user to answer a question.

    This emits the question_asked signal which leads to a gui prompt being displayed.
    The UI is blocked until the question was answered or aborted.

    Args:
        title: Title of the question.
        body: Sentence body representing the actual question.
    Returns:
        answer: Answer given by the user if any.
    """
    question = Question(title=title, body=body)
    _logger.debug("Asking question '%s'", question.title)
    question_asked.emit(question)  # Enters a gui prompt widget
    _logger.debug("Answered '%s' with '%s'", question.title, question.answer)
    return question.answer


# Expose only signals from the bridge
_bridge = _Bridge()
question_asked = _bridge.question_asked
