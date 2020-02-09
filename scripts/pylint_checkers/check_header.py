# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Checker to ensure each python file includes a modeline and copyright notice."""

from pylint.interfaces import IRawChecker
from pylint.checkers import BaseChecker


class FileHeaderChecker(BaseChecker):
    """Checker to ensure each python file includes a modeline and copyright notice."""

    __implements__ = IRawChecker

    name = "file-header"
    name_modeline_missing = "modeline-missing"
    name_copyright_missing = "copyright-missing"

    msgs = {
        "E9501": (
            "Vim modeline is missing",
            name_modeline_missing,
            "All files should include a valid vim modeline.",
        ),
        "E9502": (
            "Copyright is missing",
            name_copyright_missing,
            "All files should include a valid copyright notice.",
        ),
    }
    options = ()

    priority = -1

    MODELINE = "# vim: ft=python fileencoding=utf-8 sw=4 et sts=4"
    COPYRIGHT = (
        "# This file is part of vimiv.\n"
        "# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>\n"
        '# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.\n'
    )

    def process_module(self, node):
        """Read the module content as string and check for the necessary content."""

        with node.stream() as stream:
            content = stream.read().decode("utf-8")

        if self.MODELINE not in content.split("\n"):
            self.add_message(self.name_modeline_missing, line=1)

        if self.COPYRIGHT not in content:
            self.add_message(self.name_copyright_missing, line=1)


def register(linter):
    """Register the defined checkers automatically."""
    linter.register_checker(FileHeaderChecker(linter))
