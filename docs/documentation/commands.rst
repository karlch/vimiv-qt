########
Commands
########

In vimiv all keybindings are mapped to commands.

Most of the commands can also be run from the command line but some are hidden
as they are not useful to run by hand. A typical example is the ``:command``
command which enters the command line.

Every command is limited to its mode. This allows commands with equal names to
do different things depending on the mode they are run in. For example the
``:zoom`` command rescales the image in ``image`` mode but changes the size of
thumbnails in ``thumbnail`` mode. This also prevents running commands that are
useless in the current mode. Commands available in the special ``global`` mode
can be run in ``image``, ``library`` and ``thumbnail`` mode.

Below is a complete list of all commands in every mode.

.. include:: commands_desc.rstsrc
