# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Statusbar widget in the bar and functions to interact with it.

Module Attributes:
    _modules: Dictionary to store any modules for the statusbar. These modules
        are instances of the _Module class which essentially have a name in the
        form of {module} and a callable function that returns a parsed string
        for the statubar to show.
"""

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QLabel, QWidget, QStackedLayout

from vimiv.commands import runners
from vimiv.config import settings, styles
from vimiv.gui import widgets
from vimiv.utils import objreg


_modules = {}


class Module():
    """Class to store function of one statusbar module."""

    def __init__(self, func, instance=None):
        self._func = func
        self._instance = instance

    def __call__(self):
        if self._instance:
            return self._func(objreg.get(self._instance))
        return self._func()


def module(name, instance=None):
    """Decorator to register a command as a statusbar module.

    Args:
        name: Name of the module as set in the config file.
        instance: Name of the class in the objreg for methods or None.
    """
    def decorator(function):
        """Store function executable under module name."""
        _modules[name] = Module(function, instance)
        def inner(*args):
            """Run the function."""
            return function(*args)
        return inner
    return decorator


def evaluate_modules(text):
    """Evaluate module and update text accordingly.

    Replaces all occurances of module names with the output of the
    corresponding function.

    Example:
        A module called {pwd} is associated with the function os.pwd. Assuming
        the output of os.pwd() is "/home/foo/bar", the text 'Path: {pwd}'
        becomes 'Path: /home/foo/bar'.

    Args:
        text: The text to evaluate.
    Return:
        The updated text.
    """
    for name, mod in _modules.items():
        if name in text:
            text = text.replace(name, mod())
    return text


def update():
    """Update the statusbar.

    Clears any pushed messages and then re-evaluates the assigned modules.
    """
    bar = objreg.get("statusbar")
    bar.update()


class StatusBar(QWidget):
    """Statusbar widget to display permanent and temporary messages.

    Packs three labels for permanent messages ("left", "center", "right") and
    one for temporary ones ("message"). The three labels are grouped into one
    hbox. The hbox and the message label are both in a QStackedLayout to toggle
    between them.

    Attributes:
        timer: QTimer object to remove temporary messages after timeout.

        _items: Dictionary storing the widgets.
    """

    STYLESHEET = """
    QWidget,
    QWidget QLabel {
        font: {statusbar.font};
        background-color: {statusbar.bg};
        color: {statusbar.fg};
        padding: {statusbar.padding};
    }
    """

    @objreg.register("statusbar")
    def __init__(self):
        self._items = {}
        super().__init__()
        timeout = settings.get_value("statusbar.message_timeout")
        self.timer = QTimer()
        self.timer.setInterval(timeout)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.clear_message)

        self["stack"] = QStackedLayout(self)

        self["status"] = QWidget()
        labelbox = widgets.SimpleHBox(self["status"])
        self["left"] = QLabel()
        self["center"] = QLabel()
        self["center"].setAlignment(Qt.AlignCenter)
        self["right"] = QLabel()
        self["right"].setAlignment(Qt.AlignRight)
        labelbox.addWidget(self["left"])
        labelbox.addWidget(self["center"])
        labelbox.addWidget(self["right"])
        self["stack"].addWidget(self["status"])

        self["message"] = QLabel()
        self["stack"].addWidget(self["message"])
        self["stack"].setCurrentWidget(self["status"])

        styles.apply(self)

        runners.signals.exited.connect(self._on_cmd_exited)

    def update(self):
        """Update the statusbar."""
        mode = evaluate_modules("{mode}").lower()
        self.clear_message()
        for position in ["left", "center", "right"]:
            label = self[position]
            text = self._get_text(position, mode)
            label.setText(text)

    def message(self, text, severity="Info"):
        """Push a temporary message to the statusbar.

        Args:
            text: Text of the temporary message.
            severity: One of "Info", "Warning", "Error". Affects the style.
        """
        self._set_severity_style(severity.lower())
        self["message"].setText(text)
        self["stack"].setCurrentWidget(self["message"])
        self.timer.start()

    def clear_message(self):
        """Remove a temporary message from the statusbar."""
        if self.timer.isActive():
            self.timer.stop()
        self._clear_severity_style()
        self["message"].setText("")
        self["stack"].setCurrentWidget(self["status"])

    def _get_text(self, position, mode):
        """Get the text to put into one label depending on the current mode.

        Args:
            position: One of "left", "center", "right" defining the label.
            mode: Current mode.
        """
        try:  # Prefer mode specific setting
            text = settings.get_value(
                "statusbar.%s_%s" % (position, mode))
        except KeyError:
            text = settings.get_value("statusbar.%s" % (position))
        return evaluate_modules(text)

    def _on_cmd_exited(self, returncode, message):
        """Push message or update status when a command exited."""
        if returncode == 0:
            self.update()
        elif returncode == 42:
            self.message(message, "Warning")
        else:
            self.message(message, "Error")

    def _set_severity_style(self, severity):
        """Set the style of the statusbar for a temporary message.

        Adds a colored border to the top of the statusbar. The border color
        depends on the severity.

        Args:
            severity: One of "Info", "Warning", "Error".
        """
        append = """
        QLabel {
            border-top: {statusbar.message_border} {statusbar.%s};
        }
        """ % (severity)
        styles.apply(self, append)

    def _clear_severity_style(self):
        styles.apply(self)

    def __setitem__(self, name, item):
        self._items[name] = item

    def __getitem__(self, name):
        return self._items[name]
