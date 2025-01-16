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

import React, { useState, useMemo, useEffect, lazy, Suspense } from "react";
import _ from "lodash";

import { useTranslation } from "react-i18next";
import {
  Switch,
  Route,
  Redirect,
  generatePath,
  useParams,
  useHistory,
  useLocation,
} from "react-router-dom";
import { Box } from "@mui/material";

import DialogTableSelect from "components/UIDialogTableSelect";

import { ROUTES } from "routers";

import { useRouterSearchParams, useMainContext, useReadFileText } from "hooks";

import TheCapturesScreen from "./TheCapturesScreen";

import { DataManagerContext } from "./context";
import { AppLoader } from "components/UILoaders";
import infoFile from "i18n/locales/en/info-data-manager.md";

// Lazy loading optional screen
const TheCaptureDetailsScreen = lazy(() => import("./TheCaptureDetailsScreen"));

const TheDataManager = ({
  sessions,
  selectedSessionUUID,
  isDemoTeam,
  setSelectedSession,
  loadSessions,
}) => {
  const routersHistory = useHistory();
  const [search] = useRouterSearchParams();

  const locationPath = useLocation();
  const { projectUUID } = useParams();
  const { t } = useTranslation("data-manager");

  const { showInformationWindow } = useMainContext();
  const screenInfoMd = useReadFileText(infoFile);

  const sessionsToSelect = useMemo(() => {
    return sessions.map((session) => ({
      ...session,
      isSelected: session.uuid === selectedSessionUUID,
    }));
  }, [sessions, selectedSessionUUID]);

  const selectedSession = useMemo(() => {
    return sessions.find((el) => el.uuid === selectedSessionUUID);
  }, [sessions, selectedSessionUUID]);

  const isDisabledByAutoSession = useMemo(() => {
    return selectedSession?.custom === false;
  }, [selectedSession]);

  const isReadOnlyMode = useMemo(() => {
    return isDemoTeam;
  }, [isDemoTeam]);

  const [isOpenSelectSessionDialog, setIsOpenSelectSessionDialog] = useState(false);

  const handleOpenSelectSessionDialog = () => {
    setIsOpenSelectSessionDialog(true);
  };

  const handleCloseSelectSessionDialog = () => {
    setIsOpenSelectSessionDialog(false);
  };

  const handleSelectSession = (_sessionUUID) => {
    search.set("session", _sessionUUID);
    routersHistory.replace({
      search: search.toString(),
    });
    handleCloseSelectSessionDialog();
  };

  useEffect(() => {
    const searchSession = search.get("session");
    if (searchSession && searchSession !== selectedSessionUUID) {
      setSelectedSession(searchSession);
    }
  }, [locationPath]);

  useEffect(() => {
    loadSessions(projectUUID);
  }, []);

  useEffect(() => {
    if (_.isEmpty(selectedSession) && !_.isEmpty(sessions)) {
      handleSelectSession(sessions[0]?.uuid);
    }
  }, [sessions]);

  return (
    <Box>
      <Switch>
        <Route path={ROUTES.MAIN.DATA_MANAGER.child.CAPTURES_SCREEN.path}>
          <DataManagerContext.Provider
            value={{ onOpenSelectSessionDialog: handleOpenSelectSessionDialog }}
          >
            <TheCapturesScreen
              onShowInformation={() => showInformationWindow("Data Manager", screenInfoMd)}
              selectedSession={selectedSession}
            />
          </DataManagerContext.Provider>
        </Route>
        <Route path={ROUTES.MAIN.DATA_MANAGER.child.CAPTURE_DETAILS_SCREEN.path}>
          <DataManagerContext.Provider
            value={{ onOpenSelectSessionDialog: handleOpenSelectSessionDialog }}
          >
            <Suspense fallback={AppLoader}>
              <TheCaptureDetailsScreen
                onShowInformation={() => showInformationWindow("Data Manager", screenInfoMd)}
                selectedSession={selectedSession}
                isDisabledByAutoSession={isDisabledByAutoSession}
                isReadOnlyMode={isReadOnlyMode}
              />
            </Suspense>
          </DataManagerContext.Provider>
        </Route>
        <Route>
          <Redirect
            from={ROUTES.MAIN.DATA_MANAGER.path}
            to={{
              pathname: generatePath(ROUTES.MAIN.DATA_MANAGER.child.CAPTURES_SCREEN.path, {
                projectUUID,
              }),
            }}
          />
        </Route>
      </Switch>
      <DialogTableSelect
        title={t("dialog-session-select.title")}
        isOpen={isOpenSelectSessionDialog}
        data={sessionsToSelect}
        columns={[
          { title: "Name", field: "name" },
          { title: "Type", field: "type" },
          { title: "Algorithm", field: "algorithm" },
        ]}
        onClose={handleCloseSelectSessionDialog}
        onSelect={(row) => handleSelectSession(row.uuid)}
      />
    </Box>
  );
};

export default TheDataManager;
