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

/* eslint-disable no-unused-vars */
import React from "react";
import { Provider } from "react-redux";
import { PersistGate } from "redux-persist/integration/react";
import { I18nextProvider } from "react-i18next";
import { Switch, Route } from "react-router-dom";
import { ROUTES } from "routers";
import { ConnectedRouter } from "connected-react-router";

import Auth from "containers/Auth";
import Main from "./containers/Main";
import i18n from "./i18n";

import { store, persistor, history } from "store";

import AccountSettings from "containers/AccountSettings";
import { LightTheme } from "components/Themes";

if (window.Cypress) {
  window.__store__ = store;
}

const App = () => {
  return (
    <I18nextProvider i18n={i18n}>
      <Provider store={store}>
        <PersistGate loading={null} persistor={persistor}>
          <LightTheme>
            <ConnectedRouter history={history}>
              <Switch>
                <Route path={ROUTES.AUTH.path}>
                  <Auth />
                </Route>
                <Route path={ROUTES.ACCOUNT_SETTINGS.path}>
                  <AccountSettings />
                </Route>
                <Route path={ROUTES.MAIN.path}>
                  <Main />
                </Route>
              </Switch>
            </ConnectedRouter>
          </LightTheme>
        </PersistGate>
      </Provider>
    </I18nextProvider>
  );
};

export default App;
