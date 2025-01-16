import React from "react";
import { Box, Paper } from "@mui/material";
import { useTheme } from "@mui/material/styles";

const UIPaperNoContent = ({ text, height, elevation = 0 }) => {
  const theme = useTheme();

  return (
    <Paper elevation={elevation}>
      <Box
        height={height}
        minHeight={theme.spacing(10)}
        display={"flex"}
        justifyContent={"center"}
        alignItems={"center"}
      >
        {text}
      </Box>
    </Paper>
  );
};

export default UIPaperNoContent;
