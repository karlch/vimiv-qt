#!/usr/bin/env python
# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

"""Script to run pylint over the test-suite.

Required due to https://github.com/PyCQA/pylint/issues/352.
"""

import argparse
import os
import sys
import subprocess
from typing import List


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    return parser


def get_all_python_files(directory: str) -> List[str]:
    """Retrieve all files in a directory by walking it."""
    infiles = [
        os.path.join(dirpath, filename)
        for dirpath, _, filenames in os.walk(directory)
        for filename in filenames
        if os.path.splitext(filename)[-1] == ".py"
    ]
    return infiles


def run_pylint(infiles: List[str]):
    """Run pylint over all files in infiles."""
    disabled = (
        "redefined-outer-name",  # Fixture passed as argument
        "unused-argument",  # Fixture used for setup / teardown only
        "missing-docstring",  # Not required in tests
        "command-docstring",  # Not required in tests
        "protected-access",  # Acceptable in tests
        "compare-to-empty-string",  # Stricter check than False in tests
        "import-error",  # Errors on pytest related modules
    )
    ignored = ("mock_plugin_syntax_error.py",)
    command = (
        "pylint",
        f"--disable={','.join(disabled)}",
        f"--ignore={','.join(ignored)}",
        *infiles,
    )
    print("Running pylint over tests")
    return subprocess.run(command, check=False).returncode


def main():
    parser = get_parser()
    args = parser.parse_args()
    infiles = get_all_python_files(args.directory)
    sys.exit(run_pylint(infiles))


if __name__ == "__main__":
    main()
