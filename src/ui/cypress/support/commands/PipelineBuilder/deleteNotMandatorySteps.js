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


export default (pplSteps) => {
  pplSteps.forEach(async (stepDataCy) => {
    cy.log("iterate all ster wrappers");

    // const $stepWrapper = await
    cy
      .get(`[data-cy="${stepDataCy}"]`)
      .should("exist")
      .then($stepWrapper => {
        if ($stepWrapper.find('[data-test="delete-link"]').length) {
          // 
          cy.log("if step box has link to delete")
          cy.wrap($stepWrapper).find('[data-test="delete-link"]').first().should("exist").click();
          cy.log("confirm at dialog");
          cy.wait(200);
          cy.get(`[data-testid="dialog-confirm-confirm"]`).should("exist").focus().click();
        }
      });
  });
};
