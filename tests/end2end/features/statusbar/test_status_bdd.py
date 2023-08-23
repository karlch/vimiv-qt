# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

import pytest_bdd as bdd


bdd.scenarios("status.feature")


@bdd.then("the image should have mouse tracking")
def check_image_tracks_mouse(image):
    assert image.hasMouseTracking()
