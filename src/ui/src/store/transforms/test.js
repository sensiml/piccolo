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

import * as transformActions from "./actions";
import { STORE_TRANSFORMS, LOADING_TRANSFORMS } from "./actionTypes";
import "regenerator-runtime/runtime";
import mockAxios from "axios";

describe("transforms actions", () => {
  it("should fetch all tranforms", async () => {
    //mock setup
    const expectedTransforms = [
      { name: "PME", uuid: "9a213433-1406-41d8-ab45-1fc4ba6ab8a7" },
      {
        name: "Global Peak to Peak of Low Frequency",
        uuid: "391369b1-d92c-474d-8dd7-99960602e475"
      }
    ];
    const mockedResponse = Promise.resolve({ data: expectedTransforms });
    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();
    const expectedActions = [
      {
        type: LOADING_TRANSFORMS
      },
      {
        type: STORE_TRANSFORMS,
        transforms: expectedTransforms
      }
    ];
    await transformActions.loadTransforms()(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should log error when tranforms request fails", async () => {
    mockAxios.get.mockImplementation(() => {
      throw new Error("Some Error");
    });
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: LOADING_TRANSFORMS
      },
      {
        type: STORE_TRANSFORMS,
        transforms: []
      }
    ];

    await transformActions.loadTransforms()(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });
});
