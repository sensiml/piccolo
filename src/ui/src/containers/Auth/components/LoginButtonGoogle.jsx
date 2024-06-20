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

import React, { useCallback } from "react";

import { Button } from "@mui/material";
import IconSocialGoogle from "components/UIIcons/IconSocialGoogle";

import { OAUTH_GOOGLE_CLIENT_ID, OAUTH_GOOGLE_AUTH_URL, OAUTH_GOOGLE_REDIRECT_URL } from "config";

const ButtonLoginGoogle = ({ title }) => {
  const openLoginPage = useCallback(() => {
    const scope = [
      "https://www.googleapis.com/auth/userinfo.email",
      "https://www.googleapis.com/auth/userinfo.profile",
    ].join(" ");

    const params = {
      response_type: "code",
      client_id: OAUTH_GOOGLE_CLIENT_ID,
      redirect_uri: OAUTH_GOOGLE_REDIRECT_URL,
      prompt: "select_account",
      access_type: "offline",
      scope,
    };

    const urlParams = new URLSearchParams(params).toString();

    window.location = `${OAUTH_GOOGLE_AUTH_URL}?${urlParams}`;
  }, []);

  return (
    <Button
      onClick={openLoginPage}
      startIcon={<IconSocialGoogle />}
      variant="outlined"
      color="primary"
      fullWidth
    >
      {title}
    </Button>
  );
};

export default ButtonLoginGoogle;
