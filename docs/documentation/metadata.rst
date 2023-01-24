Metadata
========

Vimiv provides optional metadata support. If enabled, then:

#. The ``:metadata`` command and the corresponding ``i``-keybinding is available. It
   displays the metadata of the current image.
#. The ``{exif-date-time}`` statusbar module is available. It displays the Exif
   creation time of the current image.
#. Metadata is automatically copied from source to destination when writing images to
   disk.

Vimiv provides full flexibility to users in terms of what metadata backend to use.
Each backend comes with their advantages and disadvantages, and each user has different
requirements, as well as different package support. Therefore, Vimiv provides metadata
backends as independent plugins, that can be loaded as one desires. In addition, users
have the ability to extend Vimiv's metadata capabilities using
:ref:`custom plugins<Plugins>`, as described in
:ref:`a later section<create_own_metadata_plugins>`.

Vimiv comes with two default plugins:

* ``metadata_piexif`` is based on `piexif`_
* ``metadata_pyexiv2`` is based on `pyexiv2`_

In addition, there are the following user metadata plugins available:

.. table:: Overview of user plugins
   :widths: 20 80

   ======================================================== ===========
   Name                                                     Description
   ======================================================== ===========
   ======================================================== ===========


Enabling metadata plugins
-------------------------

Metadata plugins are loaded as any other Vimiv plugin. To enable one of the default
plugins, simply list its name in the ``PLUGINS`` section of the configuration file. In
addition, you need to ensure that the required backend is installed on your system.

To enable a user metadata plugin, first you need to download it, and put it into the
plugin folder. Only then you can load it, similarly to the default plugins.

For more information on how to load plugins, please refer to the
:ref:`plugin section<Plugins>`.


Advantages of the different metadata plugins
--------------------------------------------

In short, ``metadata_pyexiv2`` is much more powerful than ``metadata_piexif``, though
the dependencies are also more involved to install.

.. table:: Comparison of the two libraries
   :widths: 20 15 20 45

   ======================= =================== ==================== =====================================================================
   PROPERTY                ``metadata_piexif`` ``metadata_pyexiv2`` Note
   ======================= =================== ==================== =====================================================================
   Backend                 `piexif`_           `pyexiv2`_
   Exif Support            True                True                 pyexiv2 can potentially extract more data for the same image
   ICMP Support            False               True
   XMP Suppport            False               True
   Output Formatting       False               True                 e.g. ``FNumber: 63/10`` vs ``FNumber: F6.3``
   Supported File Types    JPEG, TIFF          Many common types
   Ease of installation    Simple              More complicated     pyexiv2 requires some dependencies including the C++ library `exiv2`_
   ======================= =================== ==================== =====================================================================

We recommend to use ``metadata_pyexiv2`` if the installation of `pyexiv2`_ is not too
involved on your system and ``metadata_piexif`` as a fallback solution or in case you
don't need the full power of `pyexiv2`_ and prefer something more lightweight.


Customizing metadata keysets
----------------------------

You can configure the information displayed by the ``:metadata`` command by adding your
own key sets to the ``METADATA`` section in your configfile like this::

    keys2 = someKey,anotherOne,lastOne
    keys4 = newKey,oneMore

where the values must be a comma-separated list of valid metadata keys.

In case you are using `pyexiv2`_, you can find a complete overview of valid keys on the
`exiv2 webpage <https://www.exiv2.org/metadata.html>`_. You can choose any of the Exif,
IPTC, or XMP keys.

`Piexif`_ uses a simplified form of the key. It does not use the ``Group.Subgroup``
prefix, which is present in each of `pyexiv2`_'s keys. However, ``metadata_piexif``
automatically does this truncation, if the provided keys are in the long form.

The ``:metadata-list-keys`` command provides a list of all valid metadata keys, that
the currently loaded metadata plugins can read. This serves as an easy way to see what
keys are available in the image.


.. _create_own_metadata_plugins:

Create own metadata plugin
--------------------------

One can extend Vimiv's metadata capabilities by creating own metadata plugins. This is
for example useful, if you want to use a different metadata backend.

The rough steps are the following:

#. Create a plugin, that implements the abstract class
   ``vimiv.imutils.metadata.MetadataPlugin``

   #. Implement all required methods

   #. Optionally, also implement the non-required methods

#. In the plugin's init function, register the plugin using
   ``vimiv.imutils.metadata.register``

Please see the default metadata plugins for an example implementation.


.. _exiv2: https://www.exiv2.org/index.html
.. _pyexiv2: https://python3-exiv2.readthedocs.io
.. _piexif: https://pypi.org/project/piexif/
