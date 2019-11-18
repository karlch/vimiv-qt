# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import ast
import os
import re
import setuptools

import fastentrypoints

# C extensions
manipulate_module = setuptools.Extension(
    "vimiv.imutils._c_manipulate", sources=["c-extension/manipulate.c"]
)


try:
    BASEDIR = os.path.dirname(os.path.realpath(__file__))
except NameError:
    BASEDIR = None


def read_file(filename):
    """Read content of filename into string and return it."""
    with open(filename) as f:
        return f.read()


def read_from_init(name):
    """Read value of a __magic__ value from the __init__.py file."""
    field_re = re.compile(r"__{}__\s+=\s+(.*)".format(re.escape(name)))
    path = os.path.join(BASEDIR, "vimiv", "__init__.py")
    line = field_re.search(read_file(path)).group(1)
    return ast.literal_eval(line)


setuptools.setup(
    python_requires=">=3.6",
    install_requires=["PyQt5>=5.9.2"],
    packages=setuptools.find_packages(),
    ext_modules=[manipulate_module],
    entry_points={"gui_scripts": ["vimiv = vimiv.startup:main"]},
    name="vimiv",
    version=".".join(str(num) for num in read_from_init("version_info")),
    description=read_from_init("description"),
    long_description=read_file(os.path.join(BASEDIR, "README.md")),
    long_description_content_type="text/markdown",
    url=read_from_init("url"),
    project_urls={
        "Source Code": "https://github.com/karlch/vimiv-qt",
        "Bug Tracker": "https://github.com/karlch/vimiv-qt/issues",
        "Documentation": "https://karlch.github.io/vimiv-qt/documentation",
    },
    author=read_from_init("author"),
    author_email=read_from_init("email"),
    license=read_from_init("license"),
    keywords=["pyqt", "image viewer", "vim"],
    zip_safe=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 or later " "(GPLv3+)",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Multimedia",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Graphics :: Viewers",
    ],
)
