# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

import pytest

import pytest_bdd as bdd


bdd.scenarios("gif.feature")


@pytest.fixture()
def movie(image):
    widget = image.items()[0].widget()
    return widget.movie()


@bdd.then("the animation should be playing")
def check_animation_playing(movie):
    assert movie.state() == movie.MovieState.Running


@bdd.then("the animation should be paused")
def check_animation_paused(movie):
    assert movie.state() == movie.MovieState.Paused
