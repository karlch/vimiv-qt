#!/bin/bash

# Simple script to create the html website using sphinx

# First re-create the source code documentation
scripts/src2rst.py

# Then call sphinx to rebuild the website
# I keep the gh_pages repository cloned in a directory next to the main
# repository and build the website there
WEBSITEDIR="../VimivQtWebsite"
sphinx-build -b html docs $WEBSITEDIR
