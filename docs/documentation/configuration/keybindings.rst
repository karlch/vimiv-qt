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
bind ``f : flip``. To remove a default keybinding via ``keys.conf``, map the key to
``unbind``. In case you would like to enforce a keybinding to do nothing, for example to
remove a default Qt binding, use ``nop`` instead. ``:nop`` is a regular vimiv command
that does nothing.

.. note::

   When binding a command including the "%" wildcard which stands for the current file,
   it must be escaped as "%%" as "%" `is treated specially by the python ConfigParser
   <https://docs.python.org/3/library/configparser.html#interpolation-of-values>`_.
   Special care should be taken if paths could include whitespace as these get escaped
   using single quotes to a path of the form 'path with space.jpg'. These single quotes
   should not clash with other single quotes in the binding. We therefore recommend
   using double quotes for keybindings that include wildcards as needed.

It is also possible to bind mouse clicks and double clicks. The relevant names are
``<button-NAME>`` and ``<double-button-NAME>``. Here ``NAME`` stands for the name of the
mouse button to bind, e.g. ``left``, ``middle`` or ``right``.

.. hint::

    If you want to figure out the name of a specific key or mouse button, run vimiv with
    ``--debug gui.eventhandler``. You can find the corresponding name in the first
    output line after pressing/clicking it. For example, when pressing the ``q`` key,
    you would retrieve something along::

        DEBUG    <gui.eventhandler>   EventHandlerMixin: handling q for mode library

The following table lists all default keybindings.

.. include:: keybindings_table.rstsrc
