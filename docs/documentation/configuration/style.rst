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

A bunch of base16 styles to pick from are available in the
`base16-vimiv repository <https://github.com/karlch/base16-vimiv>`_.

Creating your own style is easy:

#. Create a new file in the ``styles`` directory. The file must start with the
   ``[STYLE]`` header.
#. Define the colors ``base00`` to ``base0f``. This is required as these colors are
   referenced by the individual options.
#. Change the ``style`` setting in the ``vimiv.conf`` file to the name of your newly
   created file.
#. Optional: override any other option such as the global ``font`` or individual
   settings like ``thumbnail.padding``.

.. hint:: Refer to the created default style for all available options

.. hint:: Defined style options can be referenced via ``new_option = {other_option}``,
   for example to use a different base color for mark-related things you can use
   ``mark.color = {base0a}``.

.. hint:: As for settings, you can refer to
    :ref:`external resources <external_resources>`.

.. hint:: The python configparser module is not case sensitive. Therefore it is
   a good idea to keep all your style options in lower case.
