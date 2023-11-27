# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

"""Additional docstring checkers."""

import re
from typing import Set

import astroid

from pylint.checkers import BaseChecker


class CommandMissingDocumentation(BaseChecker):
    """Checker to ensure command docstrings include all information for docs."""

    name = "command-docstring"

    name_ambiguous = "ambiguous-register"
    name_missing = "docstr-missing"
    name_syntax = "command-bad-syntax"
    name_count = "command-bad-count"
    name_argument_missing = "command-arg-missing-doc"
    name_argument_bad = "command-arg-bad-doc"

    msgs = {
        "E9001": (
            "Command '%s' bad syntax section",
            name_syntax,
            "All commands with args must define a section in the form of '**syntax:**'",
        ),
        "E9002": (
            "Command '%s' bad count section",
            name_count,
            "All commands with count must define a section in the form of '**count:**'",
        ),
        "E9003": (
            "Command '%s' argument '%s' undocmented",
            name_argument_missing,
            "All command arguments should be documented in the "
            "**posional/optional** arguments section**",
        ),
        "E9004": (
            "Command '%s' argument '%s' bad doc format",
            name_argument_bad,
            "All command arguments should be documented in the "
            "**posional/optional** arguments section**",
        ),
        "E9005": (
            "Command '%s' missing docstring",
            name_missing,
            "All commands must have a docstring for documentation",
        ),
        "W9001": (
            "Ambiguous register decorator, use module.register instead",
            name_ambiguous,
            "register decorators should be prepended with the module for clarity",
        ),
    }

    priority = -1

    def visit_functiondef(self, node):
        """Run the checks on all function definitions that are commands."""
        if not self._is_command(node):
            return
        argnames = {arg.name.replace("_", "-") for arg in node.args.args}
        regular_argnames = argnames - {"self", "count"}
        docstr = node.doc_node.value
        self._check_args_section(node, docstr, regular_argnames)
        self._check_count_section(node, docstr, argnames)
        self._check_syntax_section(node, docstr, regular_argnames)

    @staticmethod
    def sections(docstr):
        """Retrieve list of all sections separated by an empty line in docstr."""
        sections = []
        content = ""
        for line in docstr.split("\n"):
            if not line.strip():
                sections.append(content)
                content = ""
            else:
                content += line
        return sections

    def _check_syntax_section(self, node, docstr, argnames):
        """Check if a syntax section is available for commands with arguments."""
        if not argnames:
            return
        for section in self.sections(docstr):
            if re.match(r"\*\*syntax:\*\* ``.*``", section.strip()):
                return
        self.add_message(self.name_syntax, node=node, args=(node.name,))

    def _check_count_section(self, node, docstr, argnames):
        """Check if a count section is available for commands that support count."""
        if "count" not in argnames:
            return
        if "**count:**" not in docstr:
            self.add_message(self.name_count, node=node, args=(node.name,))

    def _check_args_section(self, node, docstr, argnames):
        """Check if all command arguments are documented."""
        docstring_argnames = self._get_args_from_docstring(node, docstr)
        difference = argnames - docstring_argnames
        for argname in difference:
            self.add_message(
                self.name_argument_missing, node=node, args=(node.name, argname)
            )

    def _is_command(self, node) -> bool:
        """Check if a function definition node is a command.

        This checks if the function was decorated by @commands.register.
        """
        decorators = node.decorators
        if decorators is None:
            return False
        for decorator in decorators.nodes:
            # @register
            if isinstance(decorator, astroid.node_classes.Name):
                if decorator.name == "register":
                    self.add_message(self.name_ambiguous, node=node)
                continue
            # @module.register, cannot be command as it needs arguments
            if isinstance(decorator, astroid.node_classes.Attribute):
                continue
            # @register()
            if isinstance(decorator.func, astroid.node_classes.Name):
                if decorator.func.name == "register":
                    self.add_message(self.name_ambiguous, node=node)
                continue
            # @module.register()
            if isinstance(decorator.func.expr, astroid.node_classes.Name):
                if decorator.func.expr.name == "commands":
                    return True
                return False
            # @api.module.register()
            if (
                decorator.func.attrname == "register"
                and decorator.func.expr.attrname == "commands"
            ):
                return True
        return False

    def _get_args_from_docstring(self, node, docstr) -> Set[str]:
        """Retrieve documented arguments from command docstring.

        If an argument is not correctly formatted in the documentation section, the
        name_argument_bad message is added.

        Returns:
            Set of all documented argument names.
        """
        if docstr is None:
            self.add_message(self.name_missing, node=node, args=(node.name,))
            return set()
        lines = [line.strip() for line in docstr.split("\n")]

        def _get_args(identifier, pattern):
            try:
                index = lines.index(identifier)
            except ValueError:
                return set()
            args = []
            for line in lines[index:]:
                if not line:  # Section separated
                    break
                if line.startswith("* "):  # Argument list
                    argument = line.split()[1]
                    argname = argument.strip("-:`")
                    if not re.match(pattern, argument):
                        self.add_message(
                            self.name_argument_bad, node=node, args=(node.name, argname)
                        )
                    args.append(argname)
            return set(args)

        positional_args = _get_args(
            "positional arguments:", "``[a-zA-Z][a-zA-Z0-9-]*``:"
        )
        optional_args = _get_args("optional arguments:", "``--[a-zA-Z][a-zA-Z0-9-]*``:")
        return positional_args | optional_args


def register(linter):
    """Register the defined checkers automatically."""
    linter.register_checker(CommandMissingDocumentation(linter))
