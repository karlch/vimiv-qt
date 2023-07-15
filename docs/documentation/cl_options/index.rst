Command Line Arguments
======================

When starting vimiv form the command line you have the ability to pass a number of
different argument to vimiv.

Examples
--------

In the following we present a few use cases of command line arguments.

* Start in library view with the thumbnail grid displayed::

    vimiv * --command "enter thumbnail" --command "enter library"

* Start in read-only mode. This prevents accidental modification (renaming, moving, editing etc.) of any images::

    vimiv --set read_only true

* Change WM_CLASS_INSTANCE to identify a vimiv instance::

    vimiv --qt-args "--name myVimivInstance"

* Print the last selected image to STDOUT when quitting::

    vimiv --output "%"

* Use vimiv as *Rofi for Images* to make a selection from candidate images::

    mySel=$(echo $myCand | vimiv --input --output "%m" --command "enter thumbnail")

* Print debug logs of your amazing plugin you are writing and of the `api._mark` module which does not behave as you are expecting::

    vimiv --debug myAmazingPlugin api._mark

Command Line Arguments
----------------------

The general calling structure is:

.. include:: synopsis.rstsrc

The following is an exhaustive list of all available arguments:

.. include:: options.rstsrc
