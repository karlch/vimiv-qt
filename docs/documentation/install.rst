Installation
============

Manual install
--------------

First of all get the code by cloning the git repository::

    $ git clone https://github.com/karlch/vimiv-qt/

or by downloading one of the snapshots on the
`releases <https://github.com/karlch/vimiv-qt/releases>`_ page.

System-wide installation
^^^^^^^^^^^^^^^^^^^^^^^^

TODO think about Makefile, icons, .desktop and so on

Using tox
^^^^^^^^^

TODO learn how to do this

Dependencies
------------

* `Python <http://www.python.org/>`_ 3.5 or newer
* `Qt <http://qt.io/>`_  # TODO find out which version is the minimum
    - QtCore / qtbase
    - QtSvg (optional for svg support)
* `PyQt5 <http://www.riverbankcomputing.com/software/pyqt/intro>`_  # TODO find out which version is the minimum
* `setuptools <https://pypi.python.org/pypi/setuptools/>`_ (for installation)

Package names for distributions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Installing the following packages should pull in all necessary dependencies for
building and running vimiv.

Arch Linux:
    * qt5-svg (optional)
    * python-pyqt5
    * python-setuptools

Fedora:
    * TODO

Debian/Ubuntu:
    * python3-pyqt5
    * python3-pyqt5.qtsvg (optional)
    * python3-setuptools
    * python3-dev (for building the C extension)
