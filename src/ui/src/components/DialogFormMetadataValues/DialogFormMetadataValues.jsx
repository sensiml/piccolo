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

import React, { useState, useEffect, useMemo } from "react";
import _ from "lodash";
import PropTypes from "prop-types";

import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteForeverOutlinedIcon from "@mui/icons-material/DeleteForeverOutlined";

import makeStyles from "@mui/styles/makeStyles";

import { useTheme } from "@mui/material/styles";
import { Alert, Box, Button, Tooltip, IconButton } from "@mui/material";

import { useTranslation } from "react-i18next";
import { ElementLoader } from "components/UILoaders";
import { DialogConfirm } from "components/DialogConfirm";

import TextFieldForm from "components/FormElements/TextFieldForm";
import UIDialogForm from "components/UIDialogFormMedium";

const useStyles = () =>
  makeStyles((theme) => ({
    formWrapper: {
      width: "100%",
      display: "flex",
      flexDirection: "column",
    },
    formWrap: {
      width: "100%",
      display: "flex",
      flexDirection: "column",
      marginBottom: theme.spacing(2),
    },
    deleteBtn: {
      height: theme.spacing(6),
      width: theme.spacing(6),
      justifyContent: "flex-start",
      alignItems: "flex-start",
    },
    dictItemWrapper: {
      width: "100%",
      display: "inline-grid",
      gridTemplateColumns: "auto 2rem",
    },
  }))();

const DialogFormMetadataValues = ({
  isOpen,
  title,
  description,
  defaultValues = [],

  onClose,
  onLoadMetadata,
  onCreate,
  onUpdate,
  onDelete,
}) => {
  const { t } = useTranslation("components");

  const classes = useStyles();
  const theme = useTheme();

  const [errors, setErrors] = useState({});
  const [values, setValues] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isShowAlertUnsaved, setIsShowAlertUnsaved] = useState(false);

  const [valuesToDelete, setValuesToDelete] = useState([]);
  const [createdValues, setCreatedValues] = useState([]);
  const [deletingValueName, setDeletingValueName] = useState("");

  const valuesToShow = useMemo(() => {
    return values.filter((el) => !valuesToDelete.includes(el.name));
  }, [values, valuesToDelete]);

  const isDisabledSubmit = useMemo(() => {
    return !_.isEmpty(errors) || _.isEqual(defaultValues, valuesToShow);
  }, [errors, valuesToShow]);

  const valuesValues = useMemo(() => {
    return valuesToShow.map((el) => el.value);
  }, [valuesToShow]);

  const defaultValuesNames = useMemo(() => {
    return defaultValues.map((el) => el.name);
  }, [defaultValues]);

  const deletingValueValue = useMemo(() => {
    const updatedValue = values.find((el) => el.name === deletingValueName)?.value || "";
    const defaultValue = defaultValues.find((el) => el.name === deletingValueName)?.value || "";
    if (updatedValue !== defaultValue) {
      return `${updatedValue} (${defaultValue})`;
    }
    return updatedValue || "";
  }, [deletingValueName, values, defaultValues]);

  const valuesToUpdate = useMemo(() => {
    return valuesToShow.filter((el) => el.isUpdated && defaultValuesNames.includes(el.name));
  }, [defaultValuesNames, values, valuesToShow]);

  const valuesToCreate = useMemo(() => {
    return valuesToShow.filter((el) => createdValues.includes(el.name)) || [];
  }, [valuesToShow, createdValues]);

  const handleSetError = (name, error) => {
    setErrors({
      ...errors,
      [name]: error,
    });
  };

  const handleResetErrors = () => {
    setErrors({});
  };

  const handleResetValues = () => {
    setIsLoading(false);
    setValues([]);
  };

  const handleValidateValue = (name, value, valueIndex) => {
    if (
      valuesValues.filter(
        (val, index) => _.toLower(_.trim(val)) === _.toLower(_.trim(value)) && index !== valueIndex,
      ).length > 0
    ) {
      handleSetError(name, t("dialog-form-metadata-values.validation-error-duplicate"));
      return false;
    }
    return true;
  };

  const handleValidateValueOnSubmit = (name, value) => {
    if (!value) {
      handleSetError(name, t("dialog-form-metadata-values.validation-error-empty"));
      return false;
    }
    return true;
  };

  const handleConfirmClose = () => {
    handleResetErrors();
    handleResetValues();
    onClose();
  };

  const handleClose = () => {
    if (!_.isEmpty(valuesToCreate) || !_.isEmpty(valuesToDelete) || !_.isEmpty(valuesToUpdate)) {
      setIsShowAlertUnsaved(true);
    } else {
      handleConfirmClose();
    }
  };

  const handleCloseUnsavedAlert = () => {
    setIsShowAlertUnsaved(false);
  };

  const handleCloseWithUpdate = () => {
    handleResetErrors();
    handleResetValues();
    onClose();
  };

  const handleChangeValue = (name, value, valueIndex) => {
    handleResetErrors();

    handleValidateValue(name, value, valueIndex);

    setValues(
      values.map((el) => {
        if (el.name === name) {
          return { ...el, value, isUpdated: true };
        }
        return el;
      }),
    );
  };

  const handleDeleteValue = (name) => {
    handleResetErrors();
    if (defaultValuesNames.includes(name)) {
      // show confirm alert
      setDeletingValueName(name);
    } else {
      setCreatedValues(valuesToCreate.filter((elName) => elName !== name));
      setValuesToDelete([...valuesToDelete, name]);
    }
  };

  const handleConfirmDeleteValue = () => {
    setDeletingValueName("");
    setValuesToDelete([...valuesToDelete, deletingValueName]);
  };

  const handleAddValue = () => {
    const name = _.uniqueId();
    setValues([...values, { name, value: "" }]);
    setCreatedValues([...createdValues, name]);
  };

  const handleSubmit = async () => {
    const submitErrors = {};
    let isValid = true;

    values.forEach((el) => {
      isValid = handleValidateValueOnSubmit(el.name, el.value);
    });

    if (isValid) {
      setIsLoading(true);
      // values => to update, to create, to delete
      if (!_.isEmpty(valuesToDelete)) {
        await Promise.all(
          // delete only existing values
          valuesToDelete
            .filter((name) => defaultValuesNames.includes(name))
            .map(async (name) => {
              try {
                await onDelete(name);
              } catch (_error) {
                isValid = false;
                setValuesToDelete(values.filter((_name) => _name !== name));
                submitErrors[name] = _error.message;
              }
            }),
        );
      }
      if (!_.isEmpty(valuesToUpdate)) {
        await Promise.all(
          // exclude existing values
          valuesToUpdate
            .filter((el) => !defaultValues.includes(el.value))
            .map(async (el) => {
              try {
                await onUpdate(el.name, el.value);
              } catch (_error) {
                isValid = false;
                submitErrors[el.name] = _error.message;
              }
            }),
        );
      }
      if (!_.isEmpty(valuesToCreate)) {
        await Promise.all(
          valuesToCreate.map(async (el) => {
            try {
              await onCreate(el.value);
              setCreatedValues(valuesToCreate.filter((name) => name !== el.name));
            } catch (_error) {
              isValid = false;
              submitErrors[el.name] = _error.message;
            }
          }),
        );
      }
      setErrors(submitErrors);
      setIsLoading(false);
      onLoadMetadata();
      if (isValid) {
        handleCloseWithUpdate();
      }
    }
  };

  useEffect(() => {
    return () => handleResetErrors();
  }, []);

  useEffect(() => {
    return () => handleResetValues();
  }, []);

  useEffect(() => {
    if (!_.isEmpty(defaultValues)) {
      setValues(defaultValues);
    } else {
      handleAddValue();
    }
  }, []);

  return (
    <UIDialogForm
      title={title}
      disableEscapeKeyDown
      isOpen={isOpen}
      onClose={handleClose}
      aria-labelledby={title}
      actionsComponent={
        <>
          <Button onClick={handleClose} color="primary" variant="outlined" fullWidth>
            {t("dialog-form-metadata-values.btn-action-cancel")}
          </Button>
          <Button
            onClick={handleSubmit}
            color="primary"
            variant="contained"
            disabled={isDisabledSubmit}
            fullWidth
          >
            {t("dialog-form-metadata-values.btn-action-save")}
          </Button>
        </>
      }
    >
      <>
        <Box mt={1} mb={2}>
          <Alert severity="info">{description}</Alert>
        </Box>
        {isLoading ? (
          <ElementLoader isOpen type="TailSpin" />
        ) : (
          <>
            <Box className={classes.formWrapper}>
              {!_.isEmpty(values)
                ? valuesToShow.map((value, valueIndex) => (
                    <Box
                      className={`${classes.formWrap} ${classes.dictItemWrapper}`}
                      key={value.name}
                    >
                      <TextFieldForm
                        id={value.name}
                        name={value.name}
                        error={Boolean(errors[value.name])}
                        helperText={errors[value.name]}
                        isUpdateWithDefault={false}
                        onChange={(_name, _val) => handleChangeValue(_name, _val, valueIndex)}
                        defaultValue={value?.value}
                        variant="outlined"
                        margin="dense"
                        placeholder={t("dialog-form-metadata-values.placeholder-value")}
                        // if some field has errors other will be disable until fix
                        disabled={!_.isEmpty(errors) && !errors[value.name]}
                        size="small"
                        required
                        autoFocus
                      />
                      <Box display={"flex"} alignItems={"flex-end"} flex={1}>
                        <Tooltip title="" placement="top">
                          <IconButton
                            className={classes.deleteBtn}
                            onClick={(_e) => handleDeleteValue(value.name)}
                            size="large"
                          >
                            <DeleteForeverOutlinedIcon style={{ color: theme.colorDeleteIcons }} />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </Box>
                  ))
                : null}
            </Box>
            <Box className={classes.formWrap}>
              <Button
                color="primary"
                variant="outlined"
                size="small"
                startIcon={<AddOutlinedIcon />}
                onClick={handleAddValue}
              >
                {t("dialog-form-metadata-values.btn-add")}
              </Button>
            </Box>
          </>
        )}
      </>
      {deletingValueName ? (
        <DialogConfirm
          isOpen={Boolean(deletingValueName)}
          title={t("dialog-form-metadata-values.dialog-delete-alert-title")}
          text={t("dialog-form-metadata-values.dialog-delete-alert-description", {
            name: deletingValueValue,
          })}
          onConfirm={handleConfirmDeleteValue}
          onCancel={() => setDeletingValueName("")}
          cancelText={t("dialog-confirm-delete.cancel")}
          confirmText={t("dialog-confirm-delete.delete")}
        />
      ) : null}
      {isShowAlertUnsaved ? (
        <DialogConfirm
          isOpen={isShowAlertUnsaved}
          title={t("dialog-form-metadata-values.dialog-alert-unsaved-title")}
          text={t("dialog-form-metadata-values.dialog-alert-unsaved-description", {
            name: deletingValueValue,
          })}
          onCancel={handleCloseUnsavedAlert}
          onConfirm={handleConfirmClose}
          cancelText={t("dialog-confirm-close.cancel")}
          confirmText={t("dialog-confirm-close.confirm")}
        />
      ) : null}
    </UIDialogForm>
  );
};

DialogFormMetadataValues.propTypes = {
  onUpdate: PropTypes.func,
  onCreate: PropTypes.func,
  onDelete: PropTypes.func,
  onClose: PropTypes.func,
  defaultValues: PropTypes.array,
};

DialogFormMetadataValues.defaultProps = {
  onUpdate: () => {},
  onCreate: () => {},
  onDelete: () => {},
  onClose: () => {},
  defaultValues: [],
};

export default DialogFormMetadataValues;
