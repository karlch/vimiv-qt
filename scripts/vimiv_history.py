#!/usr/bin/env python3
# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

"""Script to print the vimiv history of a given mode.

Reads the history from vimiv's json history file and prints the elements
line-by-line.  The default mode is image. To change the mode, pass it using its
name.

In case you use a custom data directory or are not using linux, please pass the
filename as argument.
"""

import argparse
import json
import os
from typing import List


def main():
    parser = get_parser()
    args = parser.parse_args()
    history = read_history(mode=args.mode, filename=args.filename)
    print(*history, sep="\n")


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "mode",
        choices=("image", "thumbnail", "library", "manipulate"),
        default="image",
        nargs="?",
        help="The mode for which history is printed",
    )
    parser.add_argument(
        "-f",
        "--filename",
        default=os.path.expanduser("~/.local/share/vimiv/history.json"),
        help="Path to the history file to read",
    )
    return parser


def read_history(*, mode: str, filename: str) -> List[str]:
    with open(filename, "r", encoding="utf-8") as f:
        content = json.load(f)
    return content[mode]


if __name__ == "__main__":
    main()
