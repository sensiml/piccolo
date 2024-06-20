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

// import data from "fixtures/"

const getSteps = () => {
  return new Cypress.Promise((resolve, reject) => {
    const pplSteps = [];
    cy
      .get(`[data-test="ppl-step-wapper"]`)
      .each($els => { pplSteps.push($els.data('cy')) })
      .then(() => {
        resolve(pplSteps);
      });
  });
};

const getStepWrapper = (stepDataCy) => {
  return new Cypress.Promise((resolve, reject) => {
    cy.get(`[data-cy="${stepDataCy}"]`).then(stepWrapper => (
      resolve(stepWrapper)
    ));
  });
};

describe("simple Pipeline builder", () => {
  let pplUUID = "";

  before(() => {
    cy.fixture("PipelineBuilderUserTests/projectData.json").then(data => {
      pplUUID = data.pipelineUUID;
      cy
        .login();
      cy
        .OpenProjectByName(data.project);
      cy
        .get(`[id="navBuildModel"]`)
        .should("exist")
        .click();
      cy
        .wait(3000);
    });

  });

  context("add, delete, edit all steps", () => {
    let state;
    let pplToAdd = [];
    let refPipelineList = [];

    before(() => {
      cy.fixture("PipelineBuilderUserTests/simplePipelineDataStepsToAdd.json").then(data => {
        pplToAdd = data;
      });

      cy.fixture("PipelineBuilderUserTests/simplePipelineReferenceData.json").then(data => {
        refPipelineList = data;
      });
      cy
        .window().should('have.property', '__store__');
    });

    beforeEach(() => {
      cy
        .viewport(1960, 1080);
      cy
        .wait(1000);
    });

    it("should delete all not madantory steps", () => {
      getSteps().then(steps => {
        cy
          .deleteNotMandatorySteps(steps);
      });
    });

    it("should add needed steps", () => {
      // pplSteps = [];
      
      getSteps()
        .then(steps => {
          steps.forEach((stepName) => {
           
            const pplToAddCurrent = pplToAdd.filter(step => step.parent_type === stepName);

            if (pplToAddCurrent?.length) {
              getStepWrapper(stepName).then($stepWrapper => {

                pplToAddCurrent.forEach(ppl => {
                  cy.log("ppl", ppl);
                  cy.wrap($stepWrapper).find(`[data-test="ppl-step-add"]`).first().should("exist").click();
                  cy.createFormCreateStep(ppl.type);
                  if (ppl.transform) {
                    cy.editFormTransformSetTransform(ppl.transform);
                  } else {
                    cy.get('[data-testid="edit-step-form-submit"]').click();
                  }
                });

              });
            }
        });
      });

    });

    it("should be", async () => {
      cy
        .window().should('have.property', '__store__');
      state = await cy
        .window()
        .its('__store__')
        .invoke('getState')
        .then(state => state)
        .promisify();
      cy
        .wait(1000);
      cy
        .log(JSON.stringify(state.containerBuildModel.pipelineStepData[pplUUID], undefined, 2));
      cy
        .wrap(JSON.stringify(state.containerBuildModel.pipelineStepData[pplUUID], undefined, 2))
        .should('deep.equal', refPipelineList);
    });

    it("logout", () => {
      cy.logout();
    });

  });
});