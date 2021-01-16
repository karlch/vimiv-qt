Exif
====

Vimiv provides optional exif support if either `pyexiv2`_ or `piexif`_ is available. If
this is the case:

#. Exif metadata is automatically copied from source to destination when writing images
   to disk.
#. The ``:metadata`` command and the corresponding ``i``-keybinding is available.
#. The ``{exif-date-time}`` statusbar module is available.


Advantages of the different exif libraries
------------------------------------------

`Pyexiv2`_ is the more powerful of the two options. One large advantage is that it has
the option to format exif data into human readable format, for example ``FocalLength:
5.0 mm`` where `piexif`_ would only give ``FocalLength: 5.0``. However, given it is
written as python bindings to the c++ api of `exiv2`_, the installation is more involved
compared to the pure python `piexif`_ module.

We recommend to use `pyexiv2`_ if the installation is not too involved on your system
and `piexif`_ as a fallback solution or in case you don't need the full power of
`pyexiv2`_ and prefer something more lightweight.


Moving from piexif to pyexiv2
-----------------------------

As pyexiv2 is the more powerful option compared to piexif, vimiv will prefer pyexiv2
over piexif. Therefore, to switch to pyexiv2 simply install it on your system and vimiv
will use it automatically.


Finding valid metadata keys
---------------------------

You can configure the information displayed by the ``:metadata`` command by adding your
own key sets to the ``METADATA`` section in your configfile like this::

    keys2 = Override,Second,Set
    keys4 = New,Fourth,Set

where the values must be a comma-separated list of valid metadata keys.

In case you are using `pyexiv2`_ you can find a complete overview of valid keys on the
`exiv2 webpage <https://www.exiv2.org/metadata.html>`_. It is considered best-practice
to use the full path to any key, e.g. ``Exif.Image.FocalLength``, but for convenience
the short version of the key, e.g. ``FocalLength``, also works for the keys in
``Exif.Image`` or ``Exif.Photo``.

`Piexif`_ unfortunately always uses the short form of the key, i.e. everything that
comes after the last ``.`` character.

Once `issue #220 <https://github.com/karlch/vimiv-qt/issues/220>`_ has been implemented,
you will be able to get a list of valid metadata keys for the current image using
``:metadata --list-keys``.


.. _exiv2: https://www.exiv2.org/index.html
.. _pyexiv2: https://pypi.org/project/pyexiv2/
.. _piexif: https://pypi.org/project/piexif/
