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

import os

import environ

env = environ.Env(
    REDIS_ADDRESS=(str, "127.0.0.1"),
    BROKER_URL=(str, "redis://localhost:6379"),
    TIME_ZONE=(str, "UTC"),
    FLOWER_URL_PREFIX=(str, "flower"),
    FLOWER_PORT=(int, 5555),
)

try:
    environ.Env.read_env(os.path.expanduser("~/.env.sml"))
except:
    pass


task_serializer = "pickle"
result_serializer = "pickle"
accept_content = ["pickle"]
broker_url = env("BROKER_URL")
redis_address = env("REDIS_ADDRESS")
time_zone = env("TIME_ZONE")
persistent = True
db = "/home/sml-app/flower.db"
url_prefix = env("FLOWER_URL_PREFIX")
port = env("FLOWER_PORT")
