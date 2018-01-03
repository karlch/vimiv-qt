#!/bin/bash

files=$*

sed -i '2s/^/\
# This file is part of vimiv.\
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>\
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.\
/' ${files}
