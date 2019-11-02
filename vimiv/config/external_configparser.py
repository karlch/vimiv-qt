# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Custom configparser able to retrieve variables from external resources.

Values in the configuration file with the syntax ${PREFIX:variable} are updated with the
value of the variable in the context corresponding to PREFIX. A valid example is
${env:variable} where the value of the environment variable $variable is retrieved.

To add more resources::

    * Implement the conversion function that retrieves the value of the variable, e.g.
      ``os.getenv(variable)``.
    * Add the conversion function with the corresponding prefix to
      ``ExternalInterpolation.CONVERTERS``.
"""

import configparser
import os
import re
from functools import lru_cache

from vimiv.utils import log

_logger = log.module_logger(__name__)
VARIABLE_RE = re.compile(r"\${(.*)}")


def get_parser() -> configparser.ConfigParser:
    """Return the custom configparser with support for external variables."""
    return configparser.ConfigParser(interpolation=ExternalInterpolation())


def getenv(variable: str) -> str:
    """Return the value of an environment variable.

    Used as converter function for parser and therefore raises configparser.Error on
    failure.
    """
    try:
        return os.environ[variable]
    except KeyError:
        raise configparser.Error(f"Variable '{variable}' not found in environment")


class ExternalInterpolation(configparser.Interpolation):
    """Configparser interpolation to update values from external resources.

    Class Attributes:
        CONVERTERS: Dictionary mapping variable prefixes to converter functions.
        PREFIXES: List of all valid variable converter prefixes.
    """

    CONVERTERS = {"env:": getenv}
    PREFIXES = ", ".join(CONVERTERS)

    def before_get(self, _parser, _section, _option, value: str, _defaults) -> str:
        """Update value from configfile with external resources."""
        return self.update(value)

    @staticmethod
    @lru_cache(None)
    def update(value: str) -> str:
        """Update value from configfile with external resources.

        If the value contains a variable with a valid converter prefix, the variable is
        replaced with the value of the corresponding converter function.

        Args:
            value: Value of config option possibly containing external variables.
        Returns:
            The value with any external variables replaced by their value.
        """
        match = VARIABLE_RE.match(value)
        if match is None:
            return value

        full_match, variable = match.group(0), match.group(1)
        _logger.debug("Updating config value '%s' using '%s'", value, full_match)

        for prefix, converter in ExternalInterpolation.CONVERTERS.items():
            if variable.lower().startswith(prefix):
                variable_value = converter(variable[len(prefix) :])
                _logger.debug(
                    "Updated '%s' = '%s' using '%s' converter",
                    full_match,
                    variable_value,
                    prefix.rstrip(":"),
                )
                return value.replace(full_match, variable_value)

        raise configparser.Error(
            f"Invalid variable name '{variable}', "
            f"must start with one of '{ExternalInterpolation.PREFIXES}'"
        )
