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
``$XDG_CONFIG_HOME/vimiv/`` or open the keybindings pop-up by running ``:keybindings``.

You can run ``:help topic`` to get some additional information on a specific topic.
Completion will guide you through the different options like commands and settings.

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

Images can be rotated with the ``<`` and ``>``, flipped with the ``|`` and ``_`` keys.
These changes are automatically applied to the file as long as the ``image.autowrite``
setting is true. An image is deleted with ``x``. This actually moves the image to the
trash directory specified by the freedesktop standard, by default $XDG_DATA_HOME/Trash.

For additional editing enter manipulate mode with ``gm``. Here you can change brightness
and contraste as well as hue, saturation and lightness. To increase the current
manipulation by 1/10 use ``k/K`` or ``l/L``. Correspondingly, to decrease it by 1/10 use
``j/J`` or ``h/H``. To set it to a specific value you can press ``[count]gg``.

Navigating between the manipulations in the current tab is done with ``n/p``. To get to
the next/previous tab press ``<tab>/<shift><tab>``.

When you are satisfied and want to apply the changes, accept with ``<return>``. If you
prefer to leave discarding the changes, press ``<escape>``.

.. _commandline:

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

Unix style pattern matching including ``*`` and ``?`` can be used. Recursive matching is
also possible using ``**`` but please note that this can become slow in large directory
trees. In addition ``%`` gets replaced with the currently selected file and ``%m`` by
all marked images. See :ref:`marks_and_tags` for more information on this.

Prepending a command with ``!`` lets vimiv interpret the command as an external
command. This becomes especially useful in combination with the patterns described
above.

Example: ``:!gimp %`` opens the currently selected image in gimp.

External commands can be "piped to vimiv" by appending the ``|`` char to the
command. The output of the command is then parsed by vimiv. If the first line
out output is a directory, it is opened in the library. If it is a valid image,
all lines are checked for images and these are opened.

Example: ``:!find ~/Images -ctime -5 -type f |`` opens all files in
``~/Images`` younger than five days.

.. note::

    External commands started with ``!`` do not run in a sub-shell for security and
    performance reasons. This means that redirection with ``|`` or ``>`` as well as any
    other shell specifics do not work. If you require to run with a sub-shell, use the
    ``:spawn`` command instead.

Command line history is saved to ``$XDG_DATA_HOME/vimiv/history``. History can
be navigated and searched through using the ``<control>p/<control>n`` and
``<up>/<down>`` keys.

Count
-----

Some commands support passing a ``[count]`` as repetition or step. To pass a
count in the command line, prepend ``[count]`` to the command, e.g. ``:5next``.
Pressing any number appends it to the current ``[count]`` and the next command
is run with the stored ``[count]``.

.. _marks_and_tags:

Marks and Tags
--------------

Images supports the concept of marking images using the ``:mark`` command. As an
argument it takes an arbitrary number of paths and supports pattern matching as
described in :ref:`commandline`. The current image is therefore marked using ``:mark %``
which is bound to ``m`` by default. Working with the set of marked images is done by
referencing them in the command line with ``%m``.

Example: ``:!mogrify -rotate 90 %m`` rotates all marked images by 90 degrees using the
``mogrify`` command from `imagemagick <https://imagemagick.org/index.php>`_.

All current marks are removed by running ``:mark-clear``. The last set of cleared marks
can be restored using ``:mark-restore``.

To keep a selection of marks and assigning them a name, tags can be used. New tags are
created using ``:tag-write my_fancy_tag``. Grouping into sub-directories is possible by
naming the tags accordingly, e.g. ``:tag-write favourites/2017``. Under the hood, this
creates a tag file in ``$XDG_DATA_HOME/vimiv/tags`` which is a simple text file that can
be parsed as usual.

.. hint::

   When writing to a tag that exists, all currently marked images that are not in
   the tag yet are appended to it.

Loading a tag is done with ``:tag-load my_fancy_tag`` which loads all images from the
tag into the list of marked images. To then open them in image mode we can refer to them
with ``%m`` in the open command: ``:open %m``.

Deleting a tag is done with ``:tag-delete my_fancy_tag``.

.. warning:: This deletes the tag permanently with no option to restore it!

What Next?
----------

You may want to check out how to :doc:`configure <configuration/index>` vimiv
or take a look at a :doc:`description of all commands <commands>`.
