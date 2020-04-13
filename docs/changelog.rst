Changelog
=========

All notable changes to vimiv are documented in this file.

v0.7.0 (unreleased)
-------------------

Added:
^^^^^^

* The tilde character ``~`` is now also expanded to the user's home directory when
  running external commands started via ``!``.
* The ``%f`` wildcard to match the current filelist. This is useful in addition to ``*``
  as the filelist does not have to be equal to all files in the current directory.
* The ``:tag-open`` command equivalent to ``:tag-load`` followed by ``:open %m`` for
  convenience.
* Various small improvements to the ``:help`` command:

  * Consistent cleaner formatting using the html-subset of ``QLabel``.
  * New ``wildcards`` topic.

Changed:
^^^^^^^^

* Manipulations are no longer directly written to file when running ``:accept``.
  Instead, they behave according to the ``image.autowrite`` setting just like
  transformations.
* Zooming now always uses the center of the currently visible area as focal-point.

Fixed:
^^^^^^

* Centering the image on any type of resize, even when the user explicitly changed the
  scroll position.
* Displaying bindings containing special html characters such as '<' or '>' in keyhint
  widget.


v0.6.1 (2020-03-07)
-------------------

Fixed:
^^^^^^

* Fix removing thumbnails when the number of thumbnails decreases. Regression since
  v0.6.0.


v0.6.0 (2020-03-07)
-------------------

Added:
^^^^^^

* Command names can now be overridden by passing the ``name`` keyword to
  ``api.commands.register``.
* The ``:resize`` and ``:rescale`` commands to change the dimension of the original
  image. These are transformations and can be written to file.
* The ``:undo-transformations`` command to reset the image to the original.
* The ``:straighten`` command which displays a grid to straighten the current image.
  The image can then be straightened clockwise using the ``l``, ``>`` and ``L`` keys and
  counter-clockwise with ``h``, ``<`` and ``H``. Accept the changes with ``<return>``
  and reject them with ``<escape>``. It comes ith the ``{transformation-info}`` status
  module that displays the current straightening angle in degrees.
* The option to prompt the user for an answer using ``api.prompt.ask_question``. This
  comes with a blocking prompt which can be answered using key presses. The prompt can
  be styled with the ``prompt.font``, ``prompt.fg``, ``prompt.bg``,
  ``prompt.padding``, ``prompt.border_radius``, ``prompt.border`` and
  ``prompt.border.color`` styles.
* A new ``PromptSetting`` type which is essentially a boolean setting with the
  additional ``ask`` value. If the value is ``ask``, the user is prompted everytime the
  boolean state of this setting is requested.

Changed:
^^^^^^^^

* Removed prepended whitespace from completion options.
* The ``:nop`` command is now hidden from the completion.
* The function ``api.open`` had been renamed to ``api.open_paths`` to remove the clash
  with the python builtin. Using ``api.open`` directly is deprecated and will be removed
  in `v0.7.0`.
* The slideshow is always stopped when the image is unfocused.
* The ``image.autowrite`` setting is now ``ask`` by default. This should prevent
  surprises in case the changes are written to disk or discarded.
* ``:delete`` now only deletes images.

Fixed:
^^^^^^

* Always writing changed images to disk regardless of the ``image.autowrite`` setting.
* Segfault when applying manipulations.
* Crash when searching empty pathlist.
* Library column widths when starting in an empty directory.
* Reset image filelist selection when working directory content changes. We now ensure a
  custom selection, such as after ``:open %m``, is not replaced by all images in the
  working directory on a proposed reload.
* Selecting wrong path in library/thumbnail when deleting images in image mode.


v0.5.0 (2020-01-05)
-------------------

Added:
^^^^^^

* Basic support for binding mouse clicks and double clicks to commands. The relevant
  names are ``<button-NAME>`` and ``<double-button-NAME>``. Here ``NAME`` stands for the
  name of the mouse button to bind, e.g. ``left``, ``middle`` or ``right``.
* New ``imageformats`` plugin to ease adding support for additional image formats.
  Activate it by adding ``imageformats = name, ...`` to the plugins section of your
  ``vimiv.conf``. Here ``name, ...`` consists of the names of the image formats to add
  separated by a comma. Currently only the ``cr2`` raw format is implemented which
  requires `qt raw <https://gitlab.com/mardy/qtraw>`_.
* Path completion for the ``:mark`` command.
* Some help for migrating from the gtk version:

  * All gtk directories are backed up.
  * The tag files are migrated.
  * A welcome pop-up linking the :ref:`documentation <migrating>` is displayed.

Changed:
^^^^^^^^

* Saner default step for mouse zoom. Thanks
  `@OliverLew <https://github.com/OliverLew>`_ for catching this.
* Completion api no longer provides a ``BaseFilter`` class. Instead, the
  ``FilterProxyModel`` is always used for completion filtering. Customization can only
  be done by adding new completion models inheriting from ``BaseModel``.
* Completion widget is now shown/hidden depending on if there are completions or not.
* The ``:goto`` command can now be run with count only, e.g. ``:2goto``.
* The ``:goto`` command now consistently uses the modulo operator in all modes if the
  passed number is larger than the allowed maximum.

Fixed:
^^^^^^

* Showing keyhint widget in command mode.
* Partial matches with special keys such as ``<tab>``.
* The ``-s`` command line option to temporarily set an option. Broken since v0.4.0.
* Support for some jpg files not recognized by the ``imghdr`` module. Thanks
  `@maximbaz <https://github.com/maximbaz>`_ for the help.
* Undefined behaviour when running ``:enter command``. This now displays an error
  message and hints that ``:command`` or ``:search`` should be used instead.


v0.4.1 (2019-12-01)
-------------------

Fixed:
^^^^^^

* Not clearing existing status messages when pressing a key.


v0.4.0 (2019-12-01)
-------------------

Added:
^^^^^^

* The option to reference environment variables in the configuration files using
  ``${env:VARIABLE}``.
* The ``-b``, ``--basedir`` argument to override the base directory for storage. In
  contrast to ``--temp-basedir`` the directory is not deleted later.
* ``:rename`` and ``mark-rename`` commands to rename files starting from a common base.
* Panning images with the left mouse button.
* Zooming images with control+mouse-wheel.
* Path focus synchronization between all modes. Library and thumbnail mode are always
  synchronized. To keep the image synchronized with the others, either the ``n`` and
  ``p`` bindings can be used in the library, or the image can be opened explicitly. This
  behaviour is intended as opening a new image for every scroll in library/thumbnail
  would degrade performance significantly.

Changed:
^^^^^^^^

* External commands started with ``!`` no longer run in a sub-shell. To run commands
  with a sub-shell use ``:spawn`` instead.
* The selected path in the library is centered as in thumbnail mode if possible.
* The library always focuses the child directory when entering the parent directory via
  ``:scroll left``.
* The completion widget no longer has padding but instead keeps one space to align with
  the ``:`` in the command line. To simplify alignment, ``statusbar.padding`` option now
  only applies to the top and bottom.
* The vertical scrollbar in the completion widget is now hidden.
* A reason should now be passed to ``api.status.update`` and ``api.status.clear`` for
  logging purposes. Not passing a reason is deprecated and will be removed in `v0.5.0`.

Fixed:
^^^^^^

* Fuzzy path completion.
* Setting ``monitor_filesystem`` to ``false`` during runtime.
* Crash when entering command mode with ``{filesize}`` status module.
* XDG related directories such as XDG_CONFIG_HOME are created with mode 700 as expected
  by the XDG standard if they do not exist.
* Writing image changes on quit.
* Crash when running transform-related commands without valid pixmap.

Removed:
^^^^^^^^

* All ``completion.scrollbar`` related styles as the scrollbar is now hidden.


v0.3.0 (2019-11-01)
-------------------

Added:
^^^^^^

* Elements in library and thumbnail can be selected with a mouse double click.
* Library and thumbnail selection color is dimmed when the corresponding widget is not
  focused. It comes with the style options ``library.selected.bg.unfocus`` and
  ``thumbnail.selected.bg.unfocus``.
* Pop-up window to show keybindings for current mode. It can be shown with the
  ``:keybindings`` command and comes with the style options
  ``keybindings.bindings.color`` and ``keybindings.highlight.color``.
* Default left statusbar setting for manipulate mode showing basename, image size,
  modification date and the processing indicator.
* New ``:help`` command to display help messages on commands, settings and some general
  information.

Changed:
^^^^^^^^

* Any parsing errors when reading configuration files now log an error message and exit
  vimiv.
* The ``--config`` argument overrides the default user configuration path instead of
  appending to it. This is consistent with the ``--keyfile`` argument.
* Completely broken user styles now log an error message and exit vimiv instead of
  falling back to the default. This is consistent with the configuration file handling.
* Class instances can now be retrieved from the object registry via ``Class.instance``
  instead of ``objreg.get(Class)``. The old syntax has been deprecated and will be
  removed in `v0.4.0`.
* Show full command description on ``:command -h`` instead of the default help created
  by argparse.
* Default statusbar message timeout increased to 1 minute to make ``:command -h`` more
  usable.

Fixed:
^^^^^^

* The UI no longer blocks when processing working directory changes.
* Search reacts appropriately when the working directory changes. If the content is
  updated, search is re-run. When a new directory is opened, search is cleared.
* Support for colors with alpha-channel in styles file.
* Status messages are shown even if the bar is hidden.
* Setting the style option from the command-line via ``-s style NAME``.
* Crash when passing an invalid mode to commands.
* Mixing command and search history when cycling history without substring match.
* Switching between cycling history with and without substring match.
* Aliasing to commands including the ``%`` and ``%m`` wildcards.

Removed:
^^^^^^^^

* Support for colors in 3-digit hex format (#RGB), use #RRGGBB instead.


v0.2.0 (2019-10-01)
-------------------

Added:
^^^^^^

* A global ``font`` style option to set all fonts at once. If a local option such as
  ``statusbar.font`` is defined, it overrides the global option.
* New widget to display image metadata with the ``:metadata`` command bound to ``i`` in
  image mode by default. It comes with the style options ``metadata.bg``,
  ``metadata.padding`` and ``metadata.border_radius``.
* Completion of tag names for the ``:tag-*`` commands.
* The ``--command`` argument to run arbitrary commands on startup.
* Logging is now modular, especially for debugging. This comes with the ``--debug``
  argument which accepts the names of modules to debug.  E.g. ``--debug startup`` would
  show all debug messages from ``vimiv/startup.py`` without setting the global log level
  to ``DEBUG``.
* It is now possible to chain multiple commands with ``&&``. E.g. ``:write && quit``.
* New ``--open-selected`` flag for scroll and goto commands in library which
  automatically opens any selected image. Added keybindings are ``n`` and ``p`` for
  scrolling up/down and ``go`` for goto with this flag.

Changed:
^^^^^^^^

* All styles are now based upon base16. Therefore custom styles must define the colors
  ``base00`` to ``base0f``. All other style options are optional.
* Plugins now receive the additional information in the config file as first argument of
  their ``init`` function. ``init`` without arguments has been deprecated and will be
  removed in `v0.3.0`.

Fixed:
^^^^^^

* Elided text is now calculated correctly in the library.
* Setting value completions are no longer appended to the existing suggestions when the
  setting is changed.
* Overlay widgets are always raised in addition to shown ensuring them to be visible.
* Completions are now mode dependent removing misleading completions such as undelete in
  manipulate mode.
* Crash when trying to open tag which does not exist or has wrong permissions.
* Crash when loading a plugin with a syntax error.
* Running accepted manipulations multiple times as the changes were not reset.

Removed:
^^^^^^^^

* The ``--slideshow`` argument as it was broken and can easily be emulated by the new
  ``--command`` argument using ``--command slideshow``.


v0.1.0 (2019-08-15)
-------------------

Initial release of the Qt version.
