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
import * as captureActions from "./actions";
import { STORE_CAPTURES } from "./actionTypes";

import "regenerator-runtime/runtime";
import mockAxios from "axios";

describe("captures actions", () => {
  it("should fetch all captures for a project", async () => {
    //mock setup
    const expectedCaptures = [{ name: "test1" }, { name: "test2" }];
    const mockedResponse = Promise.resolve({ data: expectedCaptures });
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedAction = {
      type: STORE_CAPTURES,
      captures: expectedCaptures,
    };
    await captureActions.loadCaptures(projectUuid)(dispatch, getState);
    expect(dispatch).toBeCalledWith(expectedAction);
  });

  it("should 0 captures when projectUuid is not provided", async () => {
    const projectUuid = "";
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedAction = {
      type: STORE_CAPTURES,
      captures: [],
    };
    await captureActions.loadCaptures(projectUuid)(dispatch, getState);
    expect(dispatch).toBeCalledWith(expectedAction);
  });

  it("should log error when captures request fails", async () => {
    //mock setup
    mockAxios.get.mockImplementation(() => {
      throw new Error("Some Error");
    });
    const expectedCaptures = [{ name: "test1" }, { name: "test2" }];
    const mockedResponse = Promise.resolve({ data: expectedCaptures });
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedAction = {
      type: STORE_CAPTURES,
      captures: [],
    };
    await captureActions.loadCaptures(projectUuid)(dispatch, getState);
    expect(dispatch).toBeCalledWith(expectedAction);
  });
});
