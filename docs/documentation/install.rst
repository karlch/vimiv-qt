Installation
============

Table of Contents:

.. contents:: :local:

Manual install
--------------

First of all get the code by cloning the git repository and switch into the
repository folder::

    $ git clone https://github.com/karlch/vimiv-qt/
    $ cd vimiv-qt

or by downloading one of the snapshots on the
`releases <https://github.com/karlch/vimiv-qt/releases>`_ page.

System-wide installation
^^^^^^^^^^^^^^^^^^^^^^^^

Vimiv provides an example Makefile in the ``misc`` directory for convenience.
To install copy the Makefile into the repository directory, ``cp misc/Makefile
.``, tweak it to your liking and run (as root if installing system-wide)::

    $ make install

The list of available options can be displayed with::

    $ make options

These options are defined at the top of the Makefile and can be changed to fit
your needs. To uninstall vimiv the standard::

    $ make uninstall

should work.

Using tox
^^^^^^^^^

First of all get the code by cloning the git repository and switch into the
repository folder::

    $ git clone https://github.com/karlch/vimiv-qt/
    $ cd vimiv-qt

Then run tox to set up the virtual environment::

    $ tox -e mkvenv

This installs all needed Python dependencies and vimiv in a .venv subfolder.
You can now launch vimiv by running::

    $ .venv/bin/vimiv

You can create a wrapper script to start vimiv somewhere in your ``$PATH``,
e.g.  ``/usr/bin/vimiv`` or ``~/bin/vimiv``::

    #!/bin/sh
    ~/path/to/vimiv/.venv/bin/vimiv

Note that this does not install data files such as the icons or the
``vimiv.desktop`` file globally. Thus e.g. file managers may not find the vimiv
program as expected. To get an idea on how to install these, you can take a
look at the Makefile located in `misc/Makefile` and read the section above.

Dependencies
------------

* `Python <http://www.python.org/>`_ 3.5 or newer
* `Qt <http://qt.io/>`_   5.7.1 or newer
    - QtCore / qtbase
    - QtSvg (optional for svg support)
* `PyQt5 <http://www.riverbankcomputing.com/software/pyqt/intro>`_  5.7.1 or newer
* `setuptools <https://pypi.python.org/pypi/setuptools/>`_ (for installation)
* `piexif <https://pypi.org/project/piexif/>`_ (optional for exif support)

Package names for distributions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Installing the following packages should pull in all necessary dependencies for
building and running vimiv.

Arch Linux:
    * qt5-svg (optional)
    * python-pyqt5
    * python-setuptools
    * python-piexif (optional)

Fedora:
    * TODO

Debian/Ubuntu:
    * python3-pyqt5
    * python3-pyqt5.qtsvg (optional)
    * python3-setuptools
    * python3-dev (for building the C extension)
    * python3-piexif (TODO not available...)
