Changelog
=========

All notable changes to vimiv are documented in this file.


v0.4.0 (unreleased)
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

Changed:
^^^^^^^^

* External commands started with ``!`` no longer run in a sub-shell. To run commands
  with a sub-shell use ``:spawn`` instead.

Fixed:
^^^^^^

* Fuzzy path completion.
* Setting ``monitor_filesystem`` to ``false`` during runtime.
* Crash when entering command mode with ``{filesize}`` status module.
* XDG related directories such as XDG_CONFIG_HOME are created with mode 700 as expected
  by the XDG standard if they do not exist.
* Writing image changes on quit.
* Crash when running transform-related commands without valid pixmap.


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
