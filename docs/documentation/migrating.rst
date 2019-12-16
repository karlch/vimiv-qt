.. _migrating:

Migrating from the Gtk Version to Qt
====================================

Some time ago I decided to rewrite vimiv completely in Qt because I was not happy with
the Gtk version and the source code. For some more details, you can check
`the corresponding issue on github <https://github.com/karlch/vimiv/issues/61>`_.

Besides the maintenance improvements for me and cleaner code + tests which should make
contributing easier, there were a number of major improvements and new feature
including:

* Much better performance, especially in thumbnail mode.
* Complete customization with :ref:`styles <styles>`.
* The possibility to bind key sequences like ``gg``.
* A keyhint widget popping up after 500 ms to help you with finding the missing part of
  key sequences.
* Customization of the statusbar with :ref:`status modules<statusbar>`.
* A plugin system enabling print support.
* Automatic reload when the image / directory was changed from the outside.
* Better synchronization between the various modes.

Overall I hope that the improvements of the Qt version outweigh the inconvenience of a
lot of breaking changes. The following sections summarize some of the major changes to
give you a feeling of what will break when migrating. If you have any questions or need
help, please do not hesitate to open an
`issue on github <https://github.com/karlch/vimiv-qt/issues/>`_ or
`contact me directly <karlch@protonmail.com>`_.

.. contents::

Major Changes
-------------

Key Sequences
^^^^^^^^^^^^^

It is now possible to bind key sequences like ``gg``. This possibility changed the
default bindings for switching modes. The library is entered with ``gl`` and toggled
with ``tl``. Same holds for thumbnail and manipulate mode with ``t`` as suffix instead
of ``l``. Image mode can only be entered with ``gi``, not toggled, as it is the "normal"
mode of vimiv. To help you with partial matches, a keyhint widget pops up 500 ms after
the first key press.

Keybinding Names
^^^^^^^^^^^^^^^^

* Naming of modifiers has changed to account for key sequences and for consistency.

  * ``Shift+`` is largely replaced by the actual character, e.g. ``Shift+w`` becomes
    ``W``. Where this is not possible, use ``<shift>``, e.g. ``<shift><tab>``.
  * ``^q`` becomes ``<ctrl>q``.
  * ``Alt+l`` becomes ``<alt>l``.
* If keys have a string representation, this is their keybinding. So ``+``, ``/`` and so
  forth are the valid keybindings, not ``plus`` or ``slash``. Only exception is
  ``<colon>`` for ``:`` as this is a valid separator for the configuration file.
* Special keys with no string representation are always surrounded in ``<>`` brackets
  and are lower-case.  Therefore ``Escape`` becomes ``<escape>``, ``Return``
  ``<return>`` and so forth.

.. hint::

    If you want to figure out the name of a specific key or mouse button, run vimiv with
    ``--debug gui.eventhandler``. You can find the corresponding name in the first
    output line after pressing/clicking it. For example, when pressing the ``q`` key,
    you would retrieve something along::

        DEBUG    <gui.eventhandler>   EventHandlerMixin: handling q for mode library

Command Names
^^^^^^^^^^^^^

Command handling has been redesigned for better scalability. This means that many names
and/or arguments have changed. You can find
:ref:`a complete overview of the current commands <commands>` in the documentation.
If you have trouble finding out how a previous command changed or are missing something,
please do not hesitate to open an
`issue on github <https://github.com/karlch/vimiv-qt/issues/>`_ or
`contact me directly <karlch@protonmail.com>`_.

Settings
^^^^^^^^

The rewrite has been used to rethink various settings. I hope the names are now clearer
and the handling is more consistent. This is a brief overview of what happened to the
settings that were available in the gtk version. The word before the ``.`` indicates the
section, the one after is the option name.

.. table:: Overview of settings changes
    :widths: 30 70

    ============================= ===========
    Setting                       Change
    ============================= ===========
    general.start_fullscreen      Removed, use the ``--fullscreen`` command line flag instead
    general.start_slideshow       Removed, use ``--command slideshow`` instead
    general.slideshow_delay       Moved to ``slideshow.delay``
    general.shuffle               Remains the same
    general.display_bar           Moved to ``statusbar.show``
    general.default_thumbsize     Moved to ``thumbnail.size``
    general.geometry              Removed, use ``--geometry`` instead
    general.recursive             Removed, use the corresponding shell tools instead
    general.rescale_svg           Removed, this is always done as it is now performant
    general.overzoom              Moved to ``image.overzoom``
    general.search_case_sensitive Moved to ``search.ignore_case``
    general.incsearch             Moved to ``search.incremental``
    general.copy_to_primary       Removed, the ``:copy-name`` command has an optional ``--primary`` flag instead
    general.commandline_padding   Removed, use :ref:`styles <styles>` instead
    general.thumb_padding         Removed, use :ref:`styles <styles>` instead
    general.completion_height     Removed, use :ref:`styles <styles>` instead
    general.play_animations       Moved to ``image.autoplay``
    |
    library.start_show_library    Moved to ``general.startup_library``
    library.library_width         Removed, use :ref:`styles <styles>` instead
    library.expand_lib            Removed, please open an issue if you miss this feature
    library.border_width          Removed, use :ref:`styles <styles>` instead
    library.markup                Removed, use :ref:`styles <styles>` instead
    library.show_hidden           Remains the same
    library.desktop_start_dir     Removed, please open an issue if you miss this feature
    library.file_check_amount     Removed, we use the total number of files instead
    library.tilde_in_statusbar    Moved to ``statusbar.collapse_home``
    |
    edit.autosave_images          Moved to ``image.autowrite``
    ============================= ===========

Marks and Tags
^^^^^^^^^^^^^^

Your tag files are migrated and should continue working as is. However, the behaviour of
marks and tags has changed in some ways.

* The ``:mark`` command can now take any number of paths as argument. This includes
  typical shell wildcards and replaces the unorthodox behaviour of ``:mark-between``. To
  mark a list of images, pass them or the corresponding wildcard to ``:mark``, e.g.::

      :mark images_1*.jpg

* The ``mark`` command now toggles the mark status of the paths passed. The default
  binding ``m`` is therefore equivalent to the old ``:mark_toggle`` bound to ``M``.
* Calling ``:tag-load`` now marks all images in the tag instead of loading them into
  image mode. To open them in image mode, call ``:open %m`` afterwards.

Manipulate
^^^^^^^^^^

Navigation in manipulate mode has been redesigned for better scalability. The one letter
shortcuts to manipulation names were unfortunately rather limiting...

* To focus the next/previous manipulation in the current tab, use ``n``/``p``.
* To focus the next/previous tab, use ``<tab>``/``<shift><tab>``.

Migration
---------

When you first launch the qt version and you had a local ``vimivrc`` of the gtk version:

* All ``vimiv`` folders are backed up to ``vimiv-gtk-backup``.
* Your tags are migrated accordingly.
* A welcome pop-up with the most important information is shown.
