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

import { React, useState } from "react";
import { Box } from "@mui/material";
import { useParams, useHistory, generatePath } from "react-router-dom";
import QueriesTable from "components/QueriesTable";
import ControlPanel from "components/ControlPanel";
import AddIcon from "@mui/icons-material/Add";
import { ROUTES } from "routers";
import { useWindowResize } from "hooks";
import { RESPONSIVE } from "consts";
import { UIButtonConvertibleToShort } from "components/UIButtons";

const TheQueryScreen = ({ onShowInformation }) => {
  // eslint-disable-next-line no-unused-vars
  const { projectUUID } = useParams();
  const routersHistory = useHistory();

  const [isShortBtnText, setIsShortBtnText] = useState(false);

  useWindowResize((data) => {
    setIsShortBtnText(data.innerWidth < RESPONSIVE.WIDTH_FOR_SHORT_TEXT);
  });

  const handleUpdateAction = () => {
    routersHistory.push({
      pathname: generatePath(ROUTES.MAIN.DATA_EXPLORER.child.QUERY_SCREEN.path, {
        projectUUID,
      }),
    });
  };

  const handleCreateQuery = () => {
    routersHistory.push({
      pathname: generatePath(ROUTES.MAIN.DATA_EXPLORER.child.QUERY_CREATE_SCREEN.path, {
        projectUUID,
      }),
    });
  };

  return (
    <>
      <Box mb={2}>
        <ControlPanel
          title={"Querying Data"}
          onShowInformation={onShowInformation}
          actionsBtns={
            <>
              <UIButtonConvertibleToShort
                variant={"outlined"}
                color={"primary"}
                onClick={() => handleCreateQuery()}
                isShort={isShortBtnText}
                tooltip={"Create a new query"}
                text={"Create Query"}
                icon={<AddIcon />}
              />
            </>
          }
        />
      </Box>
      <Box>
        <QueriesTable onUpdateProjectAction={handleUpdateAction} />
      </Box>
    </>
  );
};

export default TheQueryScreen;
