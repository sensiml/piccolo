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

/* eslint-disable react/jsx-filename-extension */
// Link.react.test.js
import React from "react";
import _ from "lodash";

import { renderWithTheme } from "tests";

import SliderNumberForm from "../SliderNumberForm";

describe("<SliderNumberForm/>", () => {
  const name = "slider_number";
  const defaultValue = 122;
  const defaultRange = [-200, 200];
  const id = "slider_number";

  it("Should called onChange with default value after mounted", () => {
    const handleChange = jest.fn();
    renderWithTheme(
      <SliderNumberForm
        id={id}
        name={name}
        range={defaultRange}
        onChange={handleChange}
        defaultValue={defaultValue}
      />,
    );
    // expect(handleChange).toHaveBeenCalled();
    expect(handleChange.mock.calls[0]).toEqual([name, defaultValue]);
  });

  it("Should set default value", () => {
    const handleChange = jest.fn();
    renderWithTheme(
      <SliderNumberForm id={id} name={name} range={defaultRange} onChange={handleChange} />,
    );
    // expect(handleChange).toHaveBeenCalled();
    expect(handleChange.mock.calls[0]).toEqual([name, _.divide(defaultRange[1], 2)]);
  });
});
