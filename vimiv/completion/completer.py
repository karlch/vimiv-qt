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
        _proxy_model: The completion filter used.
    """

    @api.objreg.register
    def __init__(self, commandline, completion):
        super().__init__()

        self._proxy_model = None
        self._cmd = commandline
        self._completion = completion

        self._completion.activated.connect(self._complete)
        api.modes.COMMAND.first_entered.connect(self._init_models)
        self._cmd.textEdited.connect(self._on_text_changed)
        self._cmd.editingFinished.connect(self._on_editing_finished)

    @utils.slot
    def _init_models(self):
        completionmodels.init()

    def initialize(self, text: str):
        """Initialize completion when command mode was entered."""
        # Set model according to text, defaults are not possible as
        # :command accepts arbitrary text as argument
        self._update_proxy_model(text)
        # Show if the model is not empty
        self._maybe_show()
        self._completion.raise_()

    def reset(self):
        """Reset completion to empty model when leaving."""
        self._proxy_model = api.completion.get_module("", api.modes.current())

    @utils.slot
    def _on_text_changed(self, text: str):
        """Update completions when text changed."""
        # Clear selection
        self._completion.selectionModel().clear()
        # Update model
        self._update_proxy_model(text)
        self._proxy_model.sourceModel().on_text_changed(text)

    @utils.slot
    def _on_editing_finished(self):
        """Reset filter and hide completion widget."""
        self._completion.selectionModel().clear()
        self._proxy_model.reset()
        self._completion.hide()

    def _update_proxy_model(self, text: str):
        """Update completion proxy model depending on text.

        Args:
            text: Text in the commandline which defines the model.
        """
        proxy_model = api.completion.get_module(text, api.modes.COMMAND.last)
        if proxy_model != self._proxy_model:
            proxy_model.sourceModel().on_enter(text)
            self._proxy_model = proxy_model
            self._completion.setModel(proxy_model)
            self._completion.update_column_widths()
        self._proxy_model.refilter(text)

    def _maybe_show(self):
        """Show completion widget if the model is not empty."""
        if not isinstance(self._proxy_model.sourceModel(), completionmodels.Empty):
            self._completion.show()

    @utils.slot
    def _complete(self, text: str):
        """Set commandline text including unmatched part (e.g. count) on completion."""
        prefix, textpart = text[0], text[1:]
        self._cmd.setText(prefix + self._proxy_model.unmatched + textpart)
