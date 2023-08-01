.. _plugins:

Plugins
=======

Vimiv provides the option to extend its functionality with python module plugins. To add
a new plugin:

#. Put the python module into the plugins folder ``$XDG_DATA_HOME/vimiv/plugins/``.
#. Activate it in the ``PLUGINS`` section of the configuration file by adding:
   ``plugin_name = any additional information`` where ``plugin_name`` is the name of the
   python module added and ``any additional information`` is passed on to the plugin
   upon startup. Plugins can decide to use this information string for anything they
   like.

Currently the following user plugins are available:

.. table:: Overview of user plugins
   :widths: 20 80

   ======================================================== ===========
   Name                                                     Description
   ======================================================== ===========
   `RawPrev <https://github.com/jcjgraf/RawPrev>`_          Raw support based on ``dcraw`` instead of `qt raw <https://gitlab.com/mardy/qtraw>`_
   `Importer <https://github.com/jcjgraf/Importer>`_        Easily import your images from a SD card, camera or any directory into your photo storage
   `BatchMark <https://github.com/jcjgraf/BatchMark>`_      Easily mark contiguous images
   `Video <https://github.com/jcjgraf/Video>`_              List videos within vimiv and play them using an external player
   ======================================================== ===========

If you would like to write a plugin, some of the information on :ref:`writing_plugins`
may be helpful to get started.

In addition to plugins that can be added by the user, vimiv ships with a few default
plugins that can be activated:

.. include:: default_plugins.rstsrc

imageformats
^^^^^^^^^^^^

Activate this plugin by adding ``imageformats = name, ...`` to the plugins section of
your ``vimiv.conf``. Here ``name, ...`` consists of the names of the image formats to
add separated by a comma.

Currently the following formats are supported:

* cr2 (requires `qt raw <https://gitlab.com/mardy/qtraw>`_)
* avif (requires `qt-avif-image-plugin <https://github.com/novomesk/qt-avif-image-plugin>`_)
