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

export const ASYNC_CECK_INTERVAL = process.env.REACT_APP_ASYNC_CHECK_INTERVAL || 5000;
export const SUPPORT_URL = process.env.REACT_SUPPORT_URL || "https://sensiml.com/support";

// AUTH
export const AUTH_CLIENT_ID = process.env.REACT_APP_AUTH_CLIENT_ID || "";
export const AUTH_CLIENT_SECRET = process.env.REACT_APP_AUTH_CLIENT_SECRET || "";
export const PROMO_LINK = process.env.REACT_APP_PROMO_LINK || "";
export const GETTING_STARTED_GUIDE_LINK = process.env.REACT_APP_GETTING_STARTED_GUIDE_LINK || "";

export const API_URL = process.env.REACT_APP_API_URL || "";

// OAUTH
const {
  REACT_APP_OAUTH_GOOGLE_CLIENT_ID,
  REACT_APP_OAUTH_GOOGLE_AUTH_URL,
  REACT_APP_OAUTH_GOOGLE_REDIRECT_URL,
} = process.env;

export const OAUTH_GOOGLE_CLIENT_ID = REACT_APP_OAUTH_GOOGLE_CLIENT_ID || "";
export const OAUTH_GOOGLE_AUTH_URL = REACT_APP_OAUTH_GOOGLE_AUTH_URL || "";
export const OAUTH_GOOGLE_REDIRECT_URL = REACT_APP_OAUTH_GOOGLE_REDIRECT_URL || "";
export const PLANS_LINK = process.env.REACT_APP_PLANS_LINK || "https://sensiml.com/plans/";
export const CHANGE_PASSWORD_LINK = process.env.REACT_APP_CHANGE_PASSWORD_LINK;
export const SUBSCRIPTION_LINK = process.env.REACT_APP_SUBSCRIPTION_URL;

export const FEATURE_SAMPLE_SIZE_LIMIT = 200;
