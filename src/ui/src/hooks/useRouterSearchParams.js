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

import _ from "lodash";
import { useMemo } from "react";

import { useLocation, useHistory } from "react-router-dom";

const useRouterSearchParams = () => {
  const { search } = useLocation();
  const history = useHistory();

  const searchParams = useMemo(() => new URLSearchParams(search), [search]);

  const removeSearchParams = (params) => {
    /**
     * @param {string[]} params
     */
    if (searchParams?.has && _.isArray(params)) {
      params.forEach((param) => {
        if (searchParams.has(param)) {
          searchParams.delete(param);
        }
      });
      history.replace({
        search: searchParams.toString(),
      });
    }
  };

  return [searchParams, removeSearchParams];
};

export default useRouterSearchParams;
