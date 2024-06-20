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

import React, { Fragment, useState, useEffect, useMemo } from "react";
import _ from "lodash";
import HelpIcon from "components/HelpIcon";
import { FormControl, Grid, InputLabel, MenuItem, Select, TextField } from "@mui/material";
import { useTranslation } from "react-i18next";
import useStyles from "../DownloadModelStyles";

const boolOptions = [
  { name: "False", value: false },
  { name: "True", value: true },
];
const levelOptions = [1, 2, 3];

const defaultAdvSettings = {
  test_data: null, // test_data
  debug: false, // debug
  debug_level: 1, // debug_level
  profile: false, // profile
  profile_iterations: 0, // profile_iterations
  extra_build_flags: "",
};

const AdvanceSettings = ({ captures, advSettings, setAdvSettings }) => {
  const { t } = useTranslation("models");
  const classes = useStyles();
  const [captureFileList, setCaptureFileList] = useState(captures);
  const [settings, setSettings] = useState(advSettings);

  const helpContent = {
    test_data: t("adv-settings.helper-test-data"),
    debug: t("adv-settings.helper-debug"),
    debugLevel: t("adv-settings.helper-debug-level"),
    profile: t("adv-settings.helper-profile"),
    profileIterations: t("adv-settings.helper-profile-iteration"),
  };

  useEffect(() => {
    if (!_.isEmpty(advSettings)) {
      setSettings({ ...advSettings });
    } else {
      setSettings({ ...defaultAdvSettings });
    }
  }, []);

  useEffect(() => {
    setCaptureFileList(captures);
  }, [captures]);

  useMemo(() => {
    setAdvSettings({ ...settings });
  }, [settings]);

  const handleDirectChange = (e) => {
    const { value, name } = e.target;
    setSettings((prevObj) => ({ ...prevObj, [name]: value }));
  };

  return (
    <Grid container className={classes.grid}>
      {!_.isUndefined(settings.test_data) ? (
        <FormControl fullWidth={true} className={classes.formControl}>
          <InputLabel htmlFor="test_data">Test Data</InputLabel>
          <Select
            label={t("adv-settings.label-test-data")}
            name="test_data"
            value={settings.test_data}
            onChange={handleDirectChange}
          >
            <MenuItem key="" value={null}>
              None
            </MenuItem>
            {captureFileList &&
              captureFileList.map((captureFile) => {
                return (
                  <MenuItem key={captureFile.name} value={captureFile.name}>
                    {captureFile.name}
                  </MenuItem>
                );
              })}
          </Select>
          <HelpIcon className={classes.helpIcon} toolTip={helpContent.test_data} />
        </FormControl>
      ) : null}
      {!_.isUndefined(settings.debug) ? (
        <FormControl fullWidth={true} className={classes.formControl}>
          <InputLabel htmlFor="debug">Debug</InputLabel>
          <Select
            label={t("adv-settings.label-debug")}
            name="debug"
            value={settings.debug}
            onChange={handleDirectChange}
          >
            <MenuItem key="" value="" disabled />
            {boolOptions.map((boolOption) => {
              return (
                <MenuItem key={boolOption.value} value={boolOption.value}>
                  {boolOption.name}
                </MenuItem>
              );
            })}
          </Select>
          <HelpIcon className={classes.helpIcon} toolTip={helpContent.debug} />
        </FormControl>
      ) : null}
      {settings.debug ? (
        <>
          {settings.debug_level ? (
            <FormControl fullWidth={true} className={classes.formControl}>
              <InputLabel htmlFor="debug_level">Debug Level</InputLabel>
              <Select
                label={t("adv-settings.label-debug-level")}
                name="debug_level"
                value={settings.debug_level}
                onChange={handleDirectChange}
              >
                <MenuItem key="" value="" disabled />
                {levelOptions.map((levelOption) => {
                  return (
                    <MenuItem key={levelOption} value={levelOption}>
                      {levelOption}
                    </MenuItem>
                  );
                })}
              </Select>
              {helpContent.debugLevel ? (
                <HelpIcon className={classes.helpIcon} toolTip={helpContent.debugLevel} />
              ) : null}
            </FormControl>
          ) : (
            <></>
          )}
          <FormControl fullWidth={true} className={classes.formControl}>
            <InputLabel htmlFor="profile">Profile</InputLabel>
            <Select
              label={t("adv-settings.label-profile")}
              name="profile"
              value={settings.profile}
              onChange={handleDirectChange}
            >
              <MenuItem key="" value="" disabled />
              {boolOptions.map((boolOption) => {
                return (
                  <MenuItem key={boolOption.value} value={boolOption.value}>
                    {boolOption.name}
                  </MenuItem>
                );
              })}
            </Select>
            {helpContent.profile ? (
              <HelpIcon className={classes.helpIcon} toolTip={helpContent.profile} />
            ) : null}
          </FormControl>
          <FormControl fullWidth={true} className={classes.formControl}>
            <TextField
              name="profile_iterations"
              label={t("adv-settings.label-profile-iteration")}
              type="number"
              value={settings.profile_iterations}
              onChange={handleDirectChange}
            />
            <HelpIcon className={classes.helpIcon} toolTip={helpContent.profileIterations} />
          </FormControl>
        </>
      ) : null}
      <FormControl fullWidth={true} className={classes.formControl}>
        <TextField
          name="extra_build_flags"
          label={t("adv-settings.label-extra-build-flags")}
          value={settings.extra_build_flags}
          onChange={handleDirectChange}
        />
        {helpContent.profile_iterations ? (
          <HelpIcon className={classes.helpIcon} toolTip={helpContent.profile_iterations} />
        ) : null}
      </FormControl>
    </Grid>
  );
};

export default AdvanceSettings;
