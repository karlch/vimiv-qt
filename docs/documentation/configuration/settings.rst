########
Settings
########

Vimiv provides configurable settings.

There are two ways to change a setting:

* Update the configuration file to change it permanently
* Run the ``:set`` command to change it temporarily

The configuration file is ``$XDG_CONFIG_HOME/vimiv/vimiv.conf`` where
``$XDG_CONFIG_HOME`` is usually ``~/.config/`` if you have not updated it.

.. _external_resources:

Referring to external resources
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the configuration file, it is possible to refer to external resources using the
``option = ${RESOURCE:variable}``
syntax. Here ``RESOURCE`` defines the type of external resource, and ``variable`` is the
corresponding variable name. The following options are available:

* ``${env:VARIABLE}`` to retrieve the value of the environment variable ``$VARIABLE``

Overview of all settings
^^^^^^^^^^^^^^^^^^^^^^^^

The following table explains all available settings.

.. include:: settings_table.rstsrc
