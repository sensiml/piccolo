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

import { screen, fireEvent } from "@testing-library/react";
import { renderWithTheme } from "tests";

import InputNumberForm from "../InputNumberForm";

describe("<InputNumberForm/>", () => {
  const name = "input_number";
  const defaultValue = 100;
  const id = "input_number";

  it("Should called onChange with default value after mounted", () => {
    const handleChange = jest.fn();
    renderWithTheme(
      <InputNumberForm id={id} name={name} onChange={handleChange} defaultValue={defaultValue} />,
    );
    expect(handleChange).toHaveBeenCalled();
    expect(handleChange.mock.calls[0]).toEqual([name, defaultValue]);
  });

  describe("Changing <SliderNumberForm/>", () => {
    const handleChange = jest.fn();
    let wrapper;

    it("Should call onChange props with all options", () => {
      renderWithTheme(
        <InputNumberForm
          id={id}
          name={name}
          onChange={handleChange}
          label="test_label"
          defaultValue={defaultValue}
        />,
      );

      const input = screen.getByDisplayValue(defaultValue);
      fireEvent.change(input, { target: { value: _.divide(defaultValue, 2) } });
      fireEvent.blur(input);
      expect(handleChange.mock.calls[0]).toEqual([name, defaultValue]);
      expect(handleChange.mock.calls[1]).toEqual([name, _.divide(defaultValue, 2)]);
    });
  });
});
