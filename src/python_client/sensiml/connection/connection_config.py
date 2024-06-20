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
    import configparser as ConfigParser
except:
    import ConfigParser
import io
import os
import errno
from typing import Optional
from six.moves import input


class ConnectionConfig(dict):
    """Loads or creates .cfg file to/from object

    Config properties can be accessed as attributes or as dictionary keys.
    Treating object as dict only contains config items, not special properties.
    """

    properties = ("path", "server")

    def __init__(self, server: str, path: Optional[str] = None, **kwargs):
        """
        Args:
            server (str): Name of server section in config file
            path (str, optional): Path to config file
        """
        self.server = server

        self.path = path
        if path:
            self.load_from_file(path=path)

    def load_from_file(self, path: Optional[str] = None, stream: Optional[str] = None):
        """Loads config file

        Args:
            path (str, optional): Path to file. specifiying this also updates the
                `path` property of the ConnectionConfig instance.
            stream (optional): Text stream of config.
        """
        config = ConfigParser.ConfigParser()
        if path and stream:
            raise IOError("Cannot pass both path and stream")

        if not os.path.exists(path):
            with open(path, "w") as fid:
                pass

        if path:
            config.read_file(open(path))
        elif stream:
            config.read_file(io.BytesIO(stream))

        self.path = path
        self.update({t[0]: t[1] for t in config.items(self.server)})

        return self

    def save(self, path: Optional[str] = None):
        """Saves section to config file

        Args:
            path (str, optional): Path to save file instead of object's
                 `path` property. Does NOT change `path` property.
        """
        path = path if path else self.path
        config = ConfigParser.ConfigParser()

        if path:
            try:
                config.readfp(open(path))
            except IOError as e:
                if not e.errno == errno.ENOENT:
                    raise

        try:
            config.add_section(self.server)
        except ConfigParser.DuplicateSectionError:
            pass

        # Set server properties
        config.set(self.server, "url", self.url)

        if self.auth_url:
            config.set(self.server, "auth_url", self.auth_url)

        config.write(open(path, "w"))

        return self

    def save_config(self, path: Optional[str] = None):
        """Prompts for user input, if needed, before calling save()

        Args:
            path (str, optional): Save location to use instead of `path` property.
        """
        path = path if path else self.path

        self.url = self.url or input("Enter server URL: ")

        if self.url[-1] != "/":
            self.url += "/"

        self.auth_url = self.url + "oauth/"

        self.save(path)

        print(f"Saved configuration file to {os.path.join(os.path.abspath('.'), path)}")

        return self

    def get_server_dict(self):
        return self

    def create_config_object(
        self,
        path: Optional[str] = None,
        url: Optional[str] = None,
        auth_url: Optional[str] = None,
    ):
        """Creates new config section if needed"""
        path = path if path else self.path

        self.url = url
        self.auth_url = auth_url

        if not path:
            path = input("Enter name of config file (connect.cfg): ") or "connect.cfg"
        self.save_config()

        return self

    def __getattr__(self, key):
        try:
            return self.__getitem__(key)
        except KeyError as e:
            raise AttributeError(e)

    def __setattr__(self, key, value):
        super(ConnectionConfig, self).__setattr__(key, value)
        if key in self.properties:
            return
        try:
            super(ConnectionConfig, self).__setitem__(key, value)
        except KeyError as e:
            raise AttributeError(e)

    def __setitem__(self, key, value):
        if key in self.properties:
            raise KeyError("This key is reserved by the system.")
        super(ConnectionConfig, self).__setitem__(key, value)
        try:
            super(ConnectionConfig, self).__setattr__(key, value)
        except AttributeError as e:
            raise KeyError(e)

    def __delattr__(self, key):
        super(ConnectionConfig, self).__delattr__(key)
        try:
            super(ConnectionConfig, self).__delitem__(key)
        except KeyError as e:
            raise AttributeError(e)

    def __delitem__(self, key):
        super(ConnectionConfig, self).__delitem__(key)
        try:
            super(ConnectionConfig, self).__delattr__(key)
        except AttributeError as e:
            raise KeyError(e)
