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

import React, { useMemo } from "react";
import ErrorBoundary from "components/ErrorBoundary";

import { Box } from "@mui/material";
import { Switch, Route, Redirect, generatePath, useLocation } from "react-router-dom";

import { ROUTES } from "routers";
import { BannerMaintenance } from "components/Banners";

import LoginForm from "./Login";
import TheOAuthCallback from "./TheOAuthCallback";

const Auth = ({ logIn, logInOauthCallback }) => {
  const { state } = useLocation();
  const isInMaintenanceRange = useMemo(() => {
    const now = new Date();
    const start = new Date("2023-05-15T20:00:00-07:00");
    const end = new Date("2023-05-15T21:00:00-07:00");

    return now >= start && now < end;
  }, []);

  return (
    <Box>
      <Switch>
        <Route path={ROUTES.AUTH.child.LOGIN.path}>
          {isInMaintenanceRange ? (
            <BannerMaintenance
              isAfterLogin={false}
              // eslint-disable-next-line max-len
              text="Our servers are temporarily unavailable due to scheduled maintenance from 8:00 PM to 9:00 PM PST. We apologize for any inconvenience caused and appreciate your patience!"
            />
          ) : null}

          <ErrorBoundary>
            <LoginForm logIn={logIn} isDisableLogin={isInMaintenanceRange} />
          </ErrorBoundary>
        </Route>
        <Route path={ROUTES.AUTH.child.OAUTH_CALLBACK.path}>
          <ErrorBoundary>
            <TheOAuthCallback logInOauthCallback={logInOauthCallback} />
          </ErrorBoundary>
        </Route>
        <Route>
          <Redirect
            from={ROUTES.AUTH.path}
            to={{
              pathname: generatePath(ROUTES.AUTH.child.LOGIN.path),
              state,
            }}
          />
        </Route>
      </Switch>
    </Box>
  );
};

export default Auth;
