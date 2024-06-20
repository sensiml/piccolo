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

import { Menu, MenuItem } from "@mui/material";
import { PIPELINE_CONSTS } from "consts";

const PipelineExportMenu = ({ archorEl, isOpen, onClose, onDownloadPipeline }) => {
  const { DOWNLOAD_TYPES } = PIPELINE_CONSTS;

  return (
    <Menu
      id="menu-appbar"
      anchorEl={archorEl}
      open={isOpen}
      onClose={() => onClose()}
      MenuListProps={{
        "aria-labelledby": "pipeline-export-menu",
      }}
    >
      <MenuItem onClick={(_e) => onDownloadPipeline(DOWNLOAD_TYPES.JSON)}>Export as JSON </MenuItem>
      <MenuItem onClick={(_e) => onDownloadPipeline(DOWNLOAD_TYPES.PYTHON)}>
        Export as Python
      </MenuItem>
      <MenuItem onClick={(_e) => onDownloadPipeline(DOWNLOAD_TYPES.IPYNB)}>
        Export as IPYNB
      </MenuItem>
    </Menu>
  );
};

export default PipelineExportMenu;
