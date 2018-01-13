Style
=====
There are two default styles: a light and a dark one. They are both based upon
`base16 tomorrow <https://github.com/chriskempson/base16-tomorrow-scheme>`_,
the dark one using tomorrow night. To switch between them, set the ``style``
setting in the ``vimiv.conf`` file to ``default`` or ``default-dark``
respectively.

The style files of the default styles are written to the ``styles`` directory
on startup if they do not exist.  The styles directory is located in
``$XDG_CONFIG_HOME/vimiv/`` where ``$XDG_CONFIG_HOME`` is usually
``~/.config/`` if you have not updated it.

You can implement your own style by copying a default file in the ``styles``
directory, configuring it to your liking, and changing the ``style`` setting in
the ``vimiv.conf`` file to the name of the new file.

As the default files show, it is possible to define variables and referencing
them afterwards. Say you define ``red = #ff0000`` and you would like the
statusbar text to be red. You can then reference it via
``statusbar.fg = {red}``.

.. warning:: Your style **MUST** implement **ALL** of the variables defined
   in the default style. Not doing so leads to undefined behaviour as the
   corresponding style of the Qt Widget will be left empty.

.. hint:: The python configparser module is not case sensitive. Therefore it is
   a good idea to keep all your styles in lower case.
