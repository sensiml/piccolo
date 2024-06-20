import ssl

ssl._create_default_https_context = getattr(ssl, "_create_unverified_context", None)
import requests
import pytest

LOGIN_URL = "/oauth/token/"


def test_valid(server_url, user, password, proxy, oauth):
    print(user)
    payload = {"username": user, "password": password}
    payload.update(oauth)
    r = requests.post(
        url=server_url + LOGIN_URL, data=payload, proxies=proxy, verify=False
    )
    assert r.status_code == 200


def test_only_username(server_url, user, password, proxy, oauth):
    payload = {"username": user}
    payload.update(oauth)
    r = requests.post(
        url=server_url + LOGIN_URL, data=payload, proxies=proxy, verify=False
    )
    assert 400 <= r.status_code <= 499


def test_only_password(server_url, user, password, proxy, oauth):
    payload = {"password": password}
    payload.update(oauth)
    r = requests.post(
        url=server_url + LOGIN_URL, data=payload, proxies=proxy, verify=False
    )
    assert 400 <= r.status_code <= 499


def test_bad_username(server_url, user, password, proxy, oauth):
    payload = {"username": "cookiesare#1", "password": password}
    payload.update(oauth)
    r = requests.post(
        url=server_url + LOGIN_URL, data=payload, proxies=proxy, verify=False
    )
    assert 400 <= r.status_code <= 499
    # assert r.text == 'Authentication failed. Please check your username and password.'


def test_bad_password(server_url, user, password, proxy, oauth):
    payload = {"username": user, "password": "cookiesarenot#!"}
    payload.update(oauth)
    r = requests.post(
        url=server_url + LOGIN_URL, data=payload, proxies=proxy, verify=False
    )
    assert 400 <= r.status_code <= 499
    # assert r.text == 'Authentication failed. Please check your username and password.'


def test_bad_client_secret(server_url, user, password, proxy, oauth):
    payload = {"username": user, "password": password}
    payload.update(oauth)
    payload["client_secret"] = "baddddddd"
    r = requests.post(
        url=server_url + LOGIN_URL, data=payload, proxies=proxy, verify=False
    )
    assert 400 <= r.status_code <= 499


def test_bad_client_id(server_url, user, password, proxy, oauth):
    payload = {"username": user, "password": password}
    payload.update(oauth)
    payload["client_id"] = "baddddddd"
    r = requests.post(
        url=server_url + LOGIN_URL, data=payload, proxies=proxy, verify=False
    )
    assert 400 <= r.status_code <= 499
