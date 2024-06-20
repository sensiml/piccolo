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

import * as plotActions from "./actions";
import { STORE_PLOTS, STORE_PLOT } from "./actionTypes";
import "regenerator-runtime/runtime";

describe("plots actions", () => {
  it("should get all the plots", () => {
    const expectedAction = {
      type: STORE_PLOTS,
      plots: [
        { id: "segment", name: "Segment" },
        { id: "samples", name: "Samples" }
      ]
    };
    expect(plotActions.loadPlots()).toEqual(expectedAction);
  });

  it("should set the plot in the store", async () => {
    const expectedPlotId = "segment";
    const expectedAction = {
      type: STORE_PLOT,
      plotId: expectedPlotId
    };
    const dispatch = jest.fn();
    const getState = jest.fn();
    await plotActions.setPlot(expectedPlotId)(dispatch, getState);
    expect(dispatch).toBeCalledWith(expectedAction);
  });
});
