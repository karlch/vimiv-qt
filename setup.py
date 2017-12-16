# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

import setuptools

setuptools.setup(
    name="vimiv",
    version="0.1",
    packages=setuptools.find_packages(),
    description="An image viewer with vim-like keybindings",
    scripts=["vimiv/vimiv"],
    license="MIT",
)
