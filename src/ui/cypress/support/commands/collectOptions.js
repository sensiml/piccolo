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

const collectOptions = ({ selectorFormWrapper, selectorSelect, selectorOptions }) => {

  const getOptions = (selectorOptions) => {
    return new Cypress.Promise((resolve, reject) => {
      const options = [];
      cy
        .get(selectorOptions)
        .each($el => { options.push($el.text()) })
        .then(() => {
          resolve(options);
        });
    })
  };

  return new Cypress.Promise((resolse, reject) => {

    cy.get(selectorFormWrapper).then($form => {
      if ($form.find(selectorSelect).length) {
        cy
          .get(selectorSelect).should("exist").click();
        getOptions(selectorOptions).then(options => {
          if (options?.length) {
            cy.log(options)
            cy
              .get(`[data-value="${options[0]}"]`)
              .should("exist")
              .click();
          }
          resolse(options);
        });
      }
    });

  });

};

export default collectOptions;