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
import React, { useEffect } from "react";
import { useCookies } from "react-cookie";
import { useHistory } from "react-router-dom";
import { Box } from "@mui/material";

import AppLoader from "components/UILoaders/AppLoader";
import { useRouterSearchParams } from "hooks";

import { ROUTES } from "routers";

const TheOAuthCallback = ({ logInOauthCallback }) => {
  const [searchParams] = useRouterSearchParams();
  const routersHistory = useHistory();

  const [cookies, _setCookie, removeCookie] = useCookies();

  const redirectWithError = (errorMessage) => {
    routersHistory.push({
      pathname: ROUTES.AUTH.child.LOGIN.path,
      search: `?error=${errorMessage}`,
    });
  };

  useEffect(() => {
    if (searchParams && !searchParams.get("error") && cookies?.email && cookies?.token) {
      try {
        logInOauthCallback({
          email: cookies.email,
          refreshToken: cookies.refresh_token,
          accessToken: cookies.token,
        });
        removeCookie("email", { path: "/" });
        removeCookie("refresh_token", { path: "/" });
        removeCookie("token", { path: "/" });
      } catch (error) {
        redirectWithError(error.message);
      }
    } else if (searchParams && searchParams.get("error")) {
      redirectWithError(searchParams.get("error"));
    } else {
      redirectWithError("Something went wrong during login throw the OAuth service");
    }
  }, [searchParams]);

  return (
    <Box style={{ height: "100vh" }}>
      <AppLoader isOpen message={"Loading profile information ..."} />
    </Box>
  );
};

export default TheOAuthCallback;
