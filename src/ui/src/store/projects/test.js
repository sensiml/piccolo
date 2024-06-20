/*
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
*/

import * as projectActions from "./actions";
import {
  DELETING_PROJECT,
  DELETED_PROJECT,
  LOADING_PROJECTS,
  LOADING_PROJECT_STATISTICS,
  STORE_PROJECTS,
  STORE_PROJECT_STATISTICS,
  STORE_SELECTED_PROJECT,
  STORE_LAST_SELECTED_PROJECT,
} from "./actionTypes";
import configureMockStore from "redux-mock-store";
import thunk from "redux-thunk";
import "regenerator-runtime/runtime";
import mockAxios from "axios";

jest.mock("../../store/reducers.js");
const mockStore = configureMockStore([thunk]);

describe("project actions", () => {
  let store;
  beforeEach(() => {
    store = mockStore({
      projects: {},
    });
  });

  it("should fetch all projects", async () => {
    //mock setup
    const expectedProjects = [
      {
        name: "test2",
        id: 2,
        uuid: "c4469500-54a3-40c0-b364-300c4cb2feb1",
        metadata: 7,
        files: 10,
        size_mb: 16,
        classes: 60,
        queries: 80,
        models: 15,
      },
      {
        name: "test1",
        id: 1,
        uuid: "653f0a20-3d76-4983-b1c3-b19c0bf56903",
        metadata: 7,
        files: 10,
        size_mb: 16,
        classes: 60,
        queries: 80,
        models: 15,
      },
    ];
    const mockedResponse = Promise.resolve({ data: expectedProjects });
    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();
    const expectedActions = [
      {
        type: LOADING_PROJECTS,
      },
      {
        type: STORE_PROJECTS,
        projects: expectedProjects,
      },
    ];

    await projectActions.loadProjects()(dispatch, getState);
    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should log error when fetch all projects fails", async () => {
    mockAxios.get.mockImplementation(() => {
      throw new Error("Some Error");
    });
    const dispatch = jest.fn();
    const getState = jest.fn();
    const expectedActions = [
      {
        type: LOADING_PROJECTS,
      },
      {
        type: STORE_PROJECTS,
        projects: [],
      },
    ];

    await projectActions.loadProjects()(dispatch, getState);
    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should handle null project list response", async () => {
    const mockedResponse = Promise.resolve({ data: undefined });
    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();
    const expectedActions = [
      {
        type: LOADING_PROJECTS,
      },
      {
        type: STORE_PROJECTS,
        projects: undefined,
      },
    ];

    await projectActions.loadProjects()(dispatch, getState);
    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should deleted a project", async () => {
    const expectedProjects = [
      {
        name: "test2",
        id: 2,
        uuid: "c4469500-54a3-40c0-b364-300c4cb2feb1",
        metadata: 7,
        files: 10,
        size_mb: 16,
        classes: 60,
        queries: 80,
        models: 15,
      },
      {
        name: "test1",
        id: 1,
        uuid: "653f0a20-3d76-4983-b1c3-b19c0bf56903",
        metadata: 7,
        files: 10,
        size_mb: 16,
        classes: 60,
        queries: 80,
        models: 15,
      },
    ];

    //deleteProject
    //mock setup
    const projectUuid = "22937b94-3882-4c2b-beef-5c1c754ffcd1";
    const mockedResponse = Promise.resolve({ data: expectedProjects });
    mockAxios.delete.mockResolvedValue({ status: "success" });
    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: DELETING_PROJECT,
      },
      {
        type: DELETED_PROJECT,
        projects: expectedProjects,
      },
    ];

    await projectActions.deleteProject(projectUuid)(dispatch, getState);
    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should log error when fetch project statistics fails", async () => {
    const projectUuid = "22937b94-3882-4c2b-beef-5c1c754ffcd1";
    mockAxios.get.mockImplementation(() => {
      throw new Error("Some Error");
    });
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: LOADING_PROJECT_STATISTICS,
      },
      {
        type: STORE_PROJECT_STATISTICS,
        statistics: [],
      },
    ];

    await projectActions.loadProjectStatistics(projectUuid)(dispatch, getState);
    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should fetch project statistics", async () => {
    //mock setup
    const expectedStatistics = ["Stats"];
    const projectUuid = "22937b94-3882-4c2b-beef-5c1c754ffcd1";
    const mockedResponse = Promise.resolve({ data: expectedStatistics });
    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: LOADING_PROJECT_STATISTICS,
      },
      {
        type: STORE_PROJECT_STATISTICS,
        statistics: expectedStatistics,
      },
    ];

    await projectActions.loadProjectStatistics(projectUuid)(dispatch, getState);
    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should log error when fetch project statistics fails", async () => {
    const projectUuid = "22937b94-3882-4c2b-beef-5c1c754ffcd1";
    mockAxios.get.mockImplementation(() => {
      throw new Error("Some Error");
    });
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: LOADING_PROJECT_STATISTICS,
      },
      {
        type: STORE_PROJECT_STATISTICS,
        statistics: [],
      },
    ];

    await projectActions.loadProjectStatistics(projectUuid)(dispatch, getState);
    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should set the selected project in the store", async () => {
    let expectedUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    let expectedName = "Test Projects";
    let project = { uuid: expectedUuid, name: expectedName, segments: 20 };
    const expectedAction = {
      type: STORE_SELECTED_PROJECT,
      selectedProject: project,
    };
    expect(projectActions.setSelectedProject(project)).toEqual(expectedAction);
  });

  it("should set the last selected project in the store with team and userId", async () => {
    const dispatch = jest.fn();
    const expectedUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const expectedName = "Test Projects";
    const project = { uuid: expectedUuid, name: expectedName, segments: 20 };
    const [team, userId] = ["SensimlTestTeam", "test@sensiml.com"];
    
    const expectedAction = {
      type: STORE_LAST_SELECTED_PROJECT,
      selectedProject: { [`${team}-${userId}`]: project },
    };
    projectActions.setLastSelectedProject(project, team, userId)(dispatch);
    projectActions.setLastSelectedProject(team, userId)(dispatch);
    projectActions.setLastSelectedProject(team)(dispatch);
    projectActions.setLastSelectedProject()(dispatch);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedAction); 
    expect(dispatch.mock.calls[1]).toEqual(undefined); // undefined means dispatch has not called
    expect(dispatch.mock.calls[2]).toEqual(undefined); // undefined means dispatch has not called
    expect(dispatch.mock.calls[3]).toEqual(undefined); // undefined means dispatch has not called
  });
});
