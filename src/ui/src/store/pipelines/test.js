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
import configureMockStore from "redux-mock-store";
import thunk from "redux-thunk";

import "regenerator-runtime/runtime";
import TokenStorage from "services/TokenStorage";

import api from "store/api";
import { exportPipeline } from "./actions";

// needs for MockAdapter
jest.unmock("axios");
const mockStore = configureMockStore([thunk]);

jest.mock("js-file-download", () => ({
  __esModule: true,
  default: (data, name) => name,
}));

// const fileDownload = import("js-file-download");

describe("Download pipeline", () => {
  const store = mockStore({
    pipelines: {
      pipelineList: {
        data: [
          {
            uuid: "2",
            name: "test",
            pipeline: [],
            hyper_params: {},
          },
        ],
      },
    },
  });

  // eslint-disable-next-line max-len
  it("should call 2 pipeline endpoind and download file with right endpoints", async () => {
    const mockResponseAdapter = new MockAdapter(api);

    mockResponseAdapter
      .onGet("/project/1/sandbox/2/python/")
      .replyOnce(200, {})
      .onGet("/project/1/sandbox/2/ipynb/")
      .replyOnce(200, {});

    await store.dispatch(exportPipeline("1", "2", "json"));
    await store.dispatch(exportPipeline("1", "2", "python"));
    await store.dispatch(exportPipeline("1", "2", "ipynb"));

    expect(mockResponseAdapter.history.get.length).toEqual(2);
  });
});
