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
import { lightBlue, deepOrange, red, blueGrey, grey } from "@mui/material/colors";
import { useTheme, createTheme, ThemeProvider, StyledEngineProvider } from "@mui/material/styles";

import DialogFormStyles from "components/ThemesStyles/DialogFormStyles";

const LightTheme = (props) => {
  const theme = useTheme();

  const currentTheme = createTheme({
    irection: "rtl",
    common: {
      ...DialogFormStyles(theme),
      spinnedIcon: {
        animation: `$spin`,
        animationDuration: "2000ms",
        animationIterationCount: "infinite",
        animationTimingFunction: "linear",
      },

      "@keyframes spin": {
        from: {
          transform: "rotate(0deg)",
        },
        to: {
          transform: "rotate(360deg)",
        },
      },
      // .element {
      //   width: 100%;
      //   height: 100%;
      //   animation: pulse 5s infinite;
      // }

      flashingAction: {
        animationName: `$flashing_action`,
        animationDuration: "1s",
        animationTimingFunction: "ease-out",
        animationDelay: "0",
        animationDirection: "alternate",
        animationIterationCount: "infinite",
        animationFillMode: "none",
        animationPlayState: "running",
        padding: "0.25rem",
        border: "1px solid",
      },

      "@keyframes flashing_action": {
        "0%": {
          transform: "scale(1)",
          backgroundColor: "rgba(240, 166, 171, 0.15)",
          borderColor: "rgba(240, 166, 171, 0.25)",
        },
        "100%": {
          transform: "scale(1.1)",
          backgroundColor: "rgba(240, 166, 171, 0.50)",
          borderColor: "rgba(240, 166, 171, 0.65)",
        },
      },
      mt1: {
        marginTop: "0.5rem",
      },
      mr1: {
        marginRight: "0.5rem",
      },
      ml1: {
        marginLeft: "0.5rem",
      },
      ml2: {
        marginLeft: "1rem",
      },
      mt2: {
        marginTop: "1rem",
      },
      mb2: {
        marginBottom: "1rem",
      },
      mh2: {
        margin: "1rem 0",
      },
      curtainWrapper: {
        margin: `0.5rem 0`,
        justifyContent: "center",
      },
      // tab
      tabWithCircularProgress: {
        display: "inline-grid",
        gridTemplateColumns: "auto auto",
        alignItems: "center",
        columnGap: "0.5rem",
      },
      loadedElement: {
        position: "relative",
      },
      infoIcon: {
        color: "#70CE80",
      },
      deleteIcon: {
        color: "#E14D57",
      },
      editIcon: {
        color: "#81A4D8",
      },
      actionIcon: {
        cursor: "pointer",
        color: lightBlue[800],
      },
    },
    responsive: {
      minWidthContainer: "350px",
    },
    ml1: {
      marginLeft: "0.5rem",
    },
    ml2: {
      marginLeft: "1rem",
    },
    mr2: {
      marginRight: "1rem",
    },

    shadowColor: blueGrey[100],

    backgroundElements: "#ffff",
    // backgroundApp: "#e2e4e5",
    backgroundApp: "linear-gradient(90deg, rgba(244,245,247,1) 0%, rgba(227,228,229,1) 60%);",
    backgroundBackDoor: "rgba(0, 0, 0, 0.12)",
    backgroundLoaderBackdrop: "rgb(244 245 247 / 90%)",
    backgroundLoaderElementBackdrop: "#ffff",
    bakgroundPrimaryHighligth: "rgb(2 119 189 / 5%)",
    bakgroundTableHeader: "#ffff",
    bakgroundTableDarkHeader: "#f5f5f5",
    bakgroundSelected: "rgba(2, 119, 189, 0.08)",

    colorRegularText: blueGrey[800],
    colorRegularHeader: blueGrey[800],
    colorBrandText: "#0071C5",
    colorInfoText: "#4D7690",
    colorInfoLinks: "#70CE80",

    colorLightBrandIcon: "#81A4D8",
    colorDeleteIcons: "#E14D57",
    colorEditIcons: "#81A4D8",
    colorNewItems: "#4D7690",

    borderBrandTransparent: "rgba(1, 119, 189, 30%)",
    borderBrandGradient:
      // eslint-disable-next-line max-len
      `linear-gradient(90deg, ${lightBlue[800]} 28%, rgba(255,255,255,1) 100%, rgba(255,255,255,1) 100%)`,

    tableBorderColor: "#e0e0e0",
    // console components

    backgroundConsole: "#585858",
    backgroundConsoleBody: "#2d2d2d",

    colorConsoleBody: "#ffff",
    colorConsoleInfoText: "#a8a8a8",
    colorConsoleSuccessIcon: "#70CE80",
    colorConsoleInfoIcon: "#0277bd",
    colorConsoleWarningIcon: "#e4bc7d",
    colorConsoleErrorIcon: "#E14D57",

    colorConsoleScrollTrackBg: "black",
    colorConsoleScrollBg: "#0277bd",

    // charts Plot
    plotBG: "#f6f9ffb8",

    spacing: (factor) => `${0.5 * factor}rem`, // (Bootstrap strategy)
    colorLoader: "rgba(0, 191, 255, 0.7)",

    palette: {
      mode: "light",
      scrollBg: "#c1c1c1",
      primary: {
        light: lightBlue[600],
        main: lightBlue[800],
        dark: lightBlue[900],
        contrastText: "#ffff",
      },
      accent: {
        light: deepOrange[200],
        main: deepOrange[500],
        dark: deepOrange[800],
        contrastText: theme.palette.getContrastText(deepOrange[500]),
      },
      secondary: {
        light: lightBlue[600],
        main: lightBlue[700],
        dark: lightBlue[800],
        contrastText: theme.palette.getContrastText(lightBlue[600]),
      },
      notSelected: {
        light: blueGrey[500],
        main: blueGrey[700],
        dark: blueGrey[800],
        contrastText: theme.palette.getContrastText(blueGrey[600]),
      },
      error: {
        light: red[200],
        main: red[500],
        dark: red[800],
        contrastText: theme.palette.getContrastText(red[500]),
      },
      text: {
        primary: blueGrey[800],
        secondary: grey[600],
        disabled: blueGrey[500],
        hint: lightBlue[600],
      },
    },
    typography: {
      h1: {
        color: blueGrey[800],
        fontWeight: 600,
        fontSize: "1.5rem",
      },
      h2: {
        color: blueGrey[800],
        fontWeight: 600,
        fontSize: "1.5rem",
      },
      h3: {
        color: blueGrey[800],
        fontWeight: 600,
        fontSize: "1.5rem",
      },
      h4: {
        color: blueGrey[800],
        fontWeight: 600,
        fontSize: "1.1rem",
      },
      h5: {
        color: blueGrey[800],
        fontWeight: 500,
        fontSize: "1.1rem",
      },
    },
    components: {
      MuiTableCell: {
        styleOverrides: {
          root: {
            padding: "6px 24px 6px 16px",
          },
        },
      },
    },
    overrides: {
      MuiBox: {
        boxSizing: "border-box",
      },
      MuiTableCell: {
        sizeSmall: {
          "@media (max-width: 1440px)": {
            padding: theme.spacing(1),
          },
        },
      },
      MuiTableSortLabel: {
        root: {
          color: blueGrey[800],
          "&:focus": {
            color: blueGrey[800],
          },
          "&:hover": {
            color: blueGrey[800],
            "&& $icon": {
              color: blueGrey[800],
            },
          },
          "&$active": {
            color: blueGrey[800],
            "&& $icon": {
              color: blueGrey[800],
            },
          },
          icon: {
            color: "white",
          },
        },
      },
    },
  });

  return (
    <StyledEngineProvider injectFirst>
      <ThemeProvider theme={currentTheme}>{props.children}</ThemeProvider>
    </StyledEngineProvider>
  );
};

export default LightTheme;
