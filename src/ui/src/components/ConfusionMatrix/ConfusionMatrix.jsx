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

/* eslint-disable guard-for-in */
/* eslint-disable no-restricted-syntax */
import React, { useState, useEffect } from "react";
import { Typography, Tooltip } from "@mui/material";
import StandardTable from "components/StandardTable";
import { useTranslation } from "react-i18next";
import useStyles from "./ConfusionMatrixStyles";

const matrixColumnNames = {
  TOTAL: "Predicted",
  SUPPORT: "Support",
  UNC: "UNC",
  UNK: "UNK",
  POSTPRED: "Pos_Predic(%)",
  SENSPERC: "Sensitivity(%)",
  GroundTruth_Total: "GroundTruth_Total",
  GroundTruth_Title: "Ground Truth",
};
const ACCOUNT_PERC = "Acc(%)";

const ConfusionMatrix = ({ model, showTitle, modelName, fileName }) => {
  const classes = useStyles();
  const [confusionMatrix, setConfusionMatrix] = useState({
    data: null,
    isFetching: model.isFetching,
  });
  const [matrixColumns, setMatrixColumns] = useState();

  const { t } = useTranslation("models");

  /** ** Cell Stylers **** */

  const labelCellStyleHandler = (col, row, stClasses) => stClasses.tableMainCell;

  const getGreenStyle = (number, stClasses) => {
    switch (number) {
      case 0:
        return stClasses.tableRowGreen;
      case 10:
        return stClasses.tableRowGreen10;
      case 20:
        return stClasses.tableRowGreen20;
      case 30:
        return stClasses.tableRowGreen30;
      case 40:
        return stClasses.tableRowGreen40;
      case 50:
        return stClasses.tableRowGreen50;
      case 60:
        return stClasses.tableRowGreen60;
      case 70:
        return stClasses.tableRowGreen70;
      case 80:
        return stClasses.tableRowGreen80;
      case 90:
        return stClasses.tableRowGreen90;
      case 100:
        return stClasses.tableRowGreen100;
      default:
        return stClasses.tableRowGreen;
    }
  };

  const getRedStyle = (number, stClasses) => {
    switch (number) {
      case 0:
        return stClasses.tableRowRed;
      case 10:
        return stClasses.tableRowRed10;
      case 20:
        return stClasses.tableRowRed20;
      case 30:
        return stClasses.tableRowRed30;
      case 40:
        return stClasses.tableRowRed40;
      case 50:
        return stClasses.tableRowRed50;
      case 60:
        return stClasses.tableRowRed60;
      case 70:
        return stClasses.tableRowRed70;
      case 80:
        return stClasses.tableRowRed80;
      case 90:
        return stClasses.tableRowRed90;
      case 100:
        return stClasses.tableRowRed100;
      default:
        return stClasses.tableRowGreen;
    }
  };

  const matrixDataCellStyleHandler = (col, row, stClasses) => {
    const data = row[col.field];
    const totalCount = row.support;
    let clsNm = null;

    // Highlight actual matrix cells with data, to Red if it is a diagonal cell else to red
    if (data !== 0 && totalCount !== 0) {
      const ratio = Math.round(((data / totalCount) * 100) / 10) * 10;
      const newLocal = row.label === col.title;
      clsNm = newLocal ? getGreenStyle(ratio, stClasses) : getRedStyle(ratio, stClasses);
    }

    // Do not highlight the cell for the postpred row
    if (row.label === matrixColumnNames.POSTPRED) clsNm = null;

    // If row label is total or column title is support, style the cell to darker blue
    if (
      row.label === matrixColumnNames.TOTAL ||
      col.title === matrixColumnNames.SUPPORT ||
      col.title === matrixColumnNames.GroundTruth_Title
    ) {
      clsNm = stClasses.tableDelimiteddBlue;
    }

    return `${stClasses.tableGenericCenteredCell} ${clsNm}`;
  };

  const dataCellStyleHandler = (col, row, stClasses) =>
    `${stClasses.tableGenericCenteredCell} ${
      row.label === matrixColumnNames.TOTAL ||
      col.title === matrixColumnNames.SUPPORT ||
      col.title === matrixColumnNames.GroundTruth_Title
        ? stClasses.tableDelimiteddBlue
        : null
    }`;

  /** ** Data formaters **** */

  const drawLabel = (column) => column.title;

  const customSupport = (column) => {
    return (
      <Tooltip title={t("confusion-matrix.support")}>
        <Typography> {column.title} </Typography>
      </Tooltip>
    );
  };

  const customGroundTruth = (column) => {
    return (
      <Tooltip title={t("confusion-matrix.ground-truth")}>
        <Typography> {column.title} </Typography>
      </Tooltip>
    );
  };

  const customSensitivity = (column) => {
    return (
      <Tooltip title={t("confusion-matrix.sensitivity")}>
        <Typography> {column.title} </Typography>
      </Tooltip>
    );
  };

  const customUNK = (column) => {
    return (
      <Tooltip title={t("confusion-matrix.unk")}>
        <Typography> {column.title} </Typography>
      </Tooltip>
    );
  };

  const drawLabelData = (data) => {
    if (data && data === matrixColumnNames.TOTAL) {
      return (
        <Tooltip title={t("confusion-matrix.predicted")}>
          <Typography> {data} </Typography>
        </Tooltip>
      );
    }

    if (data && data === matrixColumnNames.POSTPRED) {
      return (
        <Tooltip title={t("confusion-matrix.positive-predictivity")}>
          <Typography> {data} </Typography>
        </Tooltip>
      );
    }

    return !data || isNaN(data) || data === "" ? data : Number(data).toFixed(2);
  };

  /** ** sort Comparers **** */
  const labelColumnComparer = (a, b) => {
    const fieldA = a.field;
    const fieldB = b.field;

    let comparison = 0;
    if (fieldA > fieldB) {
      comparison = 1;
    } else if (fieldA < fieldB) {
      comparison = -1;
    }
    return comparison;
  };

  const rowComparer = (a, b) => {
    const fieldA = a.label;
    const fieldB = b.label;

    let comparison = 0;
    if (fieldA > fieldB) {
      comparison = 1;
    } else if (fieldA < fieldB) {
      comparison = -1;
    }
    return comparison;
  };

  useEffect(() => {
    const formatValue = (num) => +`${Math.round(`${num}e+2`)}e-2`;

    setConfusionMatrix({ data: [], isFetching: model.isFetching });
    const matrixData = [];
    let hasGroundruth = false;
    let columns = [];
    let unknownUNK = 0;
    if (model.data) {
      const confusionMatrixData = model.data;
      columns.push({
        title: "",
        field: "label",
        primary: true,
        renderLabel: drawLabel,
        render: drawLabelData,
        handleCellStyles: labelCellStyleHandler,
      });
      let i = 0;
      const totalRow = {
        label: matrixColumnNames.TOTAL,
      };
      let labelCols = [];
      for (const x in confusionMatrixData) {
        const row = { label: x };
        let support = 0;
        for (const y in confusionMatrixData[x]) {
          totalRow[y] = totalRow[y] ? totalRow[y] : 0;
          if (i === 0) {
            labelCols.push({
              title: y,
              field: y,
              primary: true,
              renderLabel: drawLabel,
              handleCellStyles: matrixDataCellStyleHandler,
            });

            if (y === matrixColumnNames.GroundTruth_Total) {
              hasGroundruth = true;
            }
          }
          row[y] = formatValue(confusionMatrixData[x][y]);
          if (y === matrixColumnNames.UNC) totalRow[y] -= row[y] ? row[y] : 0;
          else totalRow[y] += row[y] ? row[y] : 0;
          if (y === matrixColumnNames.UNK && x.toLowerCase() === "unknown") {
            unknownUNK += confusionMatrixData[x][y] ? confusionMatrixData[x][y] : 0;
          }

          if (y !== matrixColumnNames.GroundTruth_Total) {
            support += confusionMatrixData[x][y] ? confusionMatrixData[x][y] : 0;
          }
        }
        row.support = support;
        row.sense_perc =
          support === 0 ? "" : Number((100 * (row[x] + unknownUNK)) / support).toFixed(2);
        totalRow.support = (totalRow.support ? totalRow.support : 0) + row.support;
        totalRow.sense_perc = "";
        i++;
        matrixData.push(row);
      }
      matrixData.sort(rowComparer);
      matrixData.push(totalRow);

      // Sort with out UNK and UNC
      labelCols = labelCols.filter(
        (labelCol) =>
          ![
            matrixColumnNames.UNC,
            matrixColumnNames.UNK,
            matrixColumnNames.GroundTruth_Total,
          ].includes(labelCol.field),
      );
      labelCols.sort(labelColumnComparer);
      // Readd UNK and UNC columns after the main labels are sorted
      labelCols.push({
        title: matrixColumnNames.UNK,
        field: matrixColumnNames.UNK,
        primary: true,
        renderLabel: customUNK,
        handleCellStyles: dataCellStyleHandler,
      });
      columns = columns.concat(labelCols);
      const postPredData = { label: matrixColumnNames.POSTPRED };
      let diagonalSum = 0;
      for (const col in columns) {
        const fieldName = columns[col].field;
        if (fieldName !== "label") {
          const fieldRow = matrixData.find((row) => row.label === fieldName);
          if (fieldRow) {
            diagonalSum += fieldRow[fieldName];
            if (totalRow[fieldName] && totalRow[fieldName] !== 0) {
              postPredData[fieldName] = Number(
                100 * (fieldRow[fieldName] / totalRow[fieldName]),
              ).toFixed(2);
            } else postPredData[fieldName] = null;
          }
        }
      }
      postPredData.support = ACCOUNT_PERC;
      postPredData.sense_perc =
        totalRow.support === 0
          ? null
          : Number((100 * (diagonalSum + unknownUNK)) / totalRow.support).toFixed(2);
      matrixData.push(postPredData);

      if (hasGroundruth) {
        columns.push({
          title: matrixColumnNames.GroundTruth_Title,
          field: matrixColumnNames.GroundTruth_Total,
          primary: true,
          renderLabel: customGroundTruth,
          handleCellStyles: dataCellStyleHandler,
        });
      }
      columns.push(
        {
          title: matrixColumnNames.SUPPORT,
          field: "support",
          primary: true,
          renderLabel: customSupport,
          handleCellStyles: dataCellStyleHandler,
        },
        {
          title: matrixColumnNames.SENSPERC,
          field: "sense_perc",
          primary: true,
          renderLabel: customSensitivity,
          render: drawLabelData,
          handleCellStyles: dataCellStyleHandler,
        },
      );
    }

    setConfusionMatrix({ data: matrixData, isFetching: false });
    setMatrixColumns(columns);
  }, [model]);

  const title = "";
  const options = {
    rowsPerPage: 100,
    showPagination: false,
    noContentText: "No Data for Confusion Matrix",
    excludePrimaryFromDetails: true,
    headersCentered: true,
    isDarkHeader: true,
  };

  return (
    <div className={classes.centered}>
      {showTitle ? (
        <Typography variant="h2" className={classes.title}>
          {`${title}${modelName ? `${modelName}` : ""}${fileName ? ` - ${fileName}` : ""}`}
        </Typography>
      ) : null}
      <StandardTable
        tableColumns={matrixColumns}
        tableData={confusionMatrix}
        tableOptions={options}
        tableXS={null}
      />
    </div>
  );
};

export default ConfusionMatrix;
