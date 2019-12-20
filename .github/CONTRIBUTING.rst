Contributing Guidelines
=======================

You want to contribute to vimiv? Great! Every little help counts and is appreciated!

Need help? Feel free to `contact me directly <karlch@protonmail.com>`_
or open an
`issue on github <https://github.com/karlch/vimiv-qt/issues/>`_.

.. contents::

Feedback and Feature Requests
-----------------------------

Any feedback is welcome! Did you find something unintuitive? Not clearly documented? Do
you have a great idea for a new feature? Let me know!  You can either open an
`issue directly on github <https://github.com/karlch/vimiv-qt/issues/>`_
or `contact me directly <karlch@protonmail.com>`_ if you prefer.

You like vimiv? Share some love and spread the word!

Reporting Bugs
--------------

The best way to report bugs is to open an `issue on github
<https://github.com/karlch/vimiv-qt/issues/>`_. If you do not have a github account,
feel free to `contact me directly <karlch@protonmail.com>`_. If possible, please
reproduce the bug running ``vimiv --log-level debug`` and include the log file located
in ``$XDG_DATA_HOME/vimiv/vimiv.log`` where ``$XDG_DATA_HOME`` is usually
``~/.local/share/`` if you have not configured it.

Writing Code
------------

You probably already know what you want to work on as you are reading this
page. If you want to implement a new feature, it might be a good idea to open a
feature request on the `issue tracker
<https://github.com/karlch/vimiv-qt/issues/>`_ first. Otherwise you might be
disappointed if I do not accept your pull request because I do not feel like
this should be in the scope of vimiv.

If you want to find something to do, check the
`issue tracker <https://github.com/karlch/vimiv-qt/issues/>`_. Some hints:

* `Issues that are good for newcomers <https://github.com/karlch/vimiv-qt/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22>`_
* `Issues that require help <https://github.com/karlch/vimiv-qt/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22>`_
* `Issues that do not involve coding <https://github.com/karlch/vimiv-qt/issues?q=is%3Aissue+is%3Aopen+label%3Anot-code>`_

As this is my first larger project, comments and improvements to the existing
code base are more than welcome.

`writing plugins <https://karlch.github.io/vimiv-qt/documentation/hacking#writing-plugins>`_
is also a great option without having to work with the vimiv
codebase. For some inspiration you could take a look at
`issues that could be realized using plugins <https://github.com/karlch/vimiv-qt/issues?q=is%3Aissue+is%3Aopen+label%3Aplugin>`_.

If you prefer C over python, you may be interested in implementing
`additional manipulations in the C extension <https://github.com/karlch/vimiv-qt/issues/7>`_.
Some useful tips on how you can do this can be found
`here <https://karlch.github.io/vimiv-qt/documentation/hacking#adding-new-manipulations-to-the-c-extension>`_.

If you like, you can also find some more information on 
`hacking the source code <https://karlch.github.io/vimiv-qt/documentation/hacking>`_.

Writing Documentation
---------------------

More documentation is always useful! Here are some options where this could be done:

* Improving the website. Is something unclear or missing?
* Extending and improve the docstrings in the code base.
* Writing blog posts, articles, ... All of them are appreciated! If you like, they can
  also be linked here.

In case you chose to update the website, here are some more tips.
The website is written in
`resturctured Text (reST) <https://en.wikipedia.org/wiki/ReStructuredText>`_
and built using
`sphinx <http://www.sphinx-doc.org/en/master/>`_.
A great introduction is given by the
`reST Primer of sphinx <http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`_.

You can find the reST files used to build the website in the project's ``docs`` folder.
If you would like to build a local copy, you can run::

    tox -e docs -- path/to/copy

You can then browse your local build::

    $BROWSER path/to/copy/index.html
