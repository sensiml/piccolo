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

// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add("login", (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })

import projectDefaultOpen from "./projectDefaultOpen";
import projectOpenByName from "./projectOpenByName";
import storeGetState from "./storeGetState";

import {
  createFormCreateStep,
  editFormTransformSetTransform,
  deleteNotMandatorySteps,
} from "./PipelineBuilder";

Cypress.Commands.add("openDefaultProject", projectDefaultOpen);
Cypress.Commands.add("OpenProjectByName", projectOpenByName);
Cypress.Commands.add("getState", storeGetState);

Cypress.Commands.add("createFormCreateStep", createFormCreateStep);
Cypress.Commands.add("editFormTransformSetTransform", editFormTransformSetTransform);
Cypress.Commands.add("deleteNotMandatorySteps", deleteNotMandatorySteps);

// Cypress.on('fail', (err) => {
//   cy.screenshot().then(el => {
//     cy.log("screenshot");
//   });
//   debugger;
//   throw err
// });

Cypress.Commands.add("authorizeOnSite", () => {
  cy.viewport(1960, 1080);
  if (Cypress.env("name") === "localhost") {
    cy.visit("/");
  } else {
    cy.visit("/", {
      auth: {
        username: "sensiml",
        password: "TinyML4Life",
      },
    });
  }
});

Cypress.Commands.add("login", () => {
  cy.authorizeOnSite();
  cy.get("body").then(($body) => {
    if (!$body.find('[id="loginId"]').length) {
      cy.get('[id="email"]').type(Cypress.env("user"));
      cy.get('[id="password"]').type(Cypress.env("password"));
      cy.get('[id="loginButton"]').click();
      cy.wait(5000);
    }
  });
});

Cypress.Commands.add("logout", () => {
  cy.get("body").then(($body) => {
    if ($body.find('[id="loginId"]').length) {
      cy.get('[id="loginId"]').click();
      cy.get('[id="logoutButton"]').click();
    }
  });
});

Cypress.Commands.add("checkPageHeader", (customHeader) => {
  cy.get('[id="headerTitle"]')
    .should("exist")
    .should("have.text", customHeader || Cypress.env("headerTitle"));
});

Cypress.Commands.add(
  "validateTableFooter",
  (tableId, expectedCaptions, expectedButtons) => {
    cy.get(`[id="${tableId}"]`)
      .find("tr", "MuiTableRow-footer")
      .find("div", "MuiTablePagination-toolbar")
      .then((toolbar) => {
        cy.wrap(toolbar)
          .find("p", "MuiTablePagination-caption")
          .then((captions) => {
            expectedCaptions.map((captionName, captionIndex) =>
              cy.wrap(captions[captionIndex]).should("have.text", captionName)
            );
          });
        cy.wrap(toolbar)
          .find("button")
          .then((buttons) => {
            expectedButtons.map((expectedButton) => {
              cy.wrap(buttons[expectedButton.index])
                .should(
                  `${expectedButton.enabled ? "not." : ""}have.class`,
                  "Mui-disabled"
                )
                .should("have.attr", "aria-label", expectedButton.label);
            });
          });
      });
  }
);

Cypress.Commands.add("validateTableHeader", (tableId, columns) => {
  columns.map((colItem) => {
    if (colItem.name === "" || !colItem.sortable) {
      cy.get(`[id="${tableId}"]`)
        .find("th")
        .eq(colItem.index)
        .should("have.text", colItem.name);
    } else {
      cy.get(`[id="${tableId}"]`)
        .find("th")
        .eq(colItem.index)
        .contains("span", colItem.name);
    }
  });
});

Cypress.Commands.add(
  "validateTableRows",
  (tableId, columns, rows, rowOrder) => {
    if (!rowOrder) {
      rowOrder = [];
      rows.map((x, i) => rowOrder.push(i));
    }
    cy.get(`[id="${tableId}"]`)
      .find("tr")
      .then((tableRows) => {
        rows.map((row, rowIndex) => {
          cy.wrap(tableRows[rowIndex + 1])
            .find("td")
            .then((tableCols) => {
              rows[rowOrder[rowIndex]].map((colValue, colIndex) => {
                if (columns[colIndex].isAction) {
                  cy.wrap(tableCols[colIndex])
                    .find("button")
                    .eq(0)
                    .should("have.attr", "title", colValue);
                } else {
                  cy.wrap(tableCols[colIndex]).should("have.text", colValue);
                }
              });
            });
        });
      });
  }
);

Cypress.Commands.add("validateTableSort", (tableId, columns, rows) => {
  ["asc", "desc"].map((ord) => {
    columns.map((column) => {
      if (column.isAction || !column.sortable) return;
      cy.get(`[id="${tableId}"]`)
        .find("th")
        .eq(column.index)
        .find("span", "MuiTableSortLabel-root")
        .then((colHeader) => {
          if (ord === "asc") cy.wrap(colHeader).click();
          else cy.wrap(colHeader).dblclick();
        });

      cy.get(`[id="${tableId}"]`)
        .find("th")
        .eq(2)
        .find(
          "svg",
          ord === "asc"
            ? "MuiTableSortLabel-iconDirectionAsc"
            : "MuiTableSortLabel-iconDirectionDesc"
        )
        .find("path")
        .should("have.attr", "d");

      cy.validateTableRows(
        tableId,
        columns,
        rows,
        ord === "asc" ? column.ascRowOrder : column.descRowOrder
      );
    });
  });
});


Cypress.Commands.add("openBuildModelPage", () => {
  cy.get(`[id="navBuildModel"]`).should("exist").click();
});