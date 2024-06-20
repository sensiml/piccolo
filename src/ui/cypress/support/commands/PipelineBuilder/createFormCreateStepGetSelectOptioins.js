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

export default ({ selectorSelect, selectorOptions }) => {
  cy.log("collectOptions");
  let options = [];

  cy.get(selectorSelect).should("exist").click();
  cy.get(selectorOptions).each($el => { options.push($el.text()) })
    .then(() => {
      if (options?.length) {
        cy
          .get(`[data-value="${options[0]}"]`)
          .should("exist")
          .click();
      }
      // return options;
    });
};