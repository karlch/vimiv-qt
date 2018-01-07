# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import setuptools

# C extensions
manipulate_module = setuptools.Extension("vimiv.imutils._c_manipulate",
                                         sources=["c-extension/manipulate.c"])

setuptools.setup(
    name="vimiv",
    version="0.1",
    packages=setuptools.find_packages(),
    ext_modules= [manipulate_module],
    description="An image viewer with vim-like keybindings",
    scripts=["vimiv/vimiv"],
    license="GPLv3",
)
