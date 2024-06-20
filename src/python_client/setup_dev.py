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
import sys

from setuptools import find_packages, setup

__version__ = "2024.1.0"


# 'setup.py publish' shortcut.

if sys.argv[-1] == "publish":
    os.system("python setup_dev.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    sys.exit()


# 'setup.py test' shortcut.

# !pip install --index-url https://test.pypi.org/simple/ sensiml -U

if sys.argv[-1] == "test":
    os.system("python setup_dev.py sdist bdist_wheel")
    os.system("twine upload --repository-url https://test.pypi.org/legacy/ dist/*")
    sys.exit()


setup(
    name="sensiml-dev",
    description="SensiML Analytic Suite Python Dev Client",
    version=__version__,
    author="SensiML",
    author_email="support@sensiml.com",
    license="Proprietary",
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(exclude=["*test*", "*widgets*"]),
    package_data={
        "sensiml.datasets": ["*.csv"],
    },
    include_package_data=True,
    long_description=open("README.md").read(),
    install_requires=[
        "cookiejar==0.0.2",
        "requests>=2.14.2",
        "requests-oauthlib>=0.7.0",
        "appdirs==1.4.3",
        "semantic_version>=2.6.0",
        "numpy",
        "pandas",
        "matplotlib",
        "prompt-toolkit",
        "seaborn",
        "wurlitzer",
        "tabulate",
    ],
)
