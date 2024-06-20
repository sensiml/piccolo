import os
import sys

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--rlocal",
        action="store",
        default="no",
        help="--rlocal: type yes to run these test using local codebase,\
                     type no to use kbclient package, default is no",
    )
    parser.addoption(
        "--server",
        action="store",
        default="sensiml.cloud",
        help="--server: choose which server you want to run \
                     these tests on, default =  staging",
    )
    parser.addoption(
        "--insecure",
        action="store",
        default="False",
        help="Directory SVN checks out to for test data",
    )
    parser.addoption(
        "--sdk_dir",
        action="store",
        default="",
        help="Directory of SDK used to build in profiling",
    )
    parser.addoption(
        "--device_port",
        action="store",
        default="",
        help="COM port used to communicate in profiling",
    )
    parser.addoption(
        "--device_baud",
        action="store",
        default="",
        help="COM speed used to communicate in profiling",
    )
    parser.addoption(
        "--verbose_connection",
        action="store",
        default=False,
        help="Include the printouts for post requests",
    )


@pytest.fixture()
def SensiMLImport(request):
    decision = request.config.getoption("--rlocal")
    if decision.lower() in ("yes", "true", "y"):
        sys.path.insert(0, "../../../src/python_client")
        sys.path.insert(0, "../../src/python_client")

    from sensiml import SensiML

    return SensiML


@pytest.fixture(scope="session")
def SensiMLImportSession(request):
    decision = request.config.getoption("--rlocal")
    if decision.lower() in ("yes", "true", "y"):
        sys.path.insert(0, "../../../src/python_client")
        sys.path.insert(0, "../../src/python_client")

    from sensiml import SensiML

    return SensiML


@pytest.fixture()
def background_capture_endpoints(request):

    decision = request.config.getoption("--rlocal")
    if decision.lower() in ("yes", "true", "y"):
        sys.path.insert(0, "../../../src/python_client")
        sys.path.insert(0, "../../src/python_client")

    from sensiml.datamanager.capture import BackgroundCapture
    from sensiml.datamanager.captures import BackgroundCaptures

    return BackgroundCapture, BackgroundCaptures


@pytest.fixture()
def ClientConnection(request, SensiMLImport):
    server = request.config.getoption("--server")
    insecure = request.config.getoption("--insecure")
    verbose_connection = request.config.getoption("--verbose_connection")

    if server in ["test-proxy-server"]:
        os.environ["http_proxy"] = ""
        os.environ["https_proxy"] = ""

    path = "connect.cfg"
    client = SensiMLImport(
        server=server,
        path=path,
        insecure=insecure,
        skip_validate=insecure,
        username="piccolo@sensiml.com",
        password="TinyML4Life",
        verbose_connection=verbose_connection,
    )

    return client


@pytest.fixture(scope="session")
def ClientConnectionSession(request, SensiMLImportSession):
    server = request.config.getoption("--server")
    insecure = request.config.getoption("--insecure")
    verbose_connection = request.config.getoption("--verbose_connection")

    if server in ["test-proxy-server"]:
        os.environ["http_proxy"] = ""
        os.environ["https_proxy"] = ""

    path = "connect.cfg"
    client = SensiMLImportSession(
        server=server,
        path=path,
        insecure=insecure,
        skip_validate=insecure,
        username="piccolo@sensiml.com",
        password="TinyML4Life",
        verbose_connection=verbose_connection,
    )

    return client


@pytest.fixture(scope="session")
def DataDir(request):
<<<<<<< HEAD
    data_dir = os.path.join(os.path.dirname(__file__),'data')
=======
    data_dir = os.path.join(os.path.dirname(__file__), "data")
>>>>>>> 196245ee (# This is a combination of 4 commits.)

    return data_dir


@pytest.fixture
def dsk_random_project(ClientConnectionSession):
    import random

    import pandas as pd

    client = ClientConnectionSession
    project_name = "Test_Project_{}".format(random.randint(0, 100000))
    prj = client.projects.get_project_by_name(project_name)

    # Delete the project if it exists
    if prj is not None:
        prj.delete()

    client.project = project_name

    yield client

    print("DELETE PROJECT", project_name)

    client.project.delete()


@pytest.fixture
def dsk_proj_prep(ClientConnectionSession, DataDir):
    import random

    import pandas as pd

    dsk = ClientConnectionSession
    project_name = "Test_Project_{}".format(random.randint(0, 1000))
    prj = dsk.projects.get_project_by_name(project_name)

    # Delete the project if it exists
    if prj is not None:
        prj.delete()

    dsk.project = project_name
    dsk.pipeline = "automation_test_pipeline"

    dogcommands_data = pd.read_csv("{}/kbbasics/dogcommands.csv".format(DataDir))
    dogcommands_data.columns = [
        "AccelerometerX",
        "AccelerometerY",
        "AccelerometerZ",
        "GyroscopeX",
        "GyroscopeY",
        "GyroscopeZ",
        "CaptureID",
        "Label",
    ]

    dsk.upload_dataframe("dogcommand.csv", dogcommands_data, force=True)

    yield dsk

    dsk.project.delete()


@pytest.fixture()
def dsk_proj(ClientConnectionSession):
    import random

    import pandas as pd

    dsk = ClientConnectionSession
    project_name = "Test_Project_{}".format(random.randint(0, 10000))
    prj = dsk.projects.get_project_by_name(project_name)

    # Delete the project if it exists
    if prj is not None:
        prj.delete()

    dsk.project = project_name
    dsk.pipeline = "TestPipeline"

    yield dsk

    dsk.project.delete()


@pytest.fixture()
def sdk_dir(request):
    return request.config.getoption("--sdk_dir")


@pytest.fixture()
def device_port(request):
    return request.config.getoption("--device_port")


@pytest.fixture()
def device_baud(request):
    return request.config.getoption("--device_baud")
