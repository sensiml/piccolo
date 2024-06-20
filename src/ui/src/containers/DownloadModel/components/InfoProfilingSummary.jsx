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

/* eslint-disable prefer-template */
/* eslint-disable camelcase */
import _ from "lodash";
import React, { useMemo } from "react";
import { useTranslation } from "react-i18next";
import { Box, List, ListItem, Grid, Card, Typography, CardContent } from "@mui/material";
import HelpIcon from "components/HelpIcon";

const DeviceProfile = ({ deviceProfile, classes }) => {
  const { t } = useTranslation("models");

  const totalTime = useMemo(() => {
    if (_.isUndefined(deviceProfile)) {
      return "";
    }
    if (isNaN(deviceProfile?.classifier_time_ms)) {
      return deviceProfile?.feature_time_ms;
    }
    return Number(deviceProfile?.classifier_time_ms + deviceProfile?.feature_time_ms).toFixed(3);
  }, [deviceProfile]);

  const totalCycles = useMemo(() => {
    if (_.isUndefined(deviceProfile)) {
      return "";
    }
    if (isNaN(deviceProfile?.classifier_cycle_count)) {
      return deviceProfile?.feature_cycle_count;
    }
    return deviceProfile?.classifier_cycle_count + deviceProfile?.feature_cycle_count;
  }, [deviceProfile]);

  return (
    <Box>
      <Grid container justifyContent={"space-around"} grid>
        <Grid item xs={12}>
          <Card elevation={0}>
            <CardContent>
              <Typography class={classes.formSubTitle} component="div">
                {t("info.profile-device-mem")}
              </Typography>
              <List dense className={classes.infoList}>
                <ListItem>
                  {deviceProfile?.sram ? (
                    <Grid container justifyContent={"space-around"}>
                      <Grid item xs={4}>
                        <b className={classes.prefix}>{t("info.profile-sram")}</b>
                      </Grid>
                      <Grid item xs={5}>
                        {`${deviceProfile?.sram} Bytes`}
                      </Grid>
                      <Grid item xs={3}>
                        <HelpIcon
                          className={classes.profileHelpIcon}
                          toolTip={t("help-texts.sram-size")}
                        />
                      </Grid>
                    </Grid>
                  ) : (
                    ""
                  )}
                </ListItem>
                <ListItem>
                  {deviceProfile?.stack ? (
                    <Grid container justifyContent={"space-around"} grid>
                      <Grid item xs={4}>
                        <b className={classes.prefix}>{t("info.profile-stack")}</b>
                      </Grid>
                      <Grid item xs={5}>
                        {` ${deviceProfile?.stack} Bytes`}
                      </Grid>
                      <Grid item xs={3}>
                        <HelpIcon
                          className={classes.profileHelpIcon}
                          toolTip={t("help-texts.stack-size")}
                        />
                      </Grid>
                    </Grid>
                  ) : (
                    ""
                  )}
                </ListItem>
                <ListItem>
                  {deviceProfile?.flash ? (
                    <Grid container justifyContent={"space-around"} grid>
                      <Grid item xs={4}>
                        <b className={classes.prefix}>{t("info.profile-flash")}</b>
                      </Grid>
                      <Grid item xs={5}>
                        {` ${deviceProfile?.flash} Bytes`}
                      </Grid>
                      <Grid item xs={3}>
                        <HelpIcon
                          className={classes.profileHelpIcon}
                          toolTip={t("help-texts.flash-size")}
                        />
                      </Grid>
                    </Grid>
                  ) : (
                    ""
                  )}
                </ListItem>
              </List>
            </CardContent>
          </Card>
          <Card elevation={0}>
            <CardContent>
              <Typography class={classes.formSubTitle} component="div">
                {t("info.profile-latency-title")}
              </Typography>
              <List dense className={classes.infoList}>
                <ListItem>
                  {deviceProfile?.feature_time_ms ? (
                    <Grid container justifyContent={"space-around"} grid>
                      <Grid item xs={4}>
                        <b className={classes.prefix}>{t("info.profile-cycle-count-features")}</b>
                      </Grid>
                      <Grid item xs={5}>
                        {`${Number(deviceProfile?.feature_time_ms).toFixed(3)} ms` +
                          ` (${deviceProfile?.feature_cycle_count})`}
                      </Grid>
                      <Grid item xs={3}>
                        <HelpIcon
                          className={classes.profileHelpIcon}
                          toolTip={
                            t("help-texts.est-cycle-time-features") +
                            "\n\n" +
                            t("help-texts.cpu-freq-used-p1") +
                            deviceProfile?.clock_speed_mhz +
                            t("help-texts.cpu-freq-used-p2")
                          }
                        />
                      </Grid>
                    </Grid>
                  ) : (
                    ""
                  )}
                </ListItem>
                {deviceProfile?.classifier_cycle_count ? (
                  <ListItem>
                    <Grid container justifyContent={"space-around"} grid>
                      <Grid item xs={4}>
                        <b className={classes.prefix}>{t("info.profile-cycle-count-classifier")}</b>
                      </Grid>
                      <Grid item xs={5}>
                        {`${Number(deviceProfile?.classifier_time_ms).toFixed(3)} ms ` +
                          ` (${deviceProfile?.classifier_cycle_count})`}
                      </Grid>
                      <Grid item xs={3}>
                        <HelpIcon
                          className={classes.profileHelpIcon}
                          toolTip={
                            t("help-texts.est-cycle-time-classifier") +
                            "\n\n" +
                            t("help-texts.cpu-freq-used-p1") +
                            deviceProfile?.clock_speed_mhz +
                            t("help-texts.cpu-freq-used-p2")
                          }
                        />
                      </Grid>
                    </Grid>
                  </ListItem>
                ) : null}
                <ListItem>
                  {deviceProfile?.feature_time_ms ? (
                    <Grid container justifyContent={"space-around"} grid>
                      <Grid item xs={4}>
                        <b className={classes.prefix}>{t("info.profile-total-latency")}</b>
                      </Grid>
                      <Grid item xs={5}>
                        {` ${totalTime} ms (${totalCycles})`}
                      </Grid>
                      <Grid item xs={3}>
                        <HelpIcon
                          className={classes.profileHelpIcon}
                          toolTip={
                            t("help-texts.est-cycle-time-total") +
                            "\n\n" +
                            t("help-texts.cpu-freq-used-p1") +
                            deviceProfile?.clock_speed_mhz +
                            t("help-texts.cpu-freq-used-p2")
                          }
                        />
                      </Grid>
                    </Grid>
                  ) : (
                    ""
                  )}
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DeviceProfile;
