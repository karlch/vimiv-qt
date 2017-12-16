# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Functions dealing with the stylesheet of the Qt widgets.

Module Attributes:
    _styles: Dictionary saving the style settings from the config file, form:
        _styles["image.bg"] = "#000000"
"""


_styles = {}


def store(configsection):
    """Store all styles defined in the STYLES section of the config file."""
    for name, value in configsection.items():
        _styles["{%s}" % (name)] = value


def replace_referenced_variables():
    """Replace referenced variables with the stored value."""
    for name, value in _styles.items():
        if value in _styles.keys():
            _styles[name] = _styles[value]


def apply(obj, append=""):
    """Apply stylesheet to an object dereferencing config options.

    Args:
        obj: The QObject to apply the stylesheet to.
        append: Extra string to append to the stylesheet.
    """
    sheet = obj.STYLESHEET + append
    for name, value in _styles.items():
        sheet = sheet.replace(name, value)
    obj.setStyleSheet(sheet)


def get(name):
    return _styles["{%s}" % (name)]
