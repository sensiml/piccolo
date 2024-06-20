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
      } else {
        resolse([]);
      }
    });

  });


};

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

describe("Auto test Pipeline builder", () => {
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

    it("should add all possible steps", () => {

      let usedOptions = [];

      getSteps().then(steps => {
        steps.forEach((stepDataCy) => {

          getStepWrapper(stepDataCy).then($stepWrapper => {

            if ($stepWrapper.find(`[data-test="ppl-step-add"]`).length) {

              cy.log("if step box has link to add new")
              cy.log("open create form")
              cy.wrap($stepWrapper).find(`[data-test="ppl-step-add"]`).first().should("exist").click();

              collectOptions({
                selectorFormWrapper: '[data-test="drawer-create-step-form"]',
                selectorSelect: '[data-testid="select-tranform"]',
                selectorOptions: '[data-test="select-tranform-option"]',
              })
                .then(options => {

                  cy
                    .log("close create form");
                  cy
                    .get(`[data-testid="new-step-drawer-close"]`).should("exist").click();
                  cy
                    .log("start create new step for each option");

                  options.filter(option => !usedOptions.includes(option)).forEach((option) => {
                    cy
                      .wait(300);
                    cy
                      .log("open create form");
                    cy
                      .wrap($stepWrapper).find(`[data-test="ppl-step-add"]`).first().should("exist").click();
                    cy
                      .createFormCreateStep(option);
                    cy
                      .wait(300);


                    collectOptions({
                      selectorFormWrapper: '[data-test="drawer-edit-step-form"]',
                      selectorSelect: '[id="top_level_select"]',
                      selectorOptions: '[role="option"]',
                    })
                      .then(transformOptions => {
                        if (transformOptions?.length) {
                          cy
                            .log("set first transform close form with first element");
                          cy
                            .editFormTransformSetTransform(transformOptions[0]);
                          cy
                            .log("start creating steps with the rest of transforms");

                          // transformOptions.forEach((transformOption, index) => {
                          //   cy
                          //     .wait(100);
                          //   if (index > 0) {
                          //     // open create form
                          //     cy
                          //       .wrap($stepWrapper).find(`[data-test="ppl-step-add"]`).first().should("exist").click();
                          //     cy
                          //       .createFormCreateStep(option);
                          //     cy
                          //       .editFormTransformSetTransform(transformOption);
                          //   }
                          // });

                        } else {
                          // for other form like Feature Selector
                          cy
                            .get('[data-testid="edit-step-form-submit"]').click();
                        }

                        usedOptions.push(option);
                    });

                  });
              });
            }

          });
        });
      });

    });


    it("should resaved data for all possible steps", () => {
      cy.wait(2000);
      getSteps().then(steps => {

        steps.forEach((stepDataCy) => {
          cy.log("iterate all ster wrappers");

          getStepWrapper(stepDataCy).then($stepWrapper => {

          if ($stepWrapper.find('[data-test="edit-link"]').length) {

            cy
              .log("if step box has link to edit")
            cy
              .log("open edit form")
            cy
              .wrap($stepWrapper)
              .find('[data-test="edit-link"]')
              .first()
              .should("exist")
              .click();

            cy
              .log("save with edit form");
            cy
              .get('[data-testid="edit-step-form-submit"]')
              .should("exist")
              .click();
          }

          });

        });

      });
    });

    it("logout", () => {
      cy.logout();
    });

  });
});