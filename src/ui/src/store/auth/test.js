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

/* eslint-disable */
import "regenerator-runtime/runtime";
import mockAxios from "axios";
import configureMockStore from "redux-mock-store";
import thunk from "redux-thunk";

import * as actions from "./actions";
import { LOAD_TEAM_INFO, LOG_OUT } from "./actions/actionTypes";

const middlewares = [thunk];
const mockStore = configureMockStore(middlewares);

jest.mock("../../store/reducers.js");
jest.mock("axios");

describe("auth actions", () => {
  // TODO change
  let store;
  beforeEach(() => {
    store = mockStore({});
  });

  it("should login", async () => {
    const email = "test@mail.com";
    const password = "Test123";

    const expectedAuthInfo = {
      access_token: "uCHzfxvEs4CQJhnlfI3CR1JYMaHkkE",
      expires_in: 36000,
      refresh_token: "UKTu2xThtZ06UuBa1blbURSJoDM9YD",
      scope: "kb.data kb.pipeline",
      token_type: "Bearer",
    };

    const responseTeamSubscription = {
      name: "RaccoonTeam",
      cpu_usage_subscription: {
        credits_used: 0,
        credits: 0,
      },
    };

    const responseTeamInfo = {
      active: true,
      expires: "2099-12-24T17:21:28Z",
      subscription: "DEVELOPER",
    };

    const responseTranform = [
      {
        input_contract: [],
        name: "High Pass Filter",
        subtype: "Sensor Filter",
      },
    ];

    const responsePlatformLogos = {
      ARM: "test-file-stub",
      Arduino: "test-file-stub",
      Espressif: "test-file-stub",
      Google: "test-file-stub",
      Infineon: "test-file-stub",
      M5Stack: "test-file-stub",
      Microchip: "test-file-stub",
      MinGW: "test-file-stub",
      NXP: "test-file-stub",
      "Nordic Semiconductor": "test-file-stub",
      QuickLogic: "test-file-stub",
      "Raspberry Pi Foundation": "test-file-stub",
      STMicroelectronics: "test-file-stub",
      "Silicon Labs": "test-file-stub",
      onsemi: "test-file-stub",
      "x86 GCC": "test-file-stub",
    };

    const responsePlatforms = [
      {
        applications: "SensiML",
        platform_versions: ["2.1", "1.3"],
        uuid: "test",
        name: "SensiML",
      },
      {
        applications: "Arm GCC",
        platform_versions: ["2.1", "1.3"],
        uuid: "e9f53dfa-f434-4f24-9577-839c190f74da",
        name: "Arm GCC",
      },
    ];

    const expectedPlatforms = [
      {
        applications: "Arm GCC",
        platform_versions: ["2.1", "1.3"],
        uuid: "e9f53dfa-f434-4f24-9577-839c190f74da",
        name: "Arm GCC",
      },
      {
        applications: "SensiML",
        platform_versions: ["2.1", "1.3"],
        uuid: "test",
        name: "SensiML",
      },
    ];

    const responseSeed = [
      {
        description: "Generates a se",
        id: 1,
        input_contract: null,
      },
    ];

    const responseProjects = [
      {
        created_at: "2018-08-21T12:18:25.183523Z",
        description: null,
        files: 61,
        models: 92,
        name: "Swimming_POC_August",
      },
    ];

    const mockedAuthResponse = Promise.resolve({
      data: expectedAuthInfo,
      status: 200,
    });
    const mockedTeamSubscriptionResponse = Promise.resolve({
      data: responseTeamInfo,
      status: 200,
    });
    const mockedTeamInfoResponse = Promise.resolve({
      data: responseTeamSubscription,
      status: 200,
    });
    const mockedTransfrormResponse = Promise.resolve({
      data: responseTranform,
      status: 200,
    });
    const mockedPlatformsResponse = Promise.resolve({
      data: responsePlatforms,
      status: 200,
    });
    const mockedSeedResponse = Promise.resolve({
      data: responseSeed,
      status: 200,
    });
    const mockedProjectsResponse = Promise.resolve({
      data: responseProjects,
      status: 200,
    });

    mockAxios.post.mockResolvedValue(mockedAuthResponse);
    mockAxios.get.mockImplementation((url) => {
      switch (url) {
        case "/team-info/":
          return mockedTeamInfoResponse;
        case "/team-subscription/":
          return mockedTeamSubscriptionResponse;
        case "/transform/":
          return mockedTransfrormResponse;
        case "/platforms/v2":
          return mockedPlatformsResponse;
        case "/seed/v2/":
          return mockedSeedResponse;
        case "/project-summary/":
          return mockedProjectsResponse;
        default:
          return mockedTeamSubscriptionResponse;
      }
    });

    const expectedActions = [
      {
        type: "LOG_IN",
        userId: "test@mail.com",
        teamInfo: undefined,
      },
      { type: "LOADING_TRANSFORMS" },
      { type: "STORE_TRANSFORMS", transforms: responseTranform },
      { type: "SET_PLATFORM_LOGOS", payload: responsePlatformLogos },
      { type: "LOADING_TEAM_INFO" },
      { type: "LOADING_PLATFORMS" },
      { type: "LOADING_PIPELINE_SEEDS" },

      {
        type: "LOAD_TEAM_INFO",
        teamInfo: {
          active: true,
          expires: "2099-12-24T17:21:28Z",
          subscription: "DEVELOPER",
        },
      },
      {
        type: "STORE_TEAM_INFO",
        payload: {
          name: "RaccoonTeam",
          cpu_usage_subscription: {
            credits_used: 0,
            credits: 0,
          },
        },
      },
      { type: "STORE_PLATFORMS", platforms: expectedPlatforms },
      { type: "STORE_PIPELINE_SEEDS", seeds: responseSeed },
      {
        type: "@@router/CALL_HISTORY_METHOD",
        payload: {
          args: [
            {
              pathname: "/",
              state: Object({
                isConfirmed: true,
              }),
            },
          ],
          method: "push",
        },
      },
      // { type: 'STORE_ACTIVE_VIEW', activeView: 0 }
    ];
    await store.dispatch(actions.logIn({ email, password }));

    expect(mockAxios.post).toBeCalledTimes(2); // 2nd for logger
    expect(mockAxios.get).toBeCalledTimes(5); // get common data
    const actionsToTest = store
      .getActions()
      .filter((el) => el.type !== "SET_IS_SHOW_BANNER_MAINTENANCE");
    expect(actionsToTest).toEqual(expectedActions);
  });

  it("should load team info", async () => {
    const expectedTeamInfo = {
      team: "Sensiml",
      subscription: "FREETRIAL",
      active: true,
      expires: null,
    };

    const mockedResponse = Promise.resolve({
      data: expectedTeamInfo,
    });

    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedAction = {
      type: LOAD_TEAM_INFO,
      teamInfo: expectedTeamInfo,
    };

    await actions.loadTeamInfo("dummyToken")(dispatch, getState);
    expect(dispatch).toBeCalledWith(expectedAction);
  });

  it("should logout", async () => {
    const expectedAction = {
      type: LOG_OUT,
    };
    await store.dispatch(actions.logOut());
    expect(store.getActions()[0]).toEqual(expectedAction);
  });
});
