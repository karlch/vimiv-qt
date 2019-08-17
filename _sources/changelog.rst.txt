Changelog
=========

All notable changes to vimiv are documented in this file.


v0.2.0 (unreleased)
-------------------

Added:
^^^^^^

* A global ``font`` style option to set all fonts at once. If a local option such as
  ``statusbar.font`` is defined, it overrides the global option.

Changed:
^^^^^^^^

* All styles are now based upon base16. Therefore custom styles must define the colors
  ``base00`` to ``base0f``. All other style options are optional.

Fixed:
^^^^^^

* Elided text is now calculated correctly in the library.
* Setting value completions are no longer appended to the existing suggestions when the
  setting is changed
* Overlay widgets are always raised in addition to shown ensuring them to be visible.


v0.1.0 (2019-08-15)
-------------------

Initial release of the Qt version.
