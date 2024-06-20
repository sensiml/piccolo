import pytest
import sys, os


def test_valid(request, proxy, server, SensiMLImport):
    dsk = SensiMLImport(
        server=server,
        username="piccolo@sensiml.com",
        password="TinyML4Life",
        insecure=True,
        path=os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "../", "connect.cfg"
        ),
    )
    dsk.logout()


def test_username_invalid(request, proxy, server, SensiMLImport):
    with pytest.raises(Exception):
        dsk = SensiMLImport(
            server=server,
            username="unittestsdfd_bad@intel.com",
            password="TinyML4Life",
            insecure=True,
            path=os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "../", "connect.cfg"
            ),
        )
        dsk.logout()


def test_password_invalid(request, proxy, server, SensiMLImport):
    with pytest.raises(Exception):
        dsk = SensiMLImport(
            server=server,
            username="piccolo@sensiml.com",
            password="inteltest_bad_pass",
            insecure=True,
            path=os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "../", "connect.cfg"
            ),
        )
        dsk.logout()


def test_only_valid_username(request, proxy, server, SensiMLImport):
    with pytest.raises(Exception):
        dsk = SensiMLImport(
            server=server,
            username="piccolo@sensiml.com",
            password="",
            insecure=True,
            path=os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "../", "connect.cfg"
            ),
        )
        dsk.logout()


def test_only_valid_password(request, proxy, server, SensiMLImport):
    with pytest.raises(Exception):
        dsk = SensiMLImport(
            server=server,
            username="",
            password="inteltest",
            insecure=True,
            path=os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "../", "connect.cfg"
            ),
        )
        dsk.logout()


def test_valid_login_again(request, proxy, server, SensiMLImport):
    dsk = SensiMLImport(
        server=server,
        username="piccolo@sensiml.com",
        password="TinyML4Life",
        insecure=True,
        path=os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "../", "connect.cfg"
        ),
    )
