:orphan:

.. _hacking:

Hacking the Code
================

This page contains some guidelines as well as a few tips on how to get started with the
source code. If you feel like relevant information is missing, please open an
`issue on github <https://github.com/karlch/vimiv-qt/issues/>`_.

If any of the following recommendations would stop you from contributing,
please ignore them and contribute anyway. This is meant as help, not as show stopper!

In case you have questions, feel free to `contact me directly <karlch@protonmail.com>`_
or open an
`issue on github <https://github.com/karlch/vimiv-qt/issues/>`_.

.. contents::


Getting the Source Code
-----------------------

To retrieve the source code you can clone the repository using git::

    $ git clone https://github.com/karlch/vimiv-qt.git

Submitting Changes
------------------

The preferred way to submit changes is to
`fork the repository <https://help.github.com/articles/fork-a-repo/>`_
and to
`submit a merge request <https://help.github.com/articles/creating-a-pull-request/>`_.


Running the Development Version
-------------------------------

The arguably cleanest method is to :ref:`install vimiv using tox
<install_using_tox>` and use the script from the virtual environment::

    $ .venv/bin/vimiv

If you have the dependencies installed globally, you have two other options:

#. Build the c-extension in place and run the vimiv module directly from the repository
   directory::

    $ python setup.py build_ext --inplace
    $ python -m vimiv

#. Install the development version globally using::

    $ python setup.py develop

   In contrast to the other options, this replaces your global vimiv installation
   and removes the option to have both a development and a production executable.

For running in a clean directory, use the ``--temp-basedir`` option. To change
the log level, use the ``--log-level`` option, e.g. ``--log-level debug`` to
enable debugging messages. As this can become very noisy, the ``--debug`` flag is useful
to debug individual modules, e.g. ``--debug config.configfile``.


Tests and Checkers
------------------

Vimiv runs it's tests using
`tox <https://tox.readthedocs.io/en/latest/>`_. There are various different
environments:

* The standard test environment using
  `pytest <https://docs.pytest.org/en/latest/>`_. To run it with the latest PyQt
  version, use::

        tox -e pyqt

  This requires xorg xvfb to be installed on your system.

* A linting environment to check the code quality and style using
  `pylint <https://www.pylint.org/>`_,
  `pycodestyle <http://pycodestyle.pycqa.org/en/latest/>`_ and
  `pydocstyle <http://www.pydocstyle.org/>`_. Run it with::

        tox -e lint

* An environment to check the package for best-practices and completeness using
  `pyroma <https://github.com/regebro/pyroma>`_ and
  `check-manifest <https://github.com/mgedmin/check-manifest>`_.
  It can be run with::

        tox -e packaging

* The `mypy <http://www.mypy-lang.org/>`_ environment for static type checking launched
  with::

        tox -e mypy

In case you don't want to run any of the checkers locally, you can just wait for the CI
to run them. This is much slower and less direct though.


Style and Formatting
--------------------

Vimiv uses `pre-commit <https://pre-commit.com/>`_ for a consistent formatting. To
format the python source code, the
`black code formatter <https://github.com/ambv/black>`_ is used.

You can install the tools with::

    pip install pre-commit
    pip install black

And setup ``pre-commit`` using::

    pre-commit install

.. _writing_plugins:

Writing Plugins
---------------

A great way to contribute to vimiv without having to work with the main source code is
to write plugins. If you end up writing a plugin, please `let me know
<karlch@protonmail.com>`_ so I can advertise it on the :ref:`plugins` page. The basic
usage of plugins on described in the :ref:`plugins` page as well, some hints on the
plugin infrastructure are given in the ``vimiv.plugins`` module:

.. automodule:: vimiv.plugins
   :members: load, get_plugins

Adding Support for New Imageformats
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you would like to add support for a new image format that is not supported by Qt, you
can also solve this using the plugin system. A nice example of how to do this is the
`RawPrev <https://github.com/jeanggi90/RawPrev>`_ plugin which adds support for viewing
raw images using ``dcraw``.

To make this work, you need to implement two functions:

#. A function which checks if a path is of your filetype. The function must be of the
   same form as used by the standard library module
   `imghdr <https://docs.python.org/3/library/imghdr.html>`_.
#. The actual loading function which creates a ``QPixmap`` from the path.

Finally, you tell vimiv about the newly supported filetype::

    from typing import Any, BinaryIO

    from PyQt5.QtGui import QPixmap

    from vimiv import api


    def test_func(header: bytes, file_handle: BinaryIO) -> bool:
        """Return True if the file is of your format."""

    def load_func(path: str) -> QPixmap:
        """Implement your custom loading here and return the created QPixmap."""

    def init(_info: str, *_args: Any, **_kwargs: Any) -> None:
        """Setup your plugin by adding your file format to vimiv."""
        api.add_external_format("fmt", test_func, load_func)


Source Code Hints
-----------------
The following paragraphs explain some of the core concepts of the source code
which may be useful to understand before working on bigger changes.

Logging
^^^^^^^

Logging is handled by the ``vimiv.utils.log`` module which wraps around the
`standard python logging library <https://docs.python.org/3/howto/logging.html>`_:

.. automodule:: vimiv.utils.log


API Documentation
^^^^^^^^^^^^^^^^^

.. automodule:: vimiv.api

The following paragraphs provide an overview of the modules available in the
``api`` and give examples on how to use them.

The Object Registry
"""""""""""""""""""

.. automodule:: vimiv.api.objreg
   :members:

Modes
"""""

.. automodule:: vimiv.api.modes
   :members: widget, get_by_name, current

Commands
""""""""

.. automodule:: vimiv.api.commands
   :members:

Keybindings
"""""""""""

.. automodule:: vimiv.api.keybindings

Status Modules
""""""""""""""

.. automodule:: vimiv.api.status
   :members:

Completion
""""""""""

.. automodule:: vimiv.api.completion
   :members:
    BaseModel

Working Directory
"""""""""""""""""

.. automodule:: vimiv.api.working_directory

Prompt
""""""
.. automodule:: vimiv.api.prompt
    :members:
     ask_question

Imutils Module
^^^^^^^^^^^^^^

.. automodule:: vimiv.imutils

Image Editing Modules
"""""""""""""""""""""

This section gives a quick overview of the modules that deal with image editing and how
to add new functionality to manipulate images.

.. automodule:: vimiv.imutils.imtransform

.. automodule:: vimiv.imutils.immanipulate
   :members: ManipulationGroup
   :private-members:

.. _c_extension:

Adding New Manipulations to the C-Extension
""""""""""""""""""""""""""""""""""""""""""""

To add new manipulations to the C-extension, two things must be done.

First, you implement a new manipulate function in its own header such as
``brightness_contrast.h``. The function should take the image data as pure bytes, the
size of the data array as well as your new manipulation values as arguments. Task of the
function is to update the data with the manipulation values accordingly. For this it
needs to iterate over the data and update each pixel and channel (RGBA) accordingly.

Once you are happy with your manipulate function, it needs to be registered in
``manipulate.c``. First you write a wrapper function that converts the python arguments
to C arguments, runs the manipulate function you just implemented and returns the
manipulated data back to python. How this is done can be seen in ``manipulate_bc`` and
``manipulate_hsl``. The basic structure should be very similar for any case. Finally you
add the python wrapper function to the ``ManipulateMethods`` definition. Here you define
the name of the function as seen by python, pass your function, the calling convention
and finally a short docstring.

For much more information on extending python with C see
`the python documentation <https://docs.python.org/3/extending/extending.html>`_
