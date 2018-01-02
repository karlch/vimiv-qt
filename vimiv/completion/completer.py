# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Completer class as man-in-the-middle between command line and completion."""

from PyQt5.QtCore import QObject, pyqtSlot

from vimiv.completion import completionfilters, completionmodels
from vimiv.utils import objreg


class Completer(QObject):
    """Handle interaction between command line and completion.

    The commandline is stored as attribute, the completion widget is the parent
    class. Models are all created and dealt with depending on text in the
    command line.

    Attributes:
        proxy_model: completionfilters.TextFilter.

        _cmd: CommandLine object.
        _modelfunc: Current model function to avoid duplicate model setting.
        _modelargs: Current arguments for model function to avoid duplicate
            model setting.
        _mode: Mode before entering command line for commands.
    """

    @objreg.register("completer")
    def __init__(self, commandline, completion):
        super().__init__(parent=completion)
        self._cmd = objreg.get("command")
        self.proxy_model = completionfilters.TextFilter()
        self._modelfunc = None
        self._modelargs = None
        self._mode = "image"

        self.parent().setModel(self.proxy_model)

        self.parent().activated.connect(self._on_completion)
        self._cmd.entered.connect(self._on_commandline_entered)
        self._cmd.textEdited.connect(self._on_text_changed)
        self._cmd.editingFinished.connect(self._on_editing_finished)

    @pyqtSlot(str)
    def _on_commandline_entered(self, mode):
        """Initialize completion model and show completion widget.

        Args:
            mode: Mode from which the command line was entered for commands.
        """
        self._mode = mode
        # Set model according to text, defaults are not possible as :command
        # accepts arbitrary text as argument
        self._maybe_update_model(self._cmd.text())
        self.parent().show()
        self.parent().raise_()

    @pyqtSlot(str)
    def _on_text_changed(self, text):
        """Update completions when text changed."""
        # Clear selection
        self.parent().selectionModel().clear()
        # Update model
        self._maybe_update_model(text)
        # Refilter
        self.proxy_model.refilter(text)

    @pyqtSlot()
    def _on_editing_finished(self):
        """Reset filter and hide completion widget."""
        self.proxy_model.reset()
        self.parent().hide()

    def _maybe_update_model(self, text):
        """Update model depending on text."""
        modelfunc, args = self._get_modelfunc(text)
        if modelfunc != self._modelfunc or args != self._modelargs:
            self._set_model(modelfunc, *args)

    def _get_modelfunc(self, text):
        """Return the needed model function depending on text."""
        text = text.lstrip(":").lstrip()
        # Path completion
        if text.startswith("open"):
            return completionmodels.paths, (text.lstrip("open").lstrip(),)
        # Setting completion
        elif text.startswith("set"):
            setting = text.lstrip("set").lstrip().split()
            if setting:
                return completionmodels.settings, (setting[0],)
            return completionmodels.settings, ("",)
        elif text.startswith("!"):
            return completionmodels.external, ()
        # Default: command completion
        return completionmodels.command, (self._mode,)

    def _set_model(self, modelfunc, *args):
        """Set the source model of the proxy model.

        Args:
            modelfunc: Function which returns the model to set.
            args: List of arguments to pass to modelfunc.
        """
        self._modelfunc = modelfunc
        self._modelargs = args
        self.proxy_model.setSourceModel(modelfunc(*args))

    @pyqtSlot(str)
    def _on_completion(self, text):
        """Set commandline text when completion was activated.

        Args:
            text: Suggested text from completion.
        """
        # Get prefix and prepended digits
        cmdtext = self._cmd.text()
        prefix, cmdtext = cmdtext[0], cmdtext[1:]
        digits = ""
        if cmdtext:
            while cmdtext[0].isdigit():
                digits += cmdtext[0]
                cmdtext = cmdtext[1:]
        # Set text in commandline
        self._cmd.setText(prefix + digits + text)
