Getting Started
===============

You can start vimiv from any application launcher with its .desktop file or
from the command line using the ``vimiv`` command. If any valid image paths are
given, the images are opened directly, otherwise the library is opened.

To close vimiv press ``q`` or type in ``:q`` in the command line.

Vimiv is, as one would expect from an application with vim-like keybindings,
completely keyboard driven. To get you started some of the most important
keybindings for controlling vimiv are explained below. For a complete list of
them take a look at the ``keys.conf`` file which is generated upon startup in
``$XDG_CONFIG_HOME/vimiv/``.

Basics
------

Depending on how you started ``vimiv`` you will begin in image or in library
mode. To enter another mode the ``g`` key is combined with the first letter of
the mode. Therefore:

* ``gi`` enters image mode
* ``gl`` enters library mode
* ``gt`` enters thumbnail mode and
* ``gm`` enters manipulate mode.

To toggle a mode the same logic applies with the ``t`` key instead of the ``g``
key.

.. note:: Image mode cannot be toggled as it is the "normal" mode of vimiv

As in vim what a keybinding does depends on the mode in which it is ran.

Image
-----

Scrolling the image is done with ``hjkl``. The next image is selected with
``n``, the previous one with ``p``. To show the first/last image use ``gg/G``.

Zooming in and out is done with ``+/-``. To fit the image to the current window
size use ``w``. ``e/E`` fit horizontally/vertically.

To start playing a slideshow use ``ss``. The delay can be decreased/increased
using ``sh/sl``.

Library
-------

The behaviour of the library is similar to the one of the file manager
`ranger <https://ranger.github.io/>`_.
You can scroll down/up with ``j/k``. ``gg/G`` select the first/last file in the
list. ``h`` opens the parent directory while ``l`` selects the current file. If
the file is a directory, it is opened in the library. An image is displayed to
the right of the library. Pressing ``l`` again closes the library and focuses
the image.

Thumbnail
---------

Once again ``hjkl`` and ``gg/G`` work as expected.

It is also possible to vary the size of the thumbnails with the ``+/-`` keys.

To open the selected thumbnail in image mode, press ``<return>``.

Image Editing
-------------

Images can be rotated with the ``<`` and ``>``, flipped with the ``|`` and
``_`` keys. These
changes are automatically applied to the file as long as the ``image.autowrite``
setting is true. An image is deleted with x. This actually moves the image to
the trash directory specified by the freedesktop standard, by default
$XDG_DATA_HOME/Trash.

For additional editing enter manipulate mode. Here brightness and contrast can
be changed. To change between the manipulations use the ``bc`` keys. Values
between -127 and 127 are valid. To increase the value by 1/10 use ``k/K``, to
decrease it by 1/10 use ``j/J``. To apply the changes accept with ``<return>``,
to leave manipulate mode reverting any changes press ``<escape>``.

Command Line
------------

Similar to many keyboard centric programs, vimiv includes a simple commmand
line to run commands. It is opened with ``:`` and closed with ``<return>`` to
run a command and ``<escape>`` to discard it.

When entering the command line a completion window for vimiv’s commands is
displayed. Pressing ``<tab>`` starts cycling through the completions.
``<shift><tab>`` cycles in inverse direction.

Opening new paths from here is done using the ``:open`` command. Path
completion is also supported.

Prepending a command with ``!`` lets vimiv interpret the command as an external
command. The following text is passed to the shell. Here ``%`` is replaced with the
currently selected file and unix style pattern matching including ``*`` and ``?`` can be
used. Recursive matching is also possible using ``**`` but please note that this can
become slow in large directory trees.
Example: ``:!gimp %`` opens the currently selected image in gimp.

External commands can be "piped to vimiv" by appending the ``|`` char to the
command. The output of the command is then parsed by vimiv. If the first line
out output is a directory, it is opened in the library. If it is a valid image,
all lines are checked for images and these are opened.

Example: ``:!find ~/Images -ctime -5 -type f |`` opens all files in
``~/Images`` younger than five days.

Command line history is saved to ``$XDG_DATA_HOME/vimiv/history``. History can
be navigated and searched through using the ``<control>p/<control>n`` and
``<up>/<down>`` keys.

Count
-----

Some commands support passing a ``[count]`` as repetition or step. To pass a
count in the command line, prepend ``[count]`` to the command, e.g. ``:5next``.
Pressing any number appends it to the current ``[count]`` and the next command
is run with the stored ``[count]``.

What Next?
----------

You may want to check out how to :doc:`configure <configuration/index>` vimiv
or take a look at a :doc:`description of all commands <commands>`.
