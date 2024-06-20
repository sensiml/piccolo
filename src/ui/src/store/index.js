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

import thunk from "redux-thunk";
// eslint-disable-next-line import/no-extraneous-dependencies
import { createBrowserHistory } from "history";
import { routerMiddleware } from "connected-react-router";

import { createStore, applyMiddleware } from "redux";
import { composeWithDevTools } from "redux-devtools-extension";
import { persistStore, persistReducer } from "redux-persist";
import storage from "redux-persist/lib/storage/session";
import rootReducer from "./reducers";

const history = createBrowserHistory();

const persistConfig = {
  key: "sensiml-projects",
  storage,
  blackList: ["captureLabels"],
};

const middleware = [routerMiddleware(history), thunk];

// eslint-disable-next-line no-unused-vars
const enhancers = [];

const composedEnhancers = composeWithDevTools(applyMiddleware(...middleware));

const emptyBase = () => {}; // uses for test envirement

const persistedReducer = persistReducer(persistConfig, rootReducer(history) || emptyBase);

const store = createStore(persistedReducer, composedEnhancers);

const persistor = persistStore(store);

export { store, persistor, history };
