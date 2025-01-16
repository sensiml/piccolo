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
import { useTranslation } from "react-i18next";
import { Box, List, ListItem } from "@mui/material";
import useStyles from "../DownloadModelStyles";

const CaptureConfiguration = ({ captureConfigurations, dataSource }) => {
  const { t } = useTranslation("models");
  const classes = useStyles();

  const renderSensors = (source) => {
    // render sensors types separated by ,
    if (!source.sensors) {
      return [];
    }
    return source.sensors.map(
      (sensor, ind) => ` ${ind > 0 && ind < source.sensors.length - 1 ? "," : ""}${sensor.type}`,
    );
  };

  return (
    <Box>
      {captureConfigurations
        .filter((el) => el.uuid === dataSource)
        .map((el, ind) => (
          <Box key={`capture_${ind}`}>
            <List dense key={`capture_L${ind}`} className={classes.infoList}>
              <ListItem>
                <b className={classes.prefix}>{t("info.prefix-capture-name")}</b>
                {el.name}
              </ListItem>
              <ListItem>
                <b className={classes.prefix}>{t("info.prefix-capture-device")}</b>
                {` ${el?.configuration.name}`}
              </ListItem>
              <ListItem className={classes.infoListItem}>
                <b className={classes.prefix}>{t("info.capture-sources")}</b>
                {el.configuration?.capture_sources?.length &&
                  // eslint-disable-next-line no-shadow
                  el.configuration.capture_sources.map((source, ind) => (
                    <List key={`sub_${ind}`} className={classes.captureSubList}>
                      <ListItem className={classes.captureSubListItem} key={`name_${ind}`}>
                        {t("info.capture-name", { name: source.name })}
                      </ListItem>
                      <ListItem className={classes.captureSubListItem} key={`rate_${ind}`}>
                        {t("info.capture-sample-rata", { sample_rate: source.sample_rate })}
                      </ListItem>
                      <ListItem className={classes.captureSubListItem} key={`sensors_${ind}`}>
                        {t("info.capture-sensors", { sensors: renderSensors(source) })}
                      </ListItem>
                    </List>
                  ))}
              </ListItem>
            </List>
          </Box>
        ))}
    </Box>
  );
};

export default CaptureConfiguration;
