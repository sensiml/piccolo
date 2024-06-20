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
// Link.react.test.js
import React from "react";

import InputArrayString from "../InputArrayString";

import { screen, fireEvent } from "@testing-library/react";
import { renderWithTheme } from "tests";

describe("Testing InputArrayString component", () => {
  const name = "input_number";
  const defaultValue = ["Hello World", "add", "edit"];
  const newValue = "HelloWorld1, add1, edit1";

  const inputValidValues = [
    { input: "add, edit", expect: ["add", "edit"] },
    { input: "add, edit,", expect: ["add", "edit"] },
    { input: "add, edit  ", expect: ["add", "edit"] },
    { input: "add,  edit,", expect: ["add", "edit"] },
    { input: "add,edit", expect: ["add", "edit"] },
  ];

  const inputInvalidValues = [
    { input: "add, edit..", expect: [] },
    { input: "add, edit,,", expect: [] },
    { input: "add,, edit  ", expect: [] },
    { input: ",,  edit,", expect: [] },
    { input: "add;,edit", expect: [] },
  ];

  const id = "input_number";

  it("Should called onChange with default value after mounted", () => {
    const handleChange = jest.fn();
    renderWithTheme(
      <InputArrayString id={id} name={name} onChange={handleChange} defaultValue={defaultValue} />,
    );
    expect(handleChange).toHaveBeenCalled();
    expect(handleChange.mock.calls[0]).toEqual([name, defaultValue]);
  });

  describe("InputArrayString valid cases", () => {
    inputValidValues.forEach((inputEl) => {
      it(`${inputEl.input} - should be correct value`, () => {
        const mockHandleChange = jest.fn();
        renderWithTheme(
          <InputArrayString
            id={id}
            name={name}
            onChange={mockHandleChange}
            defaultValue={defaultValue}
            label="test_label"
          />,
        );
        const input = screen.getByLabelText("test_label", { selector: "input" });
        fireEvent.change(input, { target: { value: inputEl.input } });
        fireEvent.blur(input);
        expect(mockHandleChange.mock.calls[1]).toEqual([name, inputEl.expect]);
      });
    });
  });

  describe("InputArrayString invalid cases", () => {
    inputInvalidValues.forEach((inputEl) => {
      it(`${inputEl.input} - should be incorrect value`, () => {
        const mockHandleChange = jest.fn();
        renderWithTheme(
          <InputArrayString
            id={id}
            name={name}
            onChange={mockHandleChange}
            defaultValue={defaultValue}
            label="test_label"
          />,
        );
        const input = screen.getByLabelText("test_label", { selector: "input" });
        fireEvent.change(input, { target: { value: inputEl.input } });
        fireEvent.blur(input);
        // only called for default
        expect(mockHandleChange).toBeCalledTimes(1);
        expect(screen.getByText("array-field.error-validation")).toBeInTheDocument();
      });
    });
  });
});
