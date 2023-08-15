# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

"""Entry point for vimiv. Run the vimiv process."""

import sys

import vimiv.startup


if __name__ == "__main__":
    sys.exit(vimiv.startup.main())
