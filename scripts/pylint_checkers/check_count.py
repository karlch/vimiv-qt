# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Checkers to ensure count is treated correctly."""

import astroid

from pylint.interfaces import IAstroidChecker
from pylint.checkers import BaseChecker


class CountComparedWithoutNone(BaseChecker):
    """Checker to ensure count is compared to None."""

    __implements__ = IAstroidChecker

    name = "count-compared-directly"

    # here we define our messages
    msgs = {
        "E8001": (
            "Count compared without None",
            name,
            "Count should always be compared with None as zero is a valid count.",
        )
    }
    options = ()

    priority = -1

    def visit_if(self, node):
        self._check_compare_count(node)

    def visit_ifexp(self, node):
        self._check_compare_count(node)

    def _check_compare_count(self, node):
        """Check if count is compared to directly instead of comparing to None."""
        if isinstance(node.test, astroid.node_classes.Name):
            if node.test.name == "count":
                self.add_message(self.name, node=node)


class CountAssignedToZero(BaseChecker):
    """Checker to inform when default assigning count to zero."""

    __implements__ = IAstroidChecker

    name = "count-default-zero"

    # here we define our messages
    msgs = {
        "I8002": (
            "Count default assigned to zero",
            name,
            "Count default should always be assigned to None as zero is a valid count.",
        )
    }
    options = ()

    priority = -1

    def visit_functiondef(self, node):
        """Check if count is default assigned to zero in function definition.

        In almost all cases None is what we want instead.
        """
        for name, default in zip(node.args.args[::-1], node.args.defaults[::-1]):
            if name.name == "count" and default.value == 0:
                self.add_message(self.name, node=node)


def register(linter):
    """Register the defined checkers automatically."""
    linter.register_checker(CountComparedWithoutNone(linter))
    linter.register_checker(CountAssignedToZero(linter))
