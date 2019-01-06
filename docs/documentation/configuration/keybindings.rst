###########
Keybindings
###########

Vimiv provides configurable keybindings. The default keybindings are written
to the ``$XDG_CONFIG_HOME/vimiv/keys.conf`` on first start where
``$XDG_CONFIG_HOME`` is usually ``~/.config/`` if you have not updated it.

The configuration file is structured into sections. Each section corresponds to
the mode in which the keybindings arevalid. In each section the keybindings are
defined using ``keybinding : command to bind to``. Therefore ``f : fullscreen``
maps the ``f`` key to the ``fullscreen`` command. Special keys like space must
be wrapped in tags in the form of ``<space>`` to allow to differentiate them
from sequences of normal keys.

There are two ways to add a new keybinding:

* Update the configuration file by adding the binding to the appropriate mode
  to change it permanently
* Run the ``:bind`` command to add it temporarily

If you wish to replace a default keybinding, add a the new keybinding that
overrides it. For example to replace the ``f : fullscreen`` binding with flip,
bind ``f : flip``. To remove a default keybinding, map the key to the special
``nop`` command that does nothing.

The following table lists all default keybindings.

.. include:: keybindings_table.rstsrc
