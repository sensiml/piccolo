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

import React from "react";
import { Route, Switch, Redirect, generatePath } from "react-router-dom/cjs/react-router-dom.min";
import { Box, Container } from "@mui/material";

import { ROUTES } from "routers";
import AppBarAccountSettings from "components/Layout/AppBarAccountSettings";
import NavDrawerAccountSettings from "components/Layout/NavDrawerAccountSettings";
import RouterProxyAppMain from "components/Routers/RouterProxyAppMain";

import TheAccountInfo from "./TheAccountInfo";
import TheAccountSubscription from "./TheAccountSubscription";
import TheAccountAPIKeys from "./TheAccountAPIKeys";

import makeStyles from "@mui/styles/makeStyles";

const useStyles = () =>
  makeStyles((theme) => ({
    root: {
      display: "flex",
      minWidth: theme.responsive.minWidthContainer,
    },
    toolbar: {
      display: "flex",
      alignItems: "center",
      justifyContent: "flex-end",
      padding: theme.spacing(0, 1),
      ...theme.mixins.toolbar,
    },
    content: {
      boxSizing: "border-box",
      marginTop: theme.spacing(2),
      minHeight: "calc(100vh - 1rem)",
      padding: theme.spacing(2),
      width: "100%",
      paddingTop: "4rem",
    },
  }))();

const TheAccountSettings = () => {
  const classes = useStyles();

  return (
    <Box className={classes.root}>
      <AppBarAccountSettings />
      <NavDrawerAccountSettings isOpen isSmallScreen={false} />
      <main className={classes.content}>
        <Container maxWidth="lg">
          <Switch>
            <Route exact path={ROUTES.ACCOUNT_SETTINGS.child.ACCOUNT_INFO.path}>
              <RouterProxyAppMain>
                <TheAccountInfo />
              </RouterProxyAppMain>
            </Route>
            <Route exact path={ROUTES.ACCOUNT_SETTINGS.child.ACCOUNT_SUBCRIPTIONS.path}>
              <RouterProxyAppMain>
                <TheAccountSubscription />
              </RouterProxyAppMain>
            </Route>
            <Route exact path={ROUTES.ACCOUNT_SETTINGS.child.ACCOUNT_API_KEYS.path}>
              <RouterProxyAppMain>
                <TheAccountAPIKeys />
              </RouterProxyAppMain>
            </Route>
            <Redirect
              from={ROUTES.ACCOUNT_SETTINGS.path}
              to={{
                pathname: generatePath(ROUTES.ACCOUNT_SETTINGS.child.ACCOUNT_INFO.path),
              }}
            />
          </Switch>
        </Container>
      </main>
    </Box>
  );
};

export default TheAccountSettings;
