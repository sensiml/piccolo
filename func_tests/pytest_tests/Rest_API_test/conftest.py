import pytest
import ssl
import random

ssl._create_default_https_context = getattr(ssl, "_create_unverified_context", None)
import requests


def pytest_addoption(parser):
    parser.addoption(
        "--user",
        action="store",
        default="piccolo@sensiml.com",
        help="--user: select user you wish to use",
    )
    parser.addoption(
        "--password",
        action="store",
        default="TinyML4Life",
        help="--password: set password for user login",
    )


def pytest_runtest_setup(item):
    if "server" in item.keywords and "master" in item.config.getoption("--server"):
        pytest.skip()
        # basically 'server' is the keyword that is used to find this the pytest mark


@pytest.fixture(scope="session")
def server(request):

    return request.config.getoption("--server")


@pytest.fixture(scope="session")
def server_url(request):
    decision = request.config.getoption("--server")

    if decision == "sensiml.cloud":
        url = "https://sensiml.cloud"
    elif decision == "localhost":
        url = "http://localhost:80"
    elif decision == "" or None:
        url = "http://localhost:8000"
    elif decision == "staging.sensiml.cloud":
        url = "https://staging.sensiml.cloud"
    elif decision == "dev.sensiml.cloud":
        url = "https://dev.sensiml.cloud"
    elif decision == "localhost_sensiml":
        url = "http://localhost:80"
    else:
        ## Targeting multiple environments
        raise Exception("BAD URL", decision)

    if decision == "localhost":
        import os

        requests.packages.urllib3.disable_warnings()
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    return url


@pytest.fixture(scope="session")
def user(request):
    decision = request.config.getoption("--user")
    return decision


@pytest.fixture(scope="session")
def password(request):
    decision = request.config.getoption("--password")
    return decision


@pytest.fixture(scope="session")
def credentials(user, password, oauth):
    """OAuth2 password auth headers"""
    payload = {"username": user, "password": password}
    payload.update(oauth)

    return payload


@pytest.fixture(scope="session")
def proxy(request):
    decision = request.config.getoption("--server")
    proxies = {}
    if decision in ["proxy-test"]:
        proxies = {
            "http": "http://proxy-us.intel.com:911",
            "https": "http://proxy-us.intel.com:912",
        }

    return proxies


@pytest.fixture(scope="session")
def oauth(request):
    return {
        "client_id": request.config.getoption(
            "--client-id", "f7J0QNKkKcIkHMpk5lvq0wGZtBEpw1YcJ8Bea9Pv"
        ),
        "client_secret": request.config.getoption(
            "--client-secret",
            "4OxQzkEnVc6OmTMKHgi77o8uFhEDz1QCuyKsNFm2Jo84r0TlGBXli0NrZ5uHTI769P3UurvDVB86awZkrEikCUJ7RM333BTS5oajO32BRwsNkPcOzA3JlBkPblvKM0l0",
        ),
        "grant_type": request.config.getoption("--grant-type", "password"),
    }


@pytest.fixture(scope="module")
def token_header(request, credentials, proxy, server_url):
    def fn(su=False):
        if su:
            credentials.update(
                {
                    "username": "sys_sensiml@sensiml.com",
                    "password": "PheonixFromTheAshes",
                }
            )
        response = requests.post(
            server_url + "/oauth/token/", proxies=proxy, verify=False, data=credentials
        )

        print(response.json())
        print(credentials)

        return {"authorization": "Bearer " + response.json()["access_token"]}

    return fn


@pytest.fixture(scope="module")
def endpoints():
    return {
        "list_project": "/project/",
        "add_project": "/project/",
        "update_project": "/project/{proj_uuid}/",
        "delete_project": "/project/{proj_uuid}/",
        "lookup_project": "/project/{proj_uuid}/",
        "list_code": "/project/{proj_uuid}/codebook/code/",
        "add_code": "/project/{proj_uuid}/codebook/code/",
        "delete_code": "/project/{proj_uuid}/codebook/code/{code_uuid}/",
        "edit_code": "/project/{proj_uuid}/codebook/code/{code_uuid}/",
        "list_event": "/project/{proj_uuid}/event/",
        "add_event": "/project/{proj_uuid}/event/",
        "get_metadata_names": "/project/{proj_uuid}/event/eventmetadata/names/",
        "metadata_name_specific": "/project/{proj_uuid}/event/eventmetadata/{name}/values/",
        "get_eventlabel_names": "/project/{proj_uuid}/event/eventlabel/names/",
        "eventlabel_name_specific": "/project/{proj_uuid}/event/eventlabel/{name}/values/",
        "eventlabel_value_specific": "/project/{proj_uuid}/event/eventlabel/{name}{value}/",
        "edit_event": "/project/{proj_uuid}/event/{event_uuid}/",
        "delete_event": "/project/{proj_uuid}/event/{event_uuid}/",
        "list_eventfile": "/project/{proj_uuid}/event/{event_uuid}/eventfile/",
        "add_eventfile": "/project/{proj_uuid}/event/{event_uuid}/eventfile/",
        "edit_eventfile": "/project/{proj_uuid}/event/{event_uuid}/eventfile/{eventfile_uuid}/",
        "delete_eventfile": "/project/{proj_uuid}/event/{event_uuid}/eventfile/{eventfile_uuid}/",
        "list_eventlabel": "/project/{proj_uuid}/event/{event_uuid}/eventlabel/",
        "add_eventlabel": "/project/{proj_uuid}/event/{event_uuid}/eventlabel/",
        "edit_eventlabel": "/project/{proj_uuid}/event/{event_uuid}/eventlabel/{eventlabel_uuid}/",
        "delete_eventlabel": "/project/{proj_uuid}/event/{event_uuid}/eventlabel/{eventlabel_uuid}/",
        "list_eventmetadata": "/project/{proj_uuid}/event/{event_uuid}/eventmetadata/",
        "add_eventmetadata": "/project/{proj_uuid}/event/{event_uuid}/eventmetadata/",
        "edit_eventmetadata": "/project/{proj_uuid}/event/{event_uuid}/eventmetadata/{eventmetadata_uuid}/",
        "delete_eventmetadata": "/project/{proj_uuid}/event/{event_uuid}/eventmetadata/{eventmetadata_uuid}/",
        "list_sandbox": "/project/{proj_uuid}/sandbox/",
        "add_sandbox": "/project/{proj_uuid}/sandbox/",
        "edit_sandbox": "/project/{proj_uuid}/sandbox/{sandbox_uuid}/",
        "delete_sandbox": "/project/{proj_uuid}/sandbox/{sandbox_uuid}/",
        "get_sandbox_data": "/project/{proj_uuid}/sandbox/{sandbox_uuid}/data/",
        "get_knowledgepack": "/project/{proj_uuid}/sandbox/{sandbox_uuid}/knowledgepack/",
        "specific_knowledgepack": "/project/{proj_uuid}/sandbox/{sandbox_uuid}/knowledgepack/{knowledgepack_uuid}",
        "recognize_vector": "/project/{proj_uuid}/sandbox/{sandbox_uuid}/recognize/",
        "get_query": "/project/{proj_uuid}/query/",
        "add_query": "/project/{proj_uuid}/query/",
        "edit_query": "/project/{proj_uuid}/query/{query_uuid}/",
        "delete_query": "/project/{proj_uuid}/query/{query_uuid}/",
        "get_query_data": "/project/{proj_uuid}/query/{queyr_uuid}/data/",
        "get_query_stats": "/project/{proj_uuid}/query/{queyr_uuid}/statistics/",
        "get_query_size": "/project/{proj_uuid}/query/{queyr_uuid}/size/",
        "get_transform": "/transform/",
        "add_transform": "/transform/",
        "edit_transform": "/transform/{transform_uuid}/",
        "delete_transform": "/transform/{transform_uuid}/",
        "get_modelgenerator": "/modelgenerator/",
        "add_modelgenerator": "/modelgenerator/",
        "edit_modelgenerator": "/modelgenerator/{modelgenerator_uuid}/",
        "delete_modelgenerator": "/modelgenerator/{modelgenerator_uuid}/",
        "get_featurefile": "/project/{proj_uuid}/featurefile/",
        "add_featurefile": "/project/{proj_uuid}/featurefile/",
        "edit_featurefile": "/project/{proj_uuid}/featurefile/{featurefile_uuid}/",
        "delete_featurefile": "/project/{proj_uuid}/featurefile/{featurefile_uuid}/",
        "async_submit": "/project/{proj_uuid}/sandbox/{sandbox_uuid}/async_submit/",
        "async_retrieve": "/project/{proj_uuid}/sandbox/{sandbox_uuid}/async_retrieve",
        "async_status": "/project/{proj_uuid}/sandbox/{sandbox_uuid}/async_status/",
        "list_team": "/team/",
        "create_team": "/team/",
        "get_team": "/team/{team_uuid}/",
        "edit_team": "/team/{team_uuid}/",
        "delete_team": "/team/{team_uuid}/",
        "list_users": "/user/",
        "create_user": "/user/",
        "user_info": "/user/{user_id}/",
        "edit_user": "/user/{user_id}/",
        "delete_user": "/user/{user_id}/",
    }


@pytest.fixture(scope="module")
def make_get_request(proxy, endpoints, server_url, token_header):
    proxies = proxy
    server = server_url

    def get_request(endpoint, su=False, **params):
        if params:
            url_path = endpoints[endpoint].format(**params)
        else:
            url_path = endpoints[endpoint]
        url = server + url_path
        get_response = requests.get(
            url=url, proxies=proxies, verify=False, headers=token_header(su)
        )
        return get_response

    return get_request


@pytest.fixture(scope="module")
def make_post_request(proxy, endpoints, server_url, token_header):
    proxies = proxy
    server = server_url

    def post_request(endpoint, payload, su=False, **params):
        if params:
            url_path = endpoints[endpoint].format(**params)
        else:
            url_path = endpoints[endpoint]
        url = server + url_path
        post_response = requests.post(
            url=url,
            proxies=proxies,
            json=payload,
            verify=False,
            headers=token_header(su),
        )
        return post_response

    return post_request


@pytest.fixture(scope="module")
def make_patch_request(proxy, endpoints, server_url, token_header):
    proxies = proxy
    server = server_url

    def patch_request(endpoint, payload, su=False, **params):
        if params:
            url_path = endpoints[endpoint].format(**params)
        else:
            url_path = endpoints[endpoint]
        url = server + url_path
        patch_response = requests.patch(
            url=url,
            proxies=proxies,
            json=payload,
            verify=False,
            headers=token_header(su),
        )
        return patch_response

    return patch_request


@pytest.fixture(scope="module")
def make_put_request(proxy, endpoints, server_url, token_header):
    proxies = proxy
    server = server_url

    def put_request(endpoint, payload, su=False, **params):
        if params:
            url_path = endpoints[endpoint].format(**params)
        else:
            url_path = endpoints[endpoint]
        url = server + url_path
        put_response = requests.put(
            url=url,
            proxies=proxies,
            json=payload,
            verify=False,
            headers=token_header(su),
        )
        return put_response

    return put_request


@pytest.fixture(scope="module")
def make_delete_request(proxy, endpoints, server_url, token_header):
    proxies = proxy
    server = server_url

    def delete_request(endpoint, su=False, **params):
        if params:
            url_path = endpoints[endpoint].format(**params)
        else:
            url_path = endpoints[endpoint]
        url = server + url_path
        delete_response = requests.delete(
            url=url, proxies=proxies, verify=False, headers=token_header(su)
        )
        return delete_response

    return delete_request


@pytest.fixture(scope="module")
def team(make_post_request, make_delete_request, make_get_request):
    # team_name = "test_team" + '_' + str(random.random())
    team_name = "test_team_rest"

    teams = make_get_request(endpoint="list_team", su=True)
    teams_json = teams.json()
    lookup_team = next((team for team in teams_json if team["name"] == team_name), None)

    if lookup_team is not None:
        clear_team = make_delete_request(
            endpoint="delete_team", su=True, team_uuid=lookup_team["uuid"]
        )

    create_team_payload = {
        "name": team_name,
    }
    r = make_post_request(payload=create_team_payload, endpoint="create_team", su=True)

    yield r
    d = make_delete_request(endpoint="delete_team", su=True, team_uuid=r.json()["uuid"])


@pytest.fixture(scope="module")
def teamadmin(team, make_post_request, make_delete_request):
    # user_email = "test_user" + '_' + str(random.random()) + "@intel.com"
    user_email = "test_user_rest@intel.com"

    create_user_payload = {
        "email": user_email,
        "password": "inteltest",
        "is_superuser": False,
        "team": team.json()["name"],
    }
    r = make_post_request(payload=create_user_payload, su=True, endpoint="create_user")
    yield r
