# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

import configparser

from vimiv.config import configfile, keyfile


def test_dump_configfile(mocker, tmpdir):
    # Dump
    f = tmpdir.join("vimiv.conf")
    mocker.patch("vimiv.utils.xdg.join_vimiv_config", return_value=str(f))
    configfile.dump()
    # Read with configparser
    parser = configparser.ConfigParser()
    parser.read(str(f))
    # Check a few values
    assert "GENERAL" in parser
    assert parser["STATUSBAR"].getboolean("show") is True


def test_dump_keyfile(mocker, tmpdir):
    # Dump
    f = tmpdir.join("keys.conf")
    mocker.patch("vimiv.utils.xdg.join_vimiv_config", return_value=str(f))
    keyfile.dump()
    # Read with configparser
    parser = keyfile.KeyfileParser()
    parser.read(str(f))
    # Check a few values
    assert "GLOBAL" in parser
    assert "IMAGE" in parser
