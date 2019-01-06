#!/bin/bash

# Simple script to create the man page using sphinx

# First re-create the source code documentation
scripts/src2rst.py

# Then call sphinx to rebuild the man page
sphinx-build -b man docs misc/
