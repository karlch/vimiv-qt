# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

import pytest_bdd as bdd


bdd.scenarios("teardown.feature")


@bdd.when("I quit the application")
def quit_application(qapp):
    qapp.aboutToQuit.emit()
