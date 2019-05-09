#######
Plugins
#######

Vimiv provides the option to extend its functionality with python module plugins. To add
a new plugin:

#. Put the python module into the plugins folder ``$XDG_DATA_HOME/vimiv/plugins/``.
#. Activate it in the ``PLUGINS`` section of the configuration file by adding:
   ``plugin_name = any additional information`` where ``plugin_name`` is the name of the
   python module added.

Currently the following user plugins are available:

* None, waiting for your plugin :)

In addition to plugins that can be added by the user, vimiv ships with a few default
plugins that can be activated:

.. include:: default_plugins.rstsrc
