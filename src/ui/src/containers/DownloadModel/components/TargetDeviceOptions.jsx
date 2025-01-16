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
/* eslint-disable indent */
import React, { useState, useMemo, useEffect, forwardRef, useImperativeHandle } from "react";
import _ from "lodash";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import CloudDownloadIcon from "@mui/icons-material/CloudDownload";
import {
  Box,
  Button,
  FormControl,
  InputLabel,
  IconButton,
  MenuItem,
  Select,
  Collapse,
  Typography,
  Tooltip,
} from "@mui/material";
import { useTranslation } from "react-i18next";
import TextField from "@mui/material/TextField";
import Autocomplete from "@mui/material/Autocomplete";
import FormCurtain from "components/UIFormCurtain";
import CheckBoxSelectCard from "components/FormElements/CheckBoxSelectCard";

import {
  PLATROFM_TYPES,
  STEP_SELECT_PLATFORM,
  STEP_SUBMIT_DOWNLOAD,
  STEP_SELECTED_PLATFORM,
  ARMGCC_UUID,
  FORMATS,
  DRIVERS_DEFAULT_KEY,
  SOURCE_DEFAULT_LIST,
} from "containers/DownloadModel/const";

import useStyles from "../DownloadModelStyles";
import AdvanceSettings from "./AdvanceSettings";
import defaultSelectedPlatform from "./defaultSelectedPlatform";

/*
const defaultEmpty = {
  target_platform: "",
  target_processor: "",
  target_compiler: "",
  selected_platform_version: "",
  format: "",
  float_options: " ",
  sample_rate: "",
  application: "",
}
*/

const TargetDeviceOptions = forwardRef(
  (
    {
      platformList,
      captureConfigurations,
      updateOptions,
      defaultTargetOptions,
      defaultDownloadFormat,
      defaultDataSource,
      defaultAdvSettings,
      captures,
      handleDownloadRequest,
      platformLogos,
      setIsFirstLoading,
    },
    ref,
  ) => {
    const { t } = useTranslation("models");
    const classes = useStyles();
    const [step, setStep] = useState(STEP_SELECT_PLATFORM);
    const [targetDeviceOptions, setTargetDeviceOptions] = useState({});
    const [targetAdvSettings, setTargetAdvSettings] = useState({});
    const [downloadFormat, setDownloadFormat] = useState("");
    const [dataSourceList, setDataSourceList] = useState([]);
    const [dataSource, setDataSource] = useState(null);
    const [showAdvSettings, setShowAdvSettings] = useState(true);

    const [selectedPlatform, setSelectedPlatform] = useState({});

    const floatOptions = useMemo(() => {
      // get for render FloatOptions from selected selectedProcessor
      const selectedProc = selectedPlatform?.processors?.find(
        (el) => el.uuid === targetDeviceOptions.target_processor.uuid,
      );
      return selectedProc?.float_options;
    }, [selectedPlatform, targetDeviceOptions]);

    const getFormat = (canBuildLibrary) => {
      return canBuildLibrary ? FORMATS : FORMATS.filter((el) => el.isBinary === false);
    };

    const sampleRates = useMemo(() => {
      if (selectedPlatform?.supported_source_drivers && dataSource) {
        return selectedPlatform.supported_source_drivers[dataSource];
      }
      return [];
    }, [selectedPlatform, dataSource]);

    const applicationList = useMemo(() => {
      if (!selectedPlatform?.applications || !Object.keys(selectedPlatform?.applications)) {
        return [];
      }
      const list = Object.entries(selectedPlatform?.applications).map(([key, obj]) => {
        return { name: key, ...obj };
      });
      return list;
    }, [selectedPlatform]);

    const getSelectedAppicationObj = () => {
      // eslint-disable-next-line no-unused-vars
      const selectedApp = applicationList.find((el) => el.name === targetDeviceOptions.application);
      return selectedApp || {};
    };

    const getOutputs = () => {
      return getSelectedAppicationObj()?.supported_outputs || [];
    };

    const setDefaultSourceList = (platform) => {
      let sourceList = captureConfigurations.map((capture) => ({
        name: capture.name,
        value: capture.uuid,
      }));
      // for downloadFormat bin only delices from capture allowed for select
      if (platform?.supported_source_drivers) {
        Object.keys(platform.supported_source_drivers).forEach((key) => {
          if (key !== DRIVERS_DEFAULT_KEY) {
            sourceList.push({ name: key, value: key });
          }
        });
      }
      if (downloadFormat !== "bin") {
        sourceList = sourceList.concat([...SOURCE_DEFAULT_LIST]);
      }
      sourceList.sort();
      setDataSourceList([...sourceList]);
      setDataSource((value) => {
        if (sourceList?.length && !sourceList.find((el) => el?.value === value)) {
          // if default/selected value not in updated list, change to first
          return sourceList[0]?.value;
        }
        return value;
      });
    };

    const setDefaultFromSelectedPlatform = (platform) => {
      // updates defaults TargetDeviceOptions each time when selectedPlatform is changing
      const defaultData = {
        target_platform: platform.uuid,
        target_processor: platform?.processors?.find(
          (el) => el?.uuid === platform?.default_selections?.processor,
        ),
        target_compiler: platform?.default_selections?.compiler || "",
      };
      // set platform_versions
      if (platform.platform_versions && platform.platform_versions?.length) {
        defaultData.selected_platform_version = platform.platform_versions[0] || "";
      }
      // set float_options
      if (defaultData.target_compiler && defaultData.target_processor) {
        const selectedProcessor = platform?.processors?.find(
          (el) => el?.uuid === defaultData.target_processor?.uuid,
        );
        defaultData.float_options =
          selectedProcessor?.float_options[platform?.default_selections?.float] || "";
      }
      // set platform_versions

      if (
        platform.hardware_accelerators &&
        Object.keys(platform.hardware_accelerators).length !== 0
      ) {
        defaultData.hardware_accelerator = platform.default_selections.hardware_accelerator || "";
      }
      setDataSource(null);
      // set source data
      if (platform.supported_source_drivers) {
        if (platform.supported_source_drivers[DRIVERS_DEFAULT_KEY]?.length) {
          const [defaultDataSourceToSet, defaultSampleRate] =
            platform.supported_source_drivers?.Default;
          defaultData.sample_rate = defaultSampleRate;
          setDataSource(defaultDataSourceToSet);
        }
      }
      // set application
      if (platform.applications && Object.values(platform.applications)?.length) {
        const [defaultAppName, defaulAppObj] = Object.entries(platform.applications)[0] || {};
        defaultData.application = defaultAppName;
        defaultData.output_options = defaulAppObj?.supported_outputs[0] || {};
      } else {
        defaultData.application = "";
      }
      setTargetDeviceOptions({ ...defaultData });
      setDownloadFormat(getFormat(platform.can_build_binary)[0]?.value);
      setDefaultSourceList(platform);
    };

    const handleSubmitPlatformSelect = () => {
      setStep(STEP_SUBMIT_DOWNLOAD);
      setTargetDeviceOptions((currentValues) => ({
        ...currentValues,
        step: STEP_SELECTED_PLATFORM,
      }));
      window.scrollTo(0, 0);
    };

    const handleSelectPlatform = (platform, isSelect) => {
      if (isSelect) {
        setSelectedPlatform({ ...platform });
        setDefaultFromSelectedPlatform({ ...platform });
      }
    };

    const handleDeleteSelectedPlatform = () => {
      setStep(STEP_SELECT_PLATFORM);
      setSelectedPlatform(null);
      setSelectedPlatform(defaultSelectedPlatform);
      setDefaultFromSelectedPlatform(defaultSelectedPlatform);
      setTargetAdvSettings({});
    };

    const handleSelectFormat = (e) => {
      setDownloadFormat(e.target.value);
    };

    const handleSelectDataSource = (e) => {
      setDataSource(e.target.value);
    };

    useImperativeHandle(ref, () => ({
      handleDeleteSelectedPlatform: () => handleDeleteSelectedPlatform(),
      isSelectPlatform: () => step !== STEP_SELECT_PLATFORM && !_.isEmpty(selectedPlatform),
    }));

    useEffect(() => {
      // waiting for load data to selectedPlatform && defaultTargetOptions
      if (defaultTargetOptions?.target_platform) {
        // if not isLoadedDefault and default has value set this value first
        if (defaultTargetOptions?.step === STEP_SELECTED_PLATFORM) {
          setStep(STEP_SUBMIT_DOWNLOAD);
        }
        const targetPlatform = platformList.find(
          (platform) => platform.uuid === defaultTargetOptions.target_platform,
        );
        setTargetDeviceOptions({ ...defaultTargetOptions });
        setDownloadFormat(defaultDownloadFormat);
        setDataSource(defaultDataSource);
        setSelectedPlatform(targetPlatform);
        if (!_.isEmpty(defaultAdvSettings)) {
          setTargetAdvSettings(defaultAdvSettings);
          setShowAdvSettings(true);
        }
      } else {
        setSelectedPlatform(null);
        setSelectedPlatform(defaultSelectedPlatform);
        setDefaultFromSelectedPlatform(defaultSelectedPlatform);
        setShowAdvSettings(true);
      }
    }, []);

    useEffect(() => {
      // updates defaults float_options each time when targetDeviceOptions.processor is changing
      if (
        targetDeviceOptions.target_processor?.uuid !==
        selectedPlatform?.default_selections?.processor.uuid
      ) {
        const selectedProc = selectedPlatform?.processors?.find(
          (el) => el.uuid === targetDeviceOptions.target_processor?.uuid,
        );

        setTargetDeviceOptions((currentValues) => ({
          ...currentValues,
          float_options:
            selectedProc?.float_options &&
            Object.hasOwn(selectedProc?.float_options, selectedPlatform?.default_selections?.float)
              ? selectedProc?.float_options[selectedPlatform?.default_selections?.float]
              : "",
        }));
      }
    }, [targetDeviceOptions.target_processor]);

    useEffect(() => {
      // handle updates downloadFormat of options and updateback to the parent component
      setDefaultSourceList(selectedPlatform);
    }, [downloadFormat]);

    useEffect(() => {
      // updates targetDeviceOptions.sample_rate float_options each time when dataSource is changing
      if (dataSource) {
        if (selectedPlatform?.supported_source_drivers && dataSource) {
          const samplesArr = selectedPlatform.supported_source_drivers[dataSource];
          if (samplesArr?.length) {
            setTargetDeviceOptions((currentValues) => ({
              ...currentValues,
              sample_rate: samplesArr[0] || 0,
            }));
          }
        }
      }
    }, [dataSource]);

    useEffect(() => {
      // updates supported_outputs float_options each time when application is changing
      if (selectedPlatform?.applications && targetDeviceOptions.application) {
        // eslint-disable-next-line no-unused-vars
        const selectedApp = getSelectedAppicationObj();
        if (selectedApp?.supported_outputs?.length) {
          if (targetDeviceOptions.output_options !== selectedApp?.supported_outputs[0]) {
            setTargetDeviceOptions((currentValues) => ({
              ...currentValues,
              output_options: selectedApp?.supported_outputs[0],
            }));
          }
        }
      }
    }, [targetDeviceOptions.application]);

    useEffect(() => {
      // handle updates any of options and updateback to the parent component
      let platformInformation;

      if (!_.isEmpty(selectedPlatform)) {
        platformInformation = {
          name: selectedPlatform.name,
          platform_type: selectedPlatform.platform_type,
          description: selectedPlatform.description,
          documentation: selectedPlatform.documentation,
          manufacturer: selectedPlatform.manufacturer,
        };
      }
      if (targetDeviceOptions?.target_platform) {
        updateOptions(
          targetDeviceOptions,
          downloadFormat,
          dataSource,
          targetAdvSettings,
          platformInformation,
        );
        setIsFirstLoading(false);
      }
    }, [targetDeviceOptions, downloadFormat, dataSource, targetAdvSettings]);

    const handleDeviceOptionsDirectChanges = (e) => {
      /* handleDeviceOptionsDirectChanges
      set direct value to targetDeviceOptions, with name is key of config
    */
      const { name, value } = e.target;
      setTargetDeviceOptions({ ...targetDeviceOptions, [name]: value });
    };

    const handleDeviceProcessorOptionsChanges = (e, newValue) => {
      /* handleDeviceOptionsDirectChanges
      set direct value to targetDeviceOptions, with name is key of config
    */
      if (newValue == null) {
        return;
      }
      setTargetDeviceOptions({ ...targetDeviceOptions, target_processor: newValue });
    };

    return (
      <>
        {step === STEP_SUBMIT_DOWNLOAD && !_.isEmpty(selectedPlatform) ? (
          // waiting for loading default platform
          <Box>
            <Typography variant="h2" className={classes.header}>
              {t("target-device-options.download-header")}
            </Typography>
            <FormControl fullWidth className={classes.formControlPlatform}>
              <Box className={classes.selectedPlatformLabel}>
                <Typography variant="subtitle1" className={classes.selectedPlatformTitle}>
                  Platform - {selectedPlatform.name}
                </Typography>

                <IconButton
                  color="primary"
                  size="small"
                  className={classes.selectedPlatformLabelBtn}
                  onClick={handleDeleteSelectedPlatform}
                >
                  <ArrowBackIcon />
                </IconButton>

                {/* <Button variant="outlined" onClick={handleDeleteSelectedPlatform}>
                <CloseOutlinedIcon />
              </Button> */}
              </Box>
            </FormControl>
            {getFormat(selectedPlatform.can_build_binary) && downloadFormat ? (
              <FormControl fullWidth className={classes.formControl}>
                <InputLabel id="format_label">{t("target-device-options.label-format")}</InputLabel>
                <Select
                  id="format_select"
                  labelId="format_label"
                  label={t("target-device-options.label-format")}
                  name={"format"}
                  onChange={handleSelectFormat}
                  value={downloadFormat}
                >
                  {getFormat(selectedPlatform.can_build_binary).map((el, ind) => (
                    <MenuItem value={el.value} key={`format_sl_${ind}`}>
                      {el.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            ) : (
              ""
            )}
            {selectedPlatform.platform_versions?.length &&
            targetDeviceOptions.selected_platform_version ? (
              // show only platform_versions has data
              <FormControl fullWidth={true} className={classes.formControl}>
                <InputLabel id="platform_version_label" htmlFor="selected_platform_version">
                  {t("target-device-options.label-platform-version")}
                </InputLabel>
                <Select
                  id="platform_version"
                  labelId="platform_version_label"
                  label={t("target-device-options.label-platform-version")}
                  name={"selected_platform_version"}
                  onChange={handleDeviceOptionsDirectChanges}
                  value={targetDeviceOptions.selected_platform_version}
                >
                  {selectedPlatform.platform_versions.map((value, ind) => (
                    <MenuItem value={value} key={`vers_sl_${ind}`}>
                      {value}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            ) : (
              <></>
            )}
            {selectedPlatform.processors?.length && targetDeviceOptions.target_processor ? (
              <FormControl fullWidth={true} className={classes.formControl}>
                <Autocomplete
                  id="target_processor_auto"
                  labelId="target_processor_label"
                  label={t("target-device-options.label-processor")}
                  name={"target_processor"}
                  onChange={handleDeviceProcessorOptionsChanges}
                  getOptionLabel={(option) => option?.display_name}
                  // renderOption={(props, option) => option.display_name}
                  value={targetDeviceOptions.target_processor}
                  options={selectedPlatform.processors.map((el, ind) => ({
                    manufacturer: el.manufacturer,
                    uuid: el.uuid,
                    display_name: el.display_name,
                  }))}
                  renderInput={(params) => <TextField {...params} label="Processor" />}
                />
              </FormControl>
            ) : (
              ""
            )}
            {floatOptions && targetDeviceOptions.float_options ? (
              <FormControl fullWidth={true} className={classes.formControl}>
                <InputLabel id="float_options_label" htmlFor="float_options">
                  {t("target-device-options.label-float-option")}
                </InputLabel>
                <Select
                  id="float_options"
                  labelId="float_options_label"
                  label={t("target-device-options.label-float-option")}
                  name={"float_options"}
                  onChange={handleDeviceOptionsDirectChanges}
                  value={targetDeviceOptions.float_options}
                >
                  {Object.entries(floatOptions).map(([key, val], ind) => (
                    <MenuItem value={val} key={`fl_opt_sl_${ind}`}>
                      {key}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            ) : (
              ""
            )}
            {selectedPlatform.supported_compilers?.length && targetDeviceOptions.target_compiler ? (
              <FormControl fullWidth={true} className={classes.formControl}>
                <InputLabel id="target_compiler_label" htmlFor="target_compiler">
                  {t("target-device-options.label-compiler")}
                </InputLabel>
                <Select
                  id="target_compiler"
                  labelId="target_compiler_label"
                  label={t("target-device-options.label-compiler")}
                  name={"target_compiler"}
                  onChange={handleDeviceOptionsDirectChanges}
                  value={targetDeviceOptions.target_compiler}
                >
                  {selectedPlatform.supported_compilers.map((el, ind) => (
                    <MenuItem value={el.uuid} key={`comp_sl_${ind}`}>
                      {`${el.name} ${el.compiler_version}`}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            ) : (
              ""
            )}

            {Object.keys(selectedPlatform.hardware_accelerators)?.length &&
            targetDeviceOptions.hardware_accelerator ? (
              <FormControl fullWidth={true} className={classes.formControl}>
                <InputLabel id="hardware_accelerator_label" htmlFor="hardware-accelerator">
                  {t("target-device-options.hardware-accelerator")}
                </InputLabel>
                <Select
                  id="hardware_accelerator"
                  labelId="hardware_accelerator_label"
                  label={t("target-device-options.hardware-accelerator")}
                  name={"hardware_accelerator"}
                  onChange={handleDeviceOptionsDirectChanges}
                  value={targetDeviceOptions.hardware_accelerator}
                >
                  {Object.keys(selectedPlatform.hardware_accelerators).map((key, index) => (
                    <MenuItem value={key} key={`hw_sl_${index}`}>
                      {selectedPlatform.hardware_accelerators[key].display_name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            ) : (
              ""
            )}

            {dataSourceList?.length && dataSource ? (
              <FormControl fullWidth={true} className={classes.formControl}>
                <InputLabel id="format_label" htmlFor="format">
                  {t("target-device-options.label-data-source")}
                </InputLabel>
                <Select
                  id="format"
                  labelId="format_label"
                  label={t("target-device-options.label-data-source")}
                  name={"format"}
                  onChange={handleSelectDataSource}
                  value={dataSource}
                >
                  {dataSourceList.map((el, ind) => (
                    <MenuItem value={el.value} key={`source_sl_${ind}`}>
                      {el.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            ) : (
              ""
            )}
            {dataSourceList?.length && dataSource && sampleRates ? (
              <FormControl fullWidth={true} className={classes.formControl}>
                <InputLabel id="sample_rate_label" htmlFor="sample_rate">
                  {t("target-device-options.label-sample-rate")}
                </InputLabel>
                <Select
                  id="sample_rate"
                  labelId="sample_rate_label"
                  label={t("target-device-options.label-sample-rate")}
                  name={"sample_rate"}
                  onChange={handleDeviceOptionsDirectChanges}
                  value={targetDeviceOptions.sample_rate}
                >
                  {sampleRates.map((value, ind) => (
                    <MenuItem value={value} key={`rates_sl_${ind}`}>
                      {value}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            ) : (
              ""
            )}
            {!_.isEmpty(applicationList) && targetDeviceOptions.application ? (
              <FormControl fullWidth className={classes.formControl}>
                <InputLabel id="application_label" htmlFor="application">
                  {t("target-device-options.label-application")}
                </InputLabel>
                <Select
                  id="application"
                  labelId="application_label"
                  label={t("target-device-options.label-application")}
                  name={"application"}
                  onChange={handleDeviceOptionsDirectChanges}
                  value={targetDeviceOptions.application}
                >
                  {applicationList.map((app, ind) => (
                    <MenuItem value={app.name} key={`app_sl_${ind}`}>
                      {app.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            ) : (
              ""
            )}
            {targetDeviceOptions.application && getOutputs()?.length ? (
              <FormControl fullWidth={true} className={classes.formControl}>
                <InputLabel id="output_options_label" htmlFor="output_options">
                  {t("target-device-options.label-output")}
                </InputLabel>
                <Select
                  id="output_options"
                  labelId="output_options_label"
                  label={t("target-device-options.label-output")}
                  name={"output_options"}
                  onChange={handleDeviceOptionsDirectChanges}
                  value={targetDeviceOptions.output_options}
                >
                  {getOutputs().map((value, ind) => (
                    <MenuItem value={value} key={`app_out_sl_${ind}`}>
                      {value.join(", ")}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            ) : (
              ""
            )}
            <Box className={classes.curtainWrapper}>
              <FormCurtain
                text={t("Debug/Profiling Settings")}
                isOpen={showAdvSettings}
                onClickHandler={(isOpen) => setShowAdvSettings(isOpen)}
              />
            </Box>
            <Collapse in={showAdvSettings}>
              <Typography variant="subtitle1" className={classes.formTitle}>
                {t("Debug/Profiling Settings")}:
              </Typography>
              <AdvanceSettings
                captures={captures}
                advSettings={targetAdvSettings}
                setAdvSettings={setTargetAdvSettings}
              />
            </Collapse>

            <Tooltip title={t("Download Knowledge Pack")}>
              <Button
                className={classes.actionButton}
                variant="contained"
                size="large"
                color="primary"
                id="downloadButton"
                startIcon={<CloudDownloadIcon />}
                onClick={handleDownloadRequest}
              >
                {t("download.btn-download")}
              </Button>
            </Tooltip>
          </Box>
        ) : platformList && platformList.length ? (
          <>
            <Typography variant="h2" className={classes.header}>
              {t("target-device-options.select-platform-header")}
            </Typography>
            {PLATROFM_TYPES.map((platformType) => (
              <Box key={platformType} fullWidth={true} className={classes.formControl}>
                <Typography variant="subtitle2" className={classes.formTitle}>
                  {platformType === "devkit"
                    ? "Development Platforms"
                    : `${_.capitalize(platformType)}s`}
                </Typography>
                <Box className={classes.cardBoardWrapper}>
                  {platformList
                    .filter((platform) => platform.platform_type === platformType)
                    .map((platform, index) => {
                      return (
                        <CheckBoxSelectCard
                          key={`pipeline_checkbox_${index}`}
                          image={
                            _.has(platformLogos, platform.manufacturer)
                              ? platformLogos[platform.manufacturer]
                              : null
                          }
                          width={"100%"}
                          name={platform.name}
                          label={<b>{platform.name}</b>}
                          btnText={"Select"}
                          header={platform.name}
                          value={
                            _.isEmpty(selectedPlatform)
                              ? false
                              : platform.uuid === selectedPlatform?.uuid
                          }
                          defaultValue={
                            _.isEmpty(selectedPlatform)
                              ? false
                              : platform.uuid === selectedPlatform?.uuid
                          }
                          onChange={(_name, value) => handleSelectPlatform(platform, value)}
                          onClickButton={handleSubmitPlatformSelect}
                        />
                      );
                    })}
                </Box>
              </Box>
            ))}
          </>
        ) : (
          <></>
        )}
      </>
    );
  },
);

export default TargetDeviceOptions;
