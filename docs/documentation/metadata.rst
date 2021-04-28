Metadata
========

Vimiv provides optional metadata support if either `pyexiv2`_ or `piexif`_ is
available. If this is the case:

#. The ``:metadata`` command and the corresponding ``i``-keybinding is available.
#. Image metadata is automatically copied from source to destination when writing images
   to disk.
#. The ``{exif-date-time}`` statusbar module is available.

.. include:: pyexiv2.rst

Advantages of the different metadata libraries
----------------------------------------------

In short, `pyexiv2`_ is much more powerful than `piexif`_, though also more involved to
install.

.. table:: Comparison of the two libraries
   :widths: 20 15 20 45

   ======================= ============== ==================== =====================================================================
   PROPERTY                `piexif`_      `pyexiv2`_           Note
   ======================= ============== ==================== =====================================================================
   Exif Support            True           True                 pyexiv2 can extract way more data for the same image
   ICMP Support            False          True
   XMP Suppport            False          True
   Output Formatting       False          True                 e.g. ``FNumber: 63/10`` vs ``FNumber: F6.3``
   Supported File Types    JPEG, TIFF     All common types
   Ease of installation    Simple         More complicated     pyexiv2 requires some dependencies including the C++ library `exiv2`_
   ======================= ============== ==================== =====================================================================


We recommend to use `pyexiv2`_ if the installation is not too involved on your system
and `piexif`_ as a fallback solution or in case you don't need the full power of
`pyexiv2`_ and prefer something more lightweight.


Moving from piexif to pyexiv2
-----------------------------

As `pyexiv2`_ is the more powerful option compared to `piexif`_, vimiv will prefer
`pyexiv2`_ over `piexif`_. Therefore, to switch to `pyexiv2`_ simply install it on your
system and vimiv will use it automatically. If you have defined custom metadata sets in
your config, you may have to adjust them to use the full path to any key. See the next
section for more information on this.


Customizing metadata keysets
----------------------------

You can configure the information displayed by the ``:metadata`` command by adding your
own key sets to the ``METADATA`` section in your configfile like this::

    keys2 = Override,Second,Set
    keys4 = New,Fourth,Set

where the values must be a comma-separated list of valid metadata keys.

In case you are using `pyexiv2`_ you can find an overview of valid Exif, IPTC and XMP
keys on the `exiv2 webpage <https://www.exiv2.org/metadata.html>`_. It is considered
best-practice to use the full path to any key, e.g. ``Exif.Image.FocalLength``, but for convenience the short version of the key, e.g. ``FocalLength``, also works for the keys
in ``Exif.Image`` or ``Exif.Photo``.

`Piexif`_ unfortunately always uses the short form of the key, i.e. everything that
comes after the last ``.`` character. In case you pass the full path, vimiv will remove
everything up to and including the last ``.`` character and match only the short form.

On top of the library specific keys, vimiv also provides a series of additional
metadata keys. They can be treated completely equivalently to the library keys.

.. table:: Complete list of internal metadata keys
   :widths: 20 80

   ======================= =================================
   Key                     Description
   ======================= =================================
   ``Vimiv.FileSize``      File size
   ``Vimiv.FileType``      File type
   ``Vimiv.XDimension``    X dimension in pixel
   ``Vimiv.YDimension``    Y dimension in pixel
   ======================= =================================

You can get a list of valid metadata keys for the current image using the
``:metadata-list-keys`` command.


.. _exiv2: https://www.exiv2.org/index.html
.. _pyexiv2: https://python3-exiv2.readthedocs.io
.. _piexif: https://pypi.org/project/piexif/
