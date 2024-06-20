import requests
import ssl


def test_all_project(make_get_request):
    get_response = make_get_request("list_project")
    get_json = get_response.json()
    assert get_json[0]["name"] is not None


def test_add_and_edit_delete_project(
    make_get_request, make_post_request, make_put_request, make_delete_request
):
    projectname = "Rest_test_project"
    payload = {"name": projectname}

    # delete project if exists
    get_response = make_get_request("list_project")
    get_json = get_response.json()
    get_project = next(
        (jdata for jdata in get_json if jdata["name"] == projectname), None
    )

    if get_project is not None:
        delete_response = make_delete_request(
            "delete_project", proj_uuid=get_project["uuid"]
        )
        print("Pre-existing project deleted")

    # create new project
    post_response = make_post_request("add_project", payload)
    assert post_response.status_code == 201
    post_json = post_response.json()
    print(post_json)
    assert post_json["name"] == projectname
    new_project_uuid = post_json["uuid"]

    # update project name
    projectname = "updated " + projectname
    payload = {"name": projectname}
    put_response = make_put_request(
        "update_project", payload, proj_uuid=new_project_uuid
    )
    assert put_response.status_code == 200
    put_json = put_response.json()
    assert put_json["name"] == projectname

    # delete project
    delete_response = make_delete_request("delete_project", proj_uuid=new_project_uuid)
    assert delete_response.status_code == 204

    # confirm project deletion
    lookup_response = make_get_request("lookup_project", proj_uuid=new_project_uuid)
    assert lookup_response.status_code == 404
