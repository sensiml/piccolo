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
import makeStyles from "@mui/styles/makeStyles";
import { CardContent, CardActions, CardMedia, Button, Box } from "@mui/material";

import { useTranslation } from "react-i18next";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import DeleteForeverOutlinedIcon from "@mui/icons-material/DeleteForeverOutlined";
import Typography from "@mui/material/Typography";

import { UICard } from "components/UICards";

const useStyles = () =>
  makeStyles((theme) => ({
    selectCard: {
      display: "grid",
      gridTemplateRows: `auto  ${theme.spacing(8)}`,
      minHeight: "320px",
      "&:hover": {
        boxShadow: `0px 8px 12px 0px  ${theme.shadowColor}`,
      },
    },

    selectCardWrapper: {},

    infoIcon: {
      color: theme.colorInfoLinks,
      fontSize: theme.spacing(3),
    },

    deleteIcon: {
      color: theme.colorDeleteIcons,
      fontSize: theme.spacing(3),
    },

    headerCardWrapper: {
      position: "relative",
      lineHeight: 1.2,
    },

    headerTitleWTImage: {
      textAlign: "center",
      padding: "0 1rem",
      paddingTop: theme.spacing(5),
    },

    headerTitleImage: {
      textAlign: "center",
      padding: "0 1rem",
      marginTop: theme.spacing(2),
      marginBottom: theme.spacing(2),
    },

    headerInfoIcon: {
      position: "absolute",
      top: theme.spacing(2),
      right: theme.spacing(2),
    },

    cardContentWrapper: {
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      position: "relative",
      padding: "2rem 1rem",
    },

    actionButton: {
      padding: theme.spacing(1),
      width: "100%",
    },

    media: {
      height: "150px",
      width: "100%",
    },
    cardAction: {
      padding: theme.spacing(2),
    },
    cardImg: {
      backgroundSize: "contain",
    },
  }))();

// eslint-disable-next-line no-unused-vars
const IconInfoBtn = ({ classes }) => {
  return (
    <InfoOutlinedIcon classes={{ root: classes.infoIcon }} className={classes.headerInfoIcon} />
  );
};

// eslint-disable-next-line no-unused-vars
const IconDeleteBtn = () => {
  const classes = useStyles();

  return <DeleteForeverOutlinedIcon classes={{ root: classes.cardImg }} />;
};

const Header = ({ header }) => {
  const classes = useStyles();

  return (
    <Box classes={{ root: classes.headerCardWrapper }}>
      <Typography variant="h4" component="h4" classes={{ root: classes.headerTitleWTImage }}>
        {header}
      </Typography>
    </Box>
  );
};

const HeaderWithImage = ({ imageSrc, header }) => {
  const classes = useStyles();

  return (
    <>
      <Typography variant="h4" component="h4" classes={{ root: classes.headerTitleImage }}>
        {header}
      </Typography>
      <CardMedia
        className={classes.media}
        image={imageSrc}
        title=""
        classes={{ root: classes.cardImg }}
      />
    </>
  );
};

export default ({ header, btnText, image, children, onClickBuild, isBuildDisabled }) => {
  const classes = useStyles();
  const { t } = useTranslation("models");

  const handleClickBuild = () => {
    onClickBuild();
  };

  return (
    <UICard classes={{ root: classes.selectCard }}>
      <Box className={classes.selectCardWrapper}>
        {image ? <HeaderWithImage imageSrc={image} header={header} /> : <Header header={header} />}
        <CardContent classes={{ root: classes.cardContentWrapper }}>{children}</CardContent>
      </Box>
      <CardActions classes={{ root: classes.cardAction }} disableSpacing>
        <Button
          onClick={handleClickBuild}
          variant="contained"
          color="primary"
          className={classes.actionButton}
          disabled={isBuildDisabled}
          disableElevation
        >
          {btnText || t("model-builder-select.card-btn-action")}
        </Button>
      </CardActions>
    </UICard>
  );
};
