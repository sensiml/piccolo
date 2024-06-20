## e2e testing cypress

---
 We use [cypress](cypress.io)

### Install dependensies

---
Please following instruction at [cypress instalation](https://docs.cypress.io/guides/getting-started/installing-cypress#System-requirements)

### Run locally

---

- `yarn cypress` or `npm cypress` will open your cypress dashboard (requaried lounched dev server)

- `yarn cyheadless` or `npm cyheadless` will launch cypress tests with console (requaried lounched dev server)

- `yarn test-e2e` or `npm test-e2e` will launch all cypress tests with console (not requaried lounched dev server)

### Configure cypress

---
configuration file stored at `./cypress/support/index.js`

### Add new tests

---

- At `./cypress/integration/*` find rigth folder and add your test with `*.spec.js` extention.

  - If you can't find best folder for your test, you can create your own.

- Commands it needs use reusable code we can use `commands`:
  - at `support/commands` create file/module with your commands
  - import all new commands to  `support/commands/index.js` and registeg that with `Cypress.Commands.add(youCommand)`

### Integration 

---
We use amplify resuorces to run e2e tests before deploy `amplify.yml`

``` yaml
test:
  phases:
    preTest:
      commands:
        - npm install
        - npm install wait-on
        - npm install pm2
        - npm install mocha@5.2.0 mochawesome mochawesome-merge mochawesome-report-generator
        - npx pm2 start npm -- start
        - 'npx wait-on http://localhost:3000'
    test:
      commands:
        - 'npx cypress run --reporter mochawesome --reporter-options "reportDir=cypress/report/mochawesome-report,overwrite=false,html=false,json=true,timestamp=mmddyyyy_HHMMss"'
    postTest:
      commands:
        - npx mochawesome-merge cypress/report/mochawesome-report/mochawesome*.json > cypress/report/mochawesome.json
        - npx pm2 kill
  artifacts:
    baseDirectory: cypress
    configFilePath: '**/mochawesome.json'
    files:
      - '**/*.png'
      - '**/*.mp4'
```
