# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Completer class as man-in-the-middle between command line and completion."""

from PyQt5.QtCore import QObject

from vimiv import api, utils
from vimiv.completion import completionmodels


class Completer(QObject):
    """Handle interaction between command line and completion.

    The commandline is stored as attribute, the completion widget is the parent
    class. Models are all created and dealt with depending on text in the
    command line.

    Attributes:
        _cmd: CommandLine object.
        _completion: CompletionWidget object.
    """

    @api.objreg.register
    def __init__(self, commandline, completion):
        super().__init__()

        self._cmd = commandline
        self._completion = completion

        self._completion.activated.connect(self._complete)
        api.modes.COMMAND.first_entered.connect(self._init_models)
        self._cmd.textEdited.connect(self._on_text_changed)
        self._cmd.editingFinished.connect(self._on_editing_finished)

    @property
    def proxy_model(self) -> api.completion.FilterProxyModel:
        return self._completion.model()

    @property
    def model(self) -> api.completion.BaseModel:
        return self.proxy_model.sourceModel()

    @property
    def has_completions(self) -> bool:
        return self.proxy_model.rowCount() > 0

    @utils.slot
    def _init_models(self):
        completionmodels.init()

    def initialize(self, text: str):
        """Initialize completion when command mode was entered."""
        # Set model according to text, defaults are not possible as
        # :command accepts arbitrary text as argument
        self._update_proxy_model(text)
        self._show_unless_empty()

    @utils.slot
    def _on_text_changed(self, text: str):
        """Update completions when text changed."""
        # Clear selection
        self._completion.selectionModel().clear()
        # Update model
        self._update_proxy_model(text)
        self.model.on_text_changed(text)
        self._show_unless_empty()

    @utils.slot
    def _on_editing_finished(self):
        """Reset filter and hide completion widget."""
        self._completion.selectionModel().clear()
        self.proxy_model.reset()
        self._completion.hide()

    def _update_proxy_model(self, text: str):
        """Update completion proxy model depending on text.

        Args:
            text: Text in the commandline which defines the model.
        """
        model = api.completion.get_model(text, api.modes.COMMAND.last)
        if model != self.model:
            model.on_enter(text)
            self.proxy_model.setSourceModel(model)
            self._completion.update_column_widths()
        self.proxy_model.refilter(text)

    @utils.slot
    def _complete(self, text: str):
        """Set commandline text including unmatched part (e.g. count) on completion."""
        prefix, textpart = text[0], text[1:]
        self._cmd.setText(prefix + self.proxy_model.unmatched + textpart)

    def _show_unless_empty(self):
        """Show completion widget if there are completions, hide it otherwise."""
        if not self.has_completions:
            self._completion.hide()
        elif not self._completion.isVisible():
            self._completion.show()
            self._completion.raise_()
