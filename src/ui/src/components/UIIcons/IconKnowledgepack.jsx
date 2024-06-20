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
/* eslint-disable max-len */
import React from "react";
import { SvgIcon } from "@mui/material";

export default ({ color, ...props }) => {
  return (
    <SvgIcon {...props}>
      <path d="M9.43498 0C7.55408 0 6.02952 1.5261 6.02952 3.40884C6.02952 4.33984 6.402 5.18418 7.00636 5.7994H2e-05V11.4808C0.6245 10.7586 1.5478 10.3007 2.57686 10.3007C4.45774 10.3007 5.98232 11.8267 5.98232 13.7095C5.98232 15.5922 4.45774 17.1183 2.57684 17.1183C1.5478 17.1183 0.6245 16.6603 0 15.9382V24H7.36C6.58172 23.3752 6.08336 22.416 6.08336 21.3397C6.08336 19.4569 7.60794 17.9309 9.48884 17.9309C11.3697 17.9309 12.8943 19.457 12.8943 21.3397C12.8943 22.416 12.3959 23.3752 11.6176 24H18.1827V16.8789C18.7993 17.4978 19.6523 17.8803 20.5945 17.8803C22.4754 17.8803 24 16.3542 24 14.4715C24 12.5887 22.4754 11.0627 20.5945 11.0627C19.6523 11.0627 18.7993 11.4452 18.1827 12.0641V5.79938H11.8636C12.4682 5.18412 12.8405 4.33996 12.8405 3.40882C12.8405 1.52608 11.3159 0 9.43498 0Z" />
    </SvgIcon>
  );
};
