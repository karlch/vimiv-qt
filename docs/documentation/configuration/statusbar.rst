.. _statusbar:

#########
Statusbar
#########

In vimiv a statusbar at the bottom is used to display useful information.

The content of the statusbar is completely configurable and mode dependent. The
bar is grouped into three parts: left, center and right. Each part has a
fallback content and can have a mode-dependent content which overrides the
default. The content is defined in the ``STATUSBAR`` section of the
``vimiv.conf`` configuration file located in ``$XDG_CONFIG_HOME/vimiv/`` where
``$XDG_CONFIG_HOME`` is usually ``~/.config/*`` if you have not configured it.

The three default options are defined via:

* ``left = the content to display on the left``
* ``center = the content to display in the center``
* ``right = the content to display on the right``

And can be extended by adding options in the form of e.g.

*   ``left_image = content to display on the left in image mode``
*   ``center_thumbnail = content to display in the center in thumbnail mode``

Text you enter is displayed *as is*. Formatting using a subset of the html
styles is possible. As this is not very useful, vimiv provides a set of so
called ``modules`` for the statusbar. A module is indicated by surrounding its
name in curly braces, e.g. ``{pwd}``. This gets replaced by the output of the
module. A list of available modules can be found below.

.. include:: statusbar_modules.rstsrc
