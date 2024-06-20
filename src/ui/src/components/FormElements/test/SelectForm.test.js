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

import { screen, fireEvent, within } from "@testing-library/react";
import { renderWithTheme } from "tests";

import SelectForm from "../SelectForm";

describe("<SelectForm/>", () => {
  const name = "sec_level_select";
  const options = [
    { value: "red", name: "Red" },
    { value: "green", name: "Green" },
    { value: "blue", name: "Blue" },
  ];
  const defaultValue = "red";
  const id = "sec_level_select";

  it("Should called onChange with default value after mounted", () => {
    const handleChange = jest.fn();
    renderWithTheme(
      <SelectForm
        id={id}
        name={name}
        onChange={handleChange}
        options={options}
        defaultValue={defaultValue}
      />,
    );
    expect(handleChange).toHaveBeenCalled();
    expect(handleChange.mock.calls[0]).toEqual([name, defaultValue]);
  });

  it("Should call onChange props with all options", async () => {
    const handleChange = jest.fn();
    renderWithTheme(
      <SelectForm
        id={id}
        name={name}
        onChange={handleChange}
        options={options}
        data-testid="test-select"
      />,
    );

    fireEvent.mouseDown(screen.getByRole("combobox"));
    const listbox = within(screen.getByRole("listbox"));

    fireEvent.click(listbox.getByText(options[0].name));
    fireEvent.click(listbox.getByText(options[1].name));
    fireEvent.click(listbox.getByText(options[2].name));

    expect(handleChange.mock.calls[0]).toEqual([name, options[0].value]);
    expect(handleChange.mock.calls[1]).toEqual([name, options[1].value]);
    expect(handleChange.mock.calls[2]).toEqual([name, options[2].value]);
  });
});
