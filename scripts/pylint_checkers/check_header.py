# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

"""Checker to ensure each python file includes a modeline and no copyright notice."""

from pylint.interfaces import IRawChecker
from pylint.checkers import BaseChecker


class FileHeaderChecker(BaseChecker):
    """Checker to ensure each python file includes a modeline and copyright notice."""

    __implements__ = IRawChecker

    name = "file-header"
    name_modeline_missing = "modeline-missing"
    name_copyright_included = "copyright-included"

    msgs = {
        "E9501": (
            "Vim modeline is missing",
            name_modeline_missing,
            "All files should include a valid vim modeline.",
        ),
        "E9502": (
            "Copyright included",
            name_copyright_included,
            "There should be no copyright at the top of the file.",
        ),
    }
    options = ()

    priority = -1

    MODELINE = "# vim: ft=python fileencoding=utf-8 sw=4 et sts=4"

    def process_module(self, node):
        """Read the module content as string and check for the necessary content."""

        with node.stream() as stream:
            content = stream.read().decode("utf-8")

        lines = content.split("\n")

        if self.MODELINE not in lines:
            self.add_message(self.name_modeline_missing, line=1)

        if any(line.lower().startswith("# copyright") for line in lines):
            self.add_message(self.name_copyright_included, line=1)


def register(linter):
    """Register the defined checkers automatically."""
    linter.register_checker(FileHeaderChecker(linter))
