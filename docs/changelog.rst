Changelog
=========

All notable changes to vimiv are documented in this file.

v0.10.0 (unreleased)
--------------------

Added:
^^^^^^

* Support for PyQt6 and thus Qt6. In case both are installed, vimiv prefers PyQt6 and
  only falls back to PyQt5 if PyQt6 is not available. The Qt version and wrapper can be
  selected explicitly with the ``QT_SELECT`` environment variable, using:

  * ``5`` or ``PyQt5``: Use PyQt5.
  * ``6`` or ``PyQt6``: Use PyQt6.
  * ``PySide6``: Use PySide6 (Qt for Python). This is highly experimental and should be
    used with care.

Fixed:
^^^^^^

* The SVG image header check to no longer return true for all XML files.
* Binding the ``<delete>`` key as special key. Thanks `@xfzv`_!


v0.9.0 (2023-07-15)
-------------------

Added:
^^^^^^

* More vim movement commands with corresponding keybindings, namely:

  * ``:scroll page-up/page-down/half-page-up/half-page-down`` mapped to ``<ctrl>b``,
    ``<ctrl>f``, ``<ctrl>u`` and ``<ctrl>d`` for library and thumbnail mode.
  * ``:end-of-line`` mapped to ``$`` and ``:first-of-line`` mapped to ``^`` to select
    the first icon of the current row in thumbnail mode.

  Thanks `@jcjgraf <https://github.com/jcjgraf>`_ for the idea!
* The ``--action`` flag for the ``:mark`` command. ``--action toggle`` is the default
  and keeps the previous behaviour of the mark command, i.e. inversing the mark status
  of the passed path(s). In addition one can now use ``--action mark`` and
  ``--action unmark`` to force (un-) marking the paths.
* Support for the ``avif`` file format using the imageformats plugin. To enable it, add
  ``imageformats = avif`` to the ``[PLUGINS]`` section of your ``vimiv.conf``. Requires
  `qt-avif-image-plugin <https://github.com/novomesk/qt-avif-image-plugin>`_.
  Thanks `@schyzophrene-asynchrone`_!
* A few more default mouse bindings:

  * ``<button-right>`` to enter the library from image and thumbnail mode.
  * ``<button-right>`` to go to the parent directory in the library.
  * ``<button-middle>`` to enter thumbnail mode from image and library mode.
  * ``<button-forward>`` and ``<button-back>`` to select the next/previous image in
    image mode.
  * ``<button-forward>`` and ``<button-back>`` to scroll down/up and open any selected
    image in library mode.
  * ``<button-forward>`` and ``<button-back>`` select the next/previous thumbnail in
    thumnbail mode.

  Thanks `@BachoSeven`_ for your thoughts!
* The ``:copy-image`` command which copies the selected image to the clipboard. The
  flags ``--width``, ``--height`` and ``--size`` allow to scale the copied image.
  Thanks `@jcjgraf`_!
* The ``read_only`` setting. When set to true, all commands that may write changes to
  disk are disabled. This comes with the ``{read-only}`` status module which displays
  ``[RO]`` in case ``read_only`` is true. Note that you must add this to your
  vimiv.conf to enable it if you already define the left status contents. The new
  defaults are::

    left = {pwd}{read-only}
    left_image = {index}/{total} {basename}{read-only} [{zoomlevel}]
    left_thumbnail = {thumbnail-index}/{thumbnail-total} {thumbnail-name}{read-only}

  Thanks `@willemw12`_ for the idea!
* The ``zh`` keybinding to toggle hidden files.
  Thanks `@Kakupakat`_ for the idea!
* The ``:print-stdout`` command which prints a given list of string to the STDOUT.
* The ``:mark-print`` default alias which prints all marked images to STDOUT using
  ``:print-stdout``.
* The ``-o TEXT`` flag to print ``TEXT`` to standard output before exit. Wildcards are
  expanded before printing, allowing to for example print marked files using ``-o %m``.
  Thanks `@loiccoyle`_ for the idea!
* The ``-i`` flag to read paths to open from standard input instead.
  Thanks `@loiccoyle`_ for the idea!
* The ``--qt-args`` flag to pass arguments directly to qt. When passing multiple
  arguments, they must be quoted accordingly, e.g.
  ``vimiv --qt-args '--name floating'``.
  Thanks `@loiccoyle`_ for the discussion!
* Statusbar modules ``name``, ``thumbnail-basename``, ``extension`` and
  ``thumbnail-extension``.
* Support for the ``jp2`` file format using the imageformats plugin. To enable it, add
  ``imageformats = jp2`` to the ``[PLUGINS]`` section of your ``vimiv.conf``. Requires
  the qt imageformats plugin. Thanks `@szsdk`_ for testing!
* The ``image.zoom_wheel_ctrl`` setting which toggles the need to hold the ``<ctrl>``
  modifier for zooming an image with the mouse wheel. Thanks `@ArtemSmaznov`_ for the
  idea!
* The ``--ask`` flag for the ``:delete`` command to prompt the user for confirmation
  before deleting. Thanks `@timsofteng`_ for the idea!
* Support for different sorting options for images and directories via the
  ``sort.image_order``, ``sort.directory_order``, ``sort.reverse`` and
  ``sort.ignore_case`` settings. Please refer to the :ref:`documentation <sorting>` for
  further details. Thanks to `@kAldown`_ for the initial implementation, `@jcjgraf`_ for
  taking over, and many more joining in the discussions and reminding us why this
  feature is important!
* New ``{cursor-position}`` statusbar module which tracks the mouse cursor position in
  image coordinates.
* The ``:crop`` command which displays a rectangle to crop the curent image. The
  rectangle can be dragged and resized using the mouse. As with ``:straighten``, accept
  the changes with ``<return>`` and reject them with ``<escape>``. The
  ``{transformation-info}`` status module displays the currently selected geometry of
  the original image. Thanks `@Yutsuten`_ for reviving this!
* Add the ``none`` sorting type for the ``sort.image_order`` and ``sort.directory_order``
  options, implemented by `@buzzingwires`_
* Add the ``thumbnail.save`` option, implemented by `@buzzingwires`_

Changed:
^^^^^^^^

* New set of default metadata key sets numbered from 1 to 5. Thanks `@jcjgraf`_!
* When toggling ``library.show_hidden`` the selection now stays on the same file, not
  the same index.
* Using the mouse to scroll in library and thumbnail mode now changes the selection
  instead of just scrolling the view. Horizontal scrolling in thumbnail mode is
  supported.
* Default statusbar module ``thumbnail-name`` was changed to ``thumbnail-basename`` for
  ``left_thumbnail``.
* Support for Qt versions 5.9 and 5.10 was officially dropped. These are no longer
  supported by our testing framework, and 5.11 is out since July 2018. Code will likely
  still work with these versions, but as it is no longer tested, there is no guarantee.
* The ``shuffle`` setting was moved into the ``sort`` group.
* Complete refactoring of metadata support. The handler functionality is moved out
  to the plugin space, allowing for full flexibility in choosing a suitable backend. By
  default, ``metadata_pyexiv2`` or ``metadata_piexif`` is loaded, if the respective
  backend is installed. The default behaviour can be overridden by explicitly loading a
  metadata plugin.
* Vimiv now requires at least Python 3.8 and thus PyQt 5.13.2.
* Qt logs of level warning / critical are now suppressed if the corresponding vimiv log
  level is higher.

Fixed:
^^^^^^

* Crash when deleting images without permission. Thanks `@jcjgraf`_!
* Undeleting symlinks. Thanks `@jcjgraf`_!
* Expanding tilde to home directory when using the ``:write`` command. Thanks
  `@jcjgraf`_ for pointing this out!
* Completion for aliases.
* Crash when extracting metadata using piexif from a non JPEG or TIFF image. Thanks `@BachoSeven`_ for pointing this out!
* Crash when searching in a symlinked directory. Thanks `@BachoSeven`_ for pointing this
  out!
* Inconsistencies between the base status bar module and the thumbnail- modules.


v0.8.0 (2021-01-18)
-------------------

Added:
^^^^^^

* A customizable set of metadata key settings numbered ``metadata.keys1`` to
  ``metadata.keys3``. The default is ``metadata.keys1``. One can switch between the sets
  using ``[count]i``. To override one of these sets, add ``keys2 =
  Override,SecondSet``. To add a new one, use ``keys4 = New,Fourth,Set``. Here the
  values must be a comma-separated list of valid metadata keys. Thanks `@jcjgraf`_!
* ``<equal>`` is now bound to ``:scale --level=fit`` in image mode. Thanks `@jcjgraf`_
  for pointing this out!
* The ``:history-clear`` command to clear the command history.
* Handle ``unbind`` explicitly when parsing ``keys.conf``. Instead of binding a key to
  the ``:unbind`` command, any existing keybinding for this key is now removed.
* A new api interface which enables writing plugins to support new image formats. See
  :ref:`support_new_imageformats` for more details.
  Thanks `@jcjgraf`_!
* New ``--keep-zoom`` flag for ``:next`` and ``:prev`` which preserves zoom level and
  scroll position of the current image.
  Thanks `@jcjgraf`_ for the idea!
* Exif support using `pyexiv2 <https://python3-exiv2.readthedocs.io/>`_. When available,
  vimiv now prefers pyexiv2 over piexif for exif support due to its ability to format
  exif values into a human readable format. Thanks a lot
  `@jcjgraf`_ for all your hard work, thoughts and comments
  on this topic!
* New ``:metadata-list-keys`` command to display all valid exif keys for the current
  image.

Changed:
^^^^^^^^

* The ``=`` key can now be bound using ``<equal>``. Using the raw ``=`` character is not
  possible in ``keys.conf`` as it is treated as separator much like ``:``.
* Renamed ``vimiv.appdata.xml`` to ``org.karlch.vimiv.qt.metainfo.xml``.
* History is now mode based. The plain-text history file is replaced by a json file
  which stores the history of each mode. Any existing history is migrated by adding it
  to every mode and keeping a backup of the plain-text history file at ``history.bak``.
  The script ``scripts/vimiv_history.py`` is provided to print the history of a mode
  line-by-line as aid in case user-scripts relied on the plain-text nature of the
  history file.

Fixed:
^^^^^^

* Not selecting the first library row in a directory in case the directory was
  previously empty.
* Initial selection of ``:complete --inverse``. This is now correctly the last row, not
  the second-to-last.
* Various issues when handling backslash and percent characters in paths and
  completions. Thanks
  `@woefe`_ for pointing these out!
* Quoting of paths and the date format of the trashinfo file created by the ``:delete``
  command. Thanks `@woefe`_ for the bug report.
* Creating thumbnails for thumbnails.
* Opening single hidden images when ``library.show_hidden`` is set to false. Thanks
  `@schyzophrene-asynchrone`_ for pointing
  this out!
* Displaying key binding conflicts before parsing the complete ``keys.conf``. This lead
  to scenarios in which a warning was displayed which is later resolved by the
  corresponding ``unbind``. Thanks `@schyzophrene-asynchrone`_!
* Crash when toggling manipulate mode before ever entering it. Thanks
  `@pozitron57`_ for pointing this out!
* Crash when dragging thumbnails.


v0.7.0 (2020-05-17)
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
* Spaces in statusbar settings such as ``statusbar.left`` are now only replaced by
  the html-equivalent ``&nbsp;`` if there are multiple subsequent spaces. This keeps
  wanted additional spacing while allowing to use html code such as
  ``<span style='color: #8FBCBB; font-weight: bold;'>colored and bold</span>``.
* Both the command line and the widget to display status messages are now overlay
  widgets instead of being integrated with the bar. This decouples them from the main
  grid layout and better reflects their role as they are being shown temporarily over
  the current widget/image.

Fixed:
^^^^^^

* Centering the image on any type of resize, even when the user explicitly changed the
  scroll position.
* Displaying bindings containing special html characters such as '<' or '>' in the
  keyhint widget and in the ``{keys}`` status module.
* Crash when scrolling thumbnail mode with empty thumbnail list.
* Crash when running ``:goto`` without valid paths/images/thumbnails.
* Switching mode when toggling an inactive mode.
* Displaying status messages larger than one line in manipulate mode.
* Resetting settings to ther default value via ``:set setting.name``. The value of the
  setting was changed accordingly, but the ``changed`` signal was not emitted which
  means nothing actually happened.
* Hanging when a FIFO file is in the current directory.


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

* Saner default step for mouse zoom. Thanks `@OliverLew`_ for catching this.
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
  `@maximbaz`_ for the help.
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


.. _@jcjgraf: https://github.com/jcjgraf
.. _@woefe: https://github.com/woefe
.. _@schyzophrene-asynchrone: https://github.com/schyzophrene-asynchrone
.. _@pozitron57: https://github.com/pozitron57
.. _@OliverLew: https://github.com/OliverLew
.. _@maximbaz: https://github.com/maximbaz
.. _@BachoSeven: https://github.com/BachoSeven
.. _@willemw12: https://github.com/willemw12
.. _@Kakupakat: https://github.com/Kakupakat
.. _@loiccoyle: https://github.com/loiccoyle
.. _@szsdk: https://github.com/szsdk
.. _@ArtemSmaznov: https://github.com/ArtemSmaznov
.. _@timsofteng: https://github.com/timsofteng
.. _@kAldown: https://github.com/kaldown
.. _@Yutsuten: https://github.com/Yutsuten
.. _@buzzingwires: https://github.com/buzzingwires
.. _@xfzv: https://github.com/xfzv
