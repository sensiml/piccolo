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

import React, { useState, useEffect } from "react";
import makeStyles from "@mui/styles/makeStyles";
import { CardMedia, Button, Box } from "@mui/material";

import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import DeleteForeverOutlinedIcon from "@mui/icons-material/DeleteForeverOutlined";
import Typography from "@mui/material/Typography";
import Card from "@mui/material/Card";

const useStyles = () =>
  makeStyles((theme) => ({
    selectCard: {
      // display: "grid",
      gridTemplateRows: `auto  ${theme.spacing(8)}`,
      minHeight: "100px",
      "&:hover": {
        boxShadow: `0px 8px 12px 0px  ${theme.shadowColor}`,
        cursor: "pointer",
      },
      height: "160px",
      display: "flex",
      flexDirection: "column",
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
      paddingTop: theme.spacing(4),
    },

    headerTitleImage: {
      textAlign: "center",
      marginTop: theme.spacing(4),
      justifyContent: "bottom",
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
    },

    actionButton: {
      // padding: theme.spacing(1),
      borderRadius: "0",
      width: "100%",
      marginTop: "auto",
      alignItems: "center",
      justifyContent: "center",
    },

    media: {
      height: "15px",
      width: "100%",
      alignItems: "center",
      justifyContent: "center",
    },
    cardAction: {
      // padding: theme.spacing(4),
      // height: "10px",
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
    },
    cardImg: {
      backgroundSize: "contain",
      marginTop: theme.spacing(2),
    },

    checked: {
      borderColor: theme.palette.primary.main,
      background: theme.bakgroundPrimaryHighligth,
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
      <CardMedia
        className={classes.media}
        image={imageSrc}
        title=""
        classes={{ root: classes.cardImg }}
      />
      <Typography variant="h4" component="h4" classes={{ root: classes.headerTitleImage }}>
        {header}
      </Typography>
    </>
  );
};

const CheckBoxSelectCard = ({
  header,
  btnText,
  image,
  defaultValue,
  onClickButton,
  isButtonDisabled,
  id,
  value,
  onChange,
}) => {
  const classes = useStyles();

  const [localVal, setLocalVal] = useState();

  useEffect(() => {
    if (!onChange) return;
    if (defaultValue) {
      onChange(name, defaultValue);
      setLocalVal(defaultValue);
    } else {
      onChange(name, false);
      setLocalVal(false);
    }
  }, []);

  useEffect(() => {
    setLocalVal(value);
  }, [value]);

  const handleChange = () => {
    if (localVal) {
      return;
    }
    if (onChange) {
      onChange(name, !localVal);
    }
    setLocalVal(!localVal);
  };

  const handleClickButton = () => {
    onClickButton();
  };

  return (
    <Card
      variant="outlined"
      id={id}
      className={localVal ? classes.checked : ""}
      classes={{ root: classes.selectCard }}
      onClick={handleChange}
    >
      <Box className={classes.selectCardWrapper}>
        {image ? <HeaderWithImage imageSrc={image} header={header} /> : <Header header={header} />}
      </Box>

      {localVal ? (
        <Button
          onClick={handleClickButton}
          variant="contained"
          color="primary"
          className={classes.actionButton}
          disabled={isButtonDisabled}
          disableElevation
        >
          {btnText}
        </Button>
      ) : (
        <></>
      )}
    </Card>
  );
};

export default CheckBoxSelectCard;
