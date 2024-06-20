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

import React, { lazy, Suspense } from "react";
import ErrorBoundary from "components/ErrorBoundary";
import { Switch, Route, Redirect, generatePath, useParams } from "react-router-dom";
import { Box } from "@mui/material";

import { ROUTES } from "routers";

import TheQueryScreen from "./TheQueryScreen";

import { DataExplorerContext } from "./context";
import { AppLoader } from "components/UILoaders";

const TheQueryDetailScreen = lazy(() => import("./TheQueryDetailScreen"));
const TheQueryCreateScreen = lazy(() => import("./TheQueryCreateScreen"));

const TheDataExplorer = () => {
  const { projectUUID } = useParams();

  return (
    <ErrorBoundary>
      <Box>
        <Switch>
          <Route path={ROUTES.MAIN.DATA_EXPLORER.child.QUERY_SCREEN.path}>
            <DataExplorerContext.Provider>
              <TheQueryScreen />
            </DataExplorerContext.Provider>
          </Route>
          <Route path={ROUTES.MAIN.DATA_EXPLORER.child.QUERY_DETAILS_SCREEN.path}>
            <DataExplorerContext.Provider>
              <Suspense fallback={<AppLoader isOpen />}>
                <TheQueryDetailScreen />
              </Suspense>
            </DataExplorerContext.Provider>
          </Route>
          <Route path={ROUTES.MAIN.DATA_EXPLORER.child.QUERY_CREATE_SCREEN.path}>
            <DataExplorerContext.Provider>
              <Suspense fallback={<AppLoader isOpen />}>
                <TheQueryCreateScreen />
              </Suspense>
            </DataExplorerContext.Provider>
          </Route>
          <Route>
            <Redirect
              from={ROUTES.MAIN.DATA_EXPLORER.path}
              to={{
                pathname: generatePath(ROUTES.MAIN.DATA_EXPLORER.child.QUERY_SCREEN.path, {
                  projectUUID,
                }),
              }}
            />
          </Route>
        </Switch>
      </Box>
    </ErrorBoundary>
  );
};

export default TheDataExplorer;
