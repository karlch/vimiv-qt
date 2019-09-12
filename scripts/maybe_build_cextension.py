# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Ensure the c-extension has been build inplace for testing.

Locally, when running tox without compiling the c-extension, an ImportError for
_c_manipulate may be raised. This is fixed by this script.
"""

import glob
import os
import subprocess
import sys


if __name__ == "__main__":
    filedir = os.path.dirname(os.path.realpath(__file__))
    rootdir = os.path.dirname(filedir)
    extension_built = glob.glob(os.path.join(rootdir, "vimiv", "imutils", "_c_*"))

    if not extension_built:
        print("Building c-extension...")
        setup_py = os.path.join(rootdir, "setup.py")
        cmd = sys.executable, setup_py, "build_ext", "--inplace"
        subprocess.run(cmd, check=True)
