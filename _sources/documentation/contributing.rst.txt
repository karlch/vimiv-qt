.. _contributing:

Contributing Guidelines
=======================

This page contains guidelines for contributing to vimiv as well as a few tips
on how to get started. If you feel like relevant information is missing, please
open an `issue on github <https://github.com/karlch/vimiv-qt/issues/>`_.

In case any of the following recommendations would stop you from contributing,
please ignore them and contribute anyway. The chances are that I will fix
upcoming issues for you. The guidelines are simply meant to ease work for me
and to keep everything consistent.

Table of Contents:

.. contents:: :local:


Finding Something to Do
----------------------------

You probably already know what you want to work on as you are reading this
page. If you want to implement a new feature, it might be a good idea to open a
feature request on the `issue tracker
<https://github.com/karlch/vimiv-qt/issues/>`_ first. Otherwise you might be
disappointed if I do not accept your pull request because I do not feel like
this should be in the scope of vimiv.

If you want to find something to do, check the
`issue tracker <https://github.com/karlch/vimiv-qt/issues/>`_. Some hints:

* `Issues that are good for newcomers <https://github.com/karlch/vimiv-qt/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22>`_
* `Issues that require help <https://github.com/karlch/vimiv-qt/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22>`_
* `Issues that do not involve coding <https://github.com/karlch/vimiv-qt/issues?q=is%3Aissue+is%3Aopen+label%3Anot-code>`_

As this is my first larger project, comments and improvements to the existing
code base are more than welcome.

If you prefer C over python, you may be interested in implementing
`additional manipulations in the C extension <https://github.com/karlch/vimiv-qt/issues/7>`_.

Improving the existing documentation and website is always another option in
case you do not want to write code.


Getting the Source Code
-----------------------

To retrieve the source code you can clone the repository using git::

    $ git clone https://github.com/karlch/vimiv-qt.git

Submitting Changes
^^^^^^^^^^^^^^^^^^

The preferred way to submit changes is to
`fork the repository <https://help.github.com/articles/fork-a-repo/>`_
and to
`submit a merge request <https://help.github.com/articles/creating-a-pull-request/>`_.


Running the Development Version
-------------------------------

The arguably cleanest method is to :ref:`install vimiv using tox
<install_using_tox>` and use the script from the virtual environment::

    $ .venv/bin/vimiv

If you have the dependencies installed globally, you have two options:
Install vimiv globally using::

    $ python setup.py develop

or run the vimiv module directly from the repository directory::

    $ python -m vimiv

The first option, in contrast to the other two, will replace your global vimiv
version and remove the option to have both a development and a production
executable.

For running on a clean directory, use the ``--temp-basedir`` option. To change
the log level, use the ``--log-level`` option, e.g. ``--log-level debug`` to
enable debugging messages.


Tests and Checkers
------------------

TODO Write this once the testing routine has stabilized


Style and Formatting
--------------------

Vimiv uses the `black code formatter <https://github.com/ambv/black>`_ to
automatically format the source code. To install black, run::

   pip install black

or use the package manager of your OS if applicable. Formatting the source code
is done using::

   black vimiv tests

For more information on the formatter as well as a few useful tips, visit
`the project's github page <https://github.com/ambv/black>`_.

TODO docstrings


Source Code Hints
-----------------
The following paragraphs explain some of the core concepts of the source code
which may be useful to understand before working on bigger changes.

Logging
^^^^^^^

For logging purposes, the
`standard python logging library <https://docs.python.org/3/howto/logging.html>`_
is used. Therefore, to use logging anywhere in vimiv::

    # Import the logging module at the beginning
    import logging
    ...
    # Use it as usual in the code
    logging.info("This is an important information")

Three handlers are currently used:

* One to print to the console
* One to save the output in a log file located in
  ``$XDG_DATA_HOME/vimiv/vimiv.log``
* One to print log messages to the statusbar


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
   :members: widget, get_by_name, current, enter, leave, toggle

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

The Image Loading Process
^^^^^^^^^^^^^^^^^^^^^^^^^

Images are loaded using a chain of signals defined in
``vimiv.imutils.imsignals``.

In a first step, the path to a new image is determined and communicated using
the ``open_new_image`` signal which says that a new image is supposed to be
opened. This can be done by the library, the thumbnail widget as well as using
the ``:open`` command.

The ``vimiv.imutils.imstorage`` module connects to this signal, processes the
path (as well as all other paths in the same directory for convenience), and
then emits the ``new_image_opened`` signal.

This signal is accepted by the file handler in ``vimiv.imutils.imfile_handler``
which then loads the actual image using ``QImageReader``. Once the format of
the image has been determined, and a displayable Qt widget has been created,
the file handler emits one of:

* ``pixmap_loaded`` for standard images
* ``movie_loaded`` for animated Gifs
* ``svg_loaded`` for vector graphics

The image widget in ``vimiv.gui.image`` connects to these signals and displays
the appropriate Qt widget.


Updating the Documentation
--------------------------

There is a script which builds the website's reST documentation automatically
from the source code. It must be run from the repository directory using::

    $ scripts/src2rst.py

Once this is completed I can re-build the actual website using ``sphinx``.

In analogy another script is used to re-build the man page::

    $ scripts/gen_manpage.sh
