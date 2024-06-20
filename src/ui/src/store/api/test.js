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
// eslint-disable-next-line import/no-extraneous-dependencies
import MockAdapter from "axios-mock-adapter";
import "regenerator-runtime/runtime";
import TokenStorage from "services/TokenStorage";
import api, { setAuthHeader } from "./index";

// jest.mock("axios");
jest.unmock("axios");

const TEST_TOKEN = "test_token";
const TEST_UPDATED_TOKEN = "test_token_1";

const REFRESH_UPDATED_TOKEN = "test_refresh_token1";

describe("Test api instance", () => {
  beforeEach(async () => {
    await TokenStorage.saveToken(TEST_TOKEN);
    setAuthHeader(TEST_TOKEN);
  });

  it("should set token and set to headers", async () => {
    expect(TokenStorage.getToken()).toEqual(TEST_TOKEN);
    expect(api.defaults.headers.common.Authorization).toEqual(`Bearer ${TEST_TOKEN}`);
  });

  // eslint-disable-next-line max-len
  it("should refresh token once, resent all paralell request and set upadted toke to session storage ", async () => {
    const mockResponseAdapter = new MockAdapter(api);

    const expectedRefreshInfo = {
      expires_in: 36000,
      access_token: TEST_UPDATED_TOKEN,
      refresh_token: REFRESH_UPDATED_TOKEN,
      scope: "kb.data kb.pipeline",
      token_type: "Bearer",
    };

    const responseTeamInfo = {
      active: true,
      expires: "2099-12-24T17:21:28Z",
      subscription: "DEVELOPER",
    };

    const responseTeamInfoTokenExpired = {
      detail: "Authentication credentials were not provided.",
    };

    mockResponseAdapter
      // scope should be sent at one time with expired token reponse
      .onGet("/team-subscription/")
      .replyOnce(403, responseTeamInfoTokenExpired)

      .onGet("/team-subscription-1/")
      .replyOnce(403, responseTeamInfoTokenExpired)

      .onGet("/team-subscription-2/")
      .replyOnce(403, responseTeamInfoTokenExpired)

      .onGet("/team-subscription-3/")
      .replyOnce(403, responseTeamInfoTokenExpired)

      // scope should resent request
      .onGet("/team-subscription/")
      .replyOnce(200, responseTeamInfo)

      .onGet("/team-subscription-1/")
      .replyOnce(200, responseTeamInfo)

      .onGet("/team-subscription-2/")
      .replyOnce(200, responseTeamInfo)

      .onGet("/team-subscription-3/")
      .replyOnce(200, responseTeamInfo)

      .onPost("/oauth/token/")
      .reply(200, expectedRefreshInfo);

    const makeRequests = async () => {
      await Promise.all([
        api.get("/team-subscription/"),
        api.get("/team-subscription-1/"),
        api.get("/team-subscription-2/"),
        api.get("/team-subscription-3/"),
      ]);
    };

    await makeRequests();

    expect(TokenStorage.getToken()).toEqual(TEST_UPDATED_TOKEN);
    expect(api.defaults.headers.common.Authorization).toEqual(`Bearer ${TEST_UPDATED_TOKEN}`);

    // starting after 4th request should be resend with updated token
    // change for all 8 looks like it's bug in libary, they devs use 1 var
    mockResponseAdapter.history.get.forEach((reqObj, index) => {
      if (index > 4) {
        expect(reqObj?.headers?.Authorization).toEqual(`Bearer ${TEST_UPDATED_TOKEN}`);
      }
    });

    // we send 4 expired request and resend 4 new, after updating with 1 refresh request
    expect(mockResponseAdapter.history.get.length).toEqual(8); // 4 send and 4 resend
    expect(mockResponseAdapter.history.post.length).toEqual(1); // only 1 update
  });
});
