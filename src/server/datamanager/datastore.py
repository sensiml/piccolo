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

import gzip
import json
import logging
import os
import pickle
from io import BytesIO
from shutil import copyfile, rmtree
from pathlib import Path

from logger.log_handler import LogHandler
from pandas import DataFrame, read_csv

logger = LogHandler(logging.getLogger(__name__))


def get_datastore_basedir(directory):
    return directory


def ensure_path_exists(path):
    path = Path(path)  # Convert to pathlib.Path for safer handling
    path.parent.mkdir(parents=True, exist_ok=True)
    path.mkdir(exist_ok=True)
    return path


def ensure_parent_dir_exists(path):
    path = Path(path)  # Convert to pathlib.Path for safer handling
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def validate_dataframe(data):
    if not isinstance(data, DataFrame):
        raise Exception("Data must be a DataFrame to save to csv")

    if sum([x == 0 for x in data.shape]) != 0:
        raise Exception("No data was generated for this step!")


class ObjectFactory:
    def __init__(self):
        self._builders = {}

    def register_builder(self, key, builder):
        self._builders[key] = builder

    def create(self, key, **kwargs):
        builder = self._builders.get(key)
        if not builder:
            raise ValueError(key)
        return builder(**kwargs)


class DataStoreProvider(ObjectFactory):
    def get(self, service_id, **kwargs):
        return self.create(service_id, **kwargs)


class LocalDataStoreService:
    def __init__(self, bucket: str = "", folder: str = "") -> None:

        print(f"DATASTORE SERVICE INITIALIZED with b:{bucket} f:{folder}")
        self._bucket = bucket  # base dir
        self._folder = folder

    @property
    def is_remote(self) -> bool:
        return False

    def _fold(self, key, folder=None):
        """add a root folder path to the key, the root folder is set when the  object is created"""
        if self._bucket and "('/hom" in self._bucket:
            raise Exception("INVALID PATH HERE")

        if self._folder and "('/hom" in self._folder:
            raise Exception("INVALID PATH HERE")

        if folder and "('/hom" in folder:
            raise Exception("INVALID PATH HERE")

        if folder:
            return os.path.join(self._bucket, folder, key)
        if self._folder:
            return os.path.join(self._bucket, self._folder, key)

        return key

    def get_data(self, key):
        print(f"DATASTORE SERVICE: Retrieving data from {self._fold(key)}")
        if key.split(".")[-1] == "gz":
            data = read_csv(self._fold(key), compression="gzip", sep="\t")

        elif key.split(".")[-1] == "csv":
            data = read_csv(self._fold(key), sep=",")

        elif key.split(".")[-1] == "json":
            with open(self._fold(key), "r") as fid:
                data = json.load(fid)

        elif key.split(".")[-1] == "pkl":
            with gzip.open(self._fold(key), "rb") as fid:
                data = pickle.load(fid)

        else:
            raise Exception("Format not supported!")

        return data

    def get_json(self, key):

        f = open(self._fold(key), "r")

        return json.load(f.read())

    def key_exists(self, file_path):
        return os.path.exists(self._fold(file_path))

    def get(self, key: str, file_path=None, file_handler=None):
        # TODO DASTASTORE Implemenet this feature in the local
        return None

    def save_data(self, data, key, fmt, sep="\t"):
        print(f"DATASTORE SERVICE: Saving data to {self._fold(key)}")
        ensure_path_exists(os.path.dirname(self._fold(key)))

        if fmt == ".csv.gz":
            validate_dataframe(data)

            gz_body = BytesIO()
            with gzip.GzipFile(None, "wb", 6, gz_body) as gzout:
                gzout.write(data.to_csv(None, index=None, sep=sep).encode("utf-8"))

            with open(self._fold(key), "wb") as obj:
                obj.write(gz_body.getvalue())

        elif fmt == ".csv":
            validate_dataframe(data)

            with open(self._fold(key), "w") as obj:
                obj.write(data.to_csv(None, index=None, sep=sep))

        elif fmt == ".json":
            if not isinstance(data, dict) and not isinstance(data, list):
                raise Exception("data must be a dict or list to save to to json")

            with open(self._fold(key), "w") as obj:
                obj.write(json.dumps(data))

        elif fmt == ".pkl":
            gz_body = BytesIO()

            with gzip.GzipFile(None, "wb", 6, gz_body) as gzout:
                gzout.write(pickle.dumps(data))

            with open(self._fold(key), "wb") as obj:
                obj.write(gz_body.getvalue())

        else:
            raise Exception("FORMAT NOT SUPPORTED")

        return True

    def delete(self, key: str):
        try:
            os.remove(self._fold(key))
        except FileNotFoundError as err:
            logger.error({"message": err, "log_type": "datamanager"})

    def remove_folder(self, key: str):
        try:
            rmtree(self._fold(key))
        except Exception as err:
            logger.error({"message": err, "log_type": "datamanager"})

    def copy(self, key: str, new_key: str, directory: str):
        print("FOLD", self._fold(""))
        print("Copy", self._fold(key))
        print("TO", os.path.join(directory, new_key))
        return copyfile(self._fold(key), os.path.join(directory, new_key))

    def copy_to_folder(self, key: str, new_key: str, new_directory: str):
        print(f"DATASTORE SERVICE: Copy from {self._fold(key)}")
        print(f"DATASTORE SERVICE: Copy to {self._fold(key, folder=new_directory)}")
        print(f"DATASTORE SERVICE: KEY: {key} B: {self._bucket}, F: {new_directory}")
        ensure_path_exists(new_directory)
        return copyfile(self._fold(key), self._fold(new_key, folder=new_directory))

    def delete_path(self, path):
        try:
            os.remove(path)
        except OSError:
            rmtree(path, ignore_errors=True)
        except:
            pass

    def create_url(self, *_args, **_kwargs):
        raise NotImplementedError(
            "Current datastore provider doesn't support direct cloud uploading"
        )


class LocalDataStoreBuilder(object):
    def __call__(self, bucket: str = "", folder: str = "", **_ignored):
        return LocalDataStoreService(bucket=bucket, folder=folder)


services = DataStoreProvider()
services.register_builder("LOCAL", LocalDataStoreBuilder())


def get_datastore(**kwargs):
    return services.get("LOCAL", **kwargs)
