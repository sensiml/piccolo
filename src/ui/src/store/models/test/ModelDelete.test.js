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

import MockAdapter from "axios-mock-adapter";
import { deleteModel } from "store/models/actions";
import api, { BaseAPIError } from "store/api";
import configureMockStore from "redux-mock-store";
import thunk from "redux-thunk";

// needs for MockAdapter
jest.unmock("axios");

const mockStore = configureMockStore([thunk]);

describe("models delete actions", () => {
  let store;
  beforeEach(() => {
    store = mockStore({});
  });
  const mockResponseAdapter = new MockAdapter(api);
  const modelUUID = "1";

  const reponseSuccess = {};
  const reponseFailedNotFound = {
    detail: "Not found.",
    status: 404,
  };

  mockResponseAdapter
    // ut to date
    .onDelete(`/knowledgepack/${modelUUID}/`)
    .replyOnce(204, reponseSuccess)
    // out of sync
    .onDelete(`/knowledgepack/${modelUUID}/`)
    .replyOnce(404, reponseFailedNotFound)
    .onDelete(`/knowledgepack/${modelUUID}/`)
    .abortRequest();

  it("delete model ", async () => {
    //mock setup
    try {
      await store.dispatch(deleteModel(modelUUID));
      expect(true).toEqual(true);
    } catch {
      expect(true).toEqual(false);
    }
  });

  it("delete model should throw error Base API error", async () => {
    //mock setup
    const errorResponse = { status: 404, data: { detail: "Not found.", status: 404 } };
    try {
      await store.dispatch(deleteModel(modelUUID));
    } catch (error) {
      expect(error).toEqual(new BaseAPIError(404, errorResponse));
      expect(error.message).toEqual(errorResponse.data.detail);
    }
  });

  it("delete model request wt connection", async () => {
    try {
      await store.dispatch(deleteModel(modelUUID));
    } catch (error) {
      console.log(error, error.message);
      expect(error.errorCode).toEqual(new BaseAPIError(503).errorCode);
    }
  });
});
