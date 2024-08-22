"""
Copyright 2017-2024 SensiML Corporation

This file is part of SensiML™ Piccolo AI™.

SensiML Piccolo AI is free software: you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License
as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

SensiML Piccolo AI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with SensiML Piccolo AI. If not, see <https://www.gnu.org/licenses/>.
"""

try:
    from http.cookiejar import CookiePolicy
except ImportError:
    from cookielib import CookiePolicy
from typing import Optional
import errno
import json as JSON
import logging
import os
import re
from datetime import datetime, timezone
from functools import partial
from getpass import getpass

import requests
from appdirs import user_config_dir
from oauthlib.oauth2 import (
    InvalidGrantError,
    LegacyApplicationClient,
    MissingTokenError,
    TokenExpiredError,
)
from requests_oauthlib import OAuth2Session
from six.moves import input

from .connection_config import ConnectionConfig

try:
    import configparser as ConfigParser
except:
    import ConfigParser

from .errors import LoginAttemptsExceededError

logger = logging.getLogger(__name__)

# Get configuration directory
config_dir = user_config_dir(__name__.split(".")[0], False)

cid = "qQ3hZ1VIn8xsHIg4ci5Kugyfj68SrJGi2pJM2rPt"
csid = "0W1wyEPLzTt38Zdq0Ky2odibE2KTWs7vHwzqBDoO9pU97Bp764BEBAlmDXX28dCPloDx0hcjMKBaPJTyH2jYEZ80sHeIX9SsMIvIcGnRcqcbHIyxSA96mDeSQJ7tKjh2"


class Warnings:
    insecure_warning = "You have chosen to disable certificate verification. Your connection is not secure!"


class Connection(object):
    """Connection class"""

    def __init__(
        self,
        server: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        oauth2_primary: bool = True,
        api_key: Optional[str] = None,
        debug: bool = False,
        **kwargs,
    ):
        """Create Connection object

        Args:
            oauth2_primary (bool, required): oauth2 | api_key
            server (str, optional): Server URL or name in config file.
            username (str, optional)
            password (str, optional)
            api_key (str, optional)
            debug (bool, False): adds additional print statements to see url information
            **kwargs (optional): Mostly used when passing `server` as URL. See below.

        Keyword Args:
            insecure (bool): Whether or not to require valid SSL/TLS in requests
            path (str, optional): When specifying a server name instead of a URL, the path of the config file.
            server_name (str, optional): user-readable name of server. defaults to the server domain.
            url (str, optional): Alternative name for server argument.
            auth_url (str, optional): URL of the oauth server. Defaults to server url.

        """
        # Check url parameter to allow direct passing of ConnectionConfig instances

        server = server or kwargs.get("url")
        if re.match(r"^https?://", server):
            self.server_url = re.sub(r"([^/])$", r"\1/", server)
            self.server_name = re.sub(r"^https?://([A-Za-z0-9.\-_]+).*$", r"\1", server)
            self.auth_url = kwargs.pop("auth_url", self.server_url)
            self.client_id = cid
            self.client_secret = csid
            self.username = username
        else:
            path = kwargs.pop("path", "connect.cfg")
            config = ConnectionConfig(server)
            try:
                config.load_from_file(path)
            except ConfigParser.NoSectionError:
                config.create_config_object(path)

            self.server_name = config.server
            self.server_url = config.url
            self.auth_url = config.auth_url
            self.client_id = cid
            self.client_secret = csid
            self.username = username

        self.debug = debug
        self.session = None
        self.token_url = self.auth_url.rstrip("/") + "/token/"
        self.max_retries = kwargs.pop("max_retries", 3)

        self._token_filename = os.path.join(
            config_dir, f"{self.server_name}_token.json"
        )

        try:
            self._token_last_updated = os.path.getmtime(self._token_filename)
        except OSError as e:
            if e.errno == errno.ENOENT:
                self._token_last_updated = None
            else:
                raise

        # Disable SSL check for localhost or when insecure=True
        self.insecure = kwargs.pop("insecure", False)
        if self.insecure:
            logger.error(Warnings.insecure_warning)
        if re.match(r"^https?://localhost", self.server_url) or self.insecure:
            requests.packages.urllib3.disable_warnings()
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
            self._verify = False
        else:
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = ""
            self._verify = True

        self._login(oauth2_primary, password, api_key)

    def _build_session(self, attempt: int = 0):
        if attempt >= self.max_retries:
            raise LoginAttemptsExceededError()

        self.session = OAuth2Session(
            client=LegacyApplicationClient(client_id=self.client_id),
            auto_refresh_url=self.token_url,
            token_updater=self._token_updater,
        )
        self._set_session_retries()
        self.session.cookies.set_policy(BlockAll())

    def _clear_session(self):
        self._save_token(None)
        self.logout(self._token_filename)

    def _login(
        self,
        oauth2_primary: str,
        password: Optional[str] = None,
        api_key: Optional[str] = None,
        attempt: int = 0,
    ):
        if password is not None:
            self._login_with_oauth2(password, attempt)
        elif api_key is not None:
            self._login_with_api_key(api_key, attempt)
        elif oauth2_primary:
            self._login_with_oauth2(password, attempt)
        else:
            self._login_with_api_key(api_key, attempt)

    def _login_with_api_key(
        self, api_key: Optional[str] = None, isError: bool = False, attempt: int = 0
    ):

        self._build_session(attempt=attempt)

        def request_api_key():
            if isError:
                print(
                    "Invalid API key. Input correct API Key, that you can generate in API Keys -> Generate API Key"
                )
            else:
                print(
                    "Connect to the cloud using API key, that you can generate in API Keys -> Generate API Key"
                )
            return input("Enter API token key:")

        # get token from json file
        if not api_key and os.path.isfile(self._token_filename):
            try:
                with open(self._token_filename, "r") as f:
                    apiKeyData = JSON.load(f)
            except Exception:
                self._clear_session()
            else:
                if apiKeyData:
                    api_key = apiKeyData.get("access_token")

        # request token from user
        if not api_key:
            api_key = request_api_key()

        # if API key is still empty exit
        if not api_key:
            return 0

        data = {
            "access_token": api_key,
            "token_type": "Bearer",
        }
        self.session.token = data

        try:
            self._save_token(self.session.token)
            response = self.request("get", "team-info/")
        except Exception:
            self._clear_session()
            self._login_with_api_key(isError=True, api_key=None, attempt=attempt + 1)
        else:
            if response.status_code != 200:
                self._clear_session()
                self._login_with_api_key(
                    isError=True, api_key=None, attempt=attempt + 1
                )
            else:
                print("Client connected to the cloud successfully")

    def _login_with_oauth2(self, password: str, attempt: int = 0):

        self._build_session(attempt=attempt)

        if self.username is None or password is None:
            if os.path.exists(self._token_filename):
                with open(self._token_filename, "r") as f:
                    self.session.token = JSON.load(f)
                try:
                    self.session.refresh_token(
                        self.token_url,
                        auth=(self.client_id, self.client_secret),
                        verify=self._verify,
                    )
                    self._save_token(self.session.token)
                except:
                    os.remove(self._token_filename)
                    print("Invalid ClientID, Enter Username And Password to Login")
                    self.session.token = {}
                    self.username = input("Enter username: ")
                    password = getpass("Enter password: ")

            else:
                print(
                    "Connect to SensiML Cloud using your SensiML Account. Sign up for free at https://sensiml.com/plans/community-edition/"
                )
                self.username = input("Enter username: ")
                password = getpass("Enter password: ")

        if not self.session.token:
            try:
                r = self.session.fetch_token(
                    token_url=self.token_url,
                    username=self.username,
                    password=password,
                    # UAA endpoints always require id/secret as basic auth
                    auth=(self.client_id, self.client_secret),
                    verify=self._verify,
                )
            except (InvalidGrantError, MissingTokenError) as e:
                if isinstance(e, InvalidGrantError):
                    print("Invalid log in credentials, please try again.")
                else:
                    print(
                        "No token received: The remote server did not return a valid authorization response."
                    )
                if os.path.exists(self._token_filename):
                    os.remove(self._token_filename)
                password = None
                self.username = None
                return self._login_with_oauth2(password, attempt=attempt + 1)
            self._save_token(self.session.token)

        logger.debug("Login completed")

    def request(
        self,
        method: str,
        path: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        **kwargs,
    ) -> requests.Response:
        """Sends request to server with authentication

        Args:
            method (str): HTTP Method.
            path (str): Path from server root to request.
            json (dict, optional): dictionary of information to be submitted as json
            headers (dict, optional): http headers to be sent
            **kwargs: Additional keyword arguments passed to underlying request library.

        Keyword Args:
            data (dict): Data to upload as application/x-www-form-urlencoded or multipart/form-data.
                Do not use in conjunction with json.
            paged (boolean): Return [PagedRequest] iterator instead of response

        Returns:
            Response: Response object from requests library with the result of the request
        """

        attempt = kwargs.pop("attempt", 0)
        paged = kwargs.pop("paged", False)
        verify = kwargs.pop("verify", self._verify)
        url = self.server_url.strip("/") + "/" + path.lstrip("/")
        if self._token_last_updated != os.path.getmtime(self._token_filename):
            with open(self._token_filename, "r") as f:
                self.session.token = JSON.load(f)

        while attempt < self.max_retries:

            if self.debug:
                print(
                    f"{ datetime.now(timezone.utc)} {method} {url} attempt: {attempt}"
                )

            if paged:
                return PagedRequest(
                    self.session,
                    method,
                    url,
                    json=json,
                    headers=headers,
                    params=params,
                    verify=verify,
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    **kwargs,
                )
            else:
                response = self.session.request(
                    method,
                    url,
                    json=json,
                    params=params,
                    headers=headers,
                    verify=verify,
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    **kwargs,
                )

            attempt += 1

            if self.debug:
                print(f"status code: {response.status_code}")

            if response.status_code in [504]:
                continue

            # temp workaround for bug in django-oauth-toolkit
            if response.status_code not in [401]:
                return response

            try:
                # If normal autorefresh fails we force it
                token = self.session.refresh_token(
                    self.token_url,
                    auth=(self.client_id, self.client_secret),
                    verify=self._verify,
                )
                self._save_token(token)
            except (TokenExpiredError, InvalidGrantError):
                print("Refresh Token expired, please re-enter your login information.")
                try:
                    os.unlink(
                        os.path.join(config_dir, f"{self.server_name}_token.json")
                    )
                except OSError as e:
                    if e.errno != errno.ENOENT:
                        raise
                self._login(None)

        return response

    def paged_request(
        self,
        method: str,
        path: str,
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
        limit: int = 1000,
        **kwargs,
    ):
        """Returns an iterator that will request a new page each call.

        The result returned by the iterator will be the json decoded data of the
        'results' property of the response. Function args are the same as [request()]

        Args:
            method
            path
            json
            headers
            limit (Optional[int]): Number of entries per page, defaults to 1000.
                Note: this will override the 'limit' param specified in 'params'
                request kwarg.
            **kwargs: passed to request method
        """
        params = kwargs.pop("params", {})
        params["limit"] = limit
        return self.request(
            method, path, json, headers, params=params, paged=True, **kwargs
        )

    def file_request(
        self,
        url: str,
        file_path: str,
        data: Optional[dict] = None,
        read_type: str = "rb",
        method: str = "post",
        **kwargs,
    ):
        """Loads a file and formats metadata for specific endpoints and makes server request

        Args:
            path (str): Path to API endpoint
            file_path (str): Local path to file
            data (dict): Data to send to server along with request. May be sent in nonstandard headers instead of request body for some endpoints.
            method (str, optional): HTTP method, defaults to POST
            read_type (str, optional): Mode to open the file. defaults to binary read ('rb')

        Returns:
            Response
        """
        with open(file_path, read_type) as f:

            if url.find("capture/") >= 0:
                request = partial(
                    self.request,
                    method,
                    url,
                    files={"file": f},
                    data=data,
                )
            elif url.find("featurefile/") >= 0:
                request = partial(
                    self.request,
                    method,
                    url,
                    files={"data_file": f},
                    data=data,
                )
            else:
                request = partial(
                    self.request, method, url, data=data, files={"file": f}
                )

            # call method with previously applied arguments
            return request(**kwargs)

    @staticmethod
    def logout(name: str):
        """Deletes saved session data for name"""
        try:
            os.unlink(os.path.join(config_dir, f"{name}_token.json"))
        except OSError as e:
            if e.errno == errno.ENOENT:
                print(f"No session saved for {name}.")
                return
            else:
                raise
        print("Logged out.")

    def _set_session_retries(self):
        """set the number of retries a session has"""
        self.session.mount(
            "http://", requests.adapters.HTTPAdapter(max_retries=self.max_retries)
        )
        self.session.mount(
            "https://", requests.adapters.HTTPAdapter(max_retries=self.max_retries)
        )

    def _token_updater(self, token: str, save: bool = True):
        """a simple function to save our token on refresh

        Args:
            token (dict): a token object for oauth2
        """
        self.session.token = token
        if save:
            self._save_token(token)

    def _save_token(self, token: str):
        if not os.path.exists(config_dir):
            try:
                os.makedirs(config_dir)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
        with open(self._token_filename, "w") as f:
            # f.write(json.dumps(token))
            JSON.dump(token, f)
            self._token_last_updated = os.path.getmtime(f.name)


# With ouath we don't want to send cookies, this will overwite and block session cookies
class BlockAll(CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = (
        lambda self, *args, **kwargs: False
    )
    netscape = True
    rfc2965 = hide_cookie2 = False


class PagedRequest(object):
    def __init__(
        self,
        session: OAuth2Session,
        method: str,
        path: str,
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
        **kwargs,
    ):
        self.session = session
        self._method = method
        self._path = path
        self._json = json
        self._headers = headers
        self._kwargs = kwargs

        self.response = None

    def __iter__(self):
        return self

    def next(self):
        """
        Returns:
            (dict) content of the results property in the response
        """
        if not self.response:
            self.response = self.session.request(
                self._method, self._path, self._json, self._headers, **self._kwargs
            )
        else:
            json = self.response.json()
            path = json["next"]
            if not path:
                raise StopIteration
            self.response = self.session.request(
                self._method, path, self._json, self._headers, **self._kwargs
            )
        self.response.raise_for_status()
        return self.response.json()["results"]
