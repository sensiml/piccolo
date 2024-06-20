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

const TOKEN_KEY = "jwtToken";
const REFRESH_TOKEN_KEY = "jwtRefreshToken";
/*
 * Manage the flow of how Access Tokens are being stored, removed, and retrieved from storage.
 *
 * Current implementation stores to sessionStorage. Local Storage should always be
 * accessed through this instace.
 */
const TokenStorage = {
  isAuthenticated() {
    return Boolean(sessionStorage.getItem(TOKEN_KEY));
  },

  getToken() {
    return sessionStorage.getItem(TOKEN_KEY);
  },

  async saveToken(accessToken) {
    sessionStorage.setItem(TOKEN_KEY, accessToken);
    await Promise.resolve();
  },

  removeToken() {
    sessionStorage.removeItem(TOKEN_KEY);
  },

  getRefreshToken() {
    return sessionStorage.getItem(REFRESH_TOKEN_KEY);
  },

  saveRefreshToken(refreshToken) {
    sessionStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  },

  removeRefreshToken() {
    sessionStorage.removeItem(REFRESH_TOKEN_KEY);
  },
};

export default TokenStorage;
