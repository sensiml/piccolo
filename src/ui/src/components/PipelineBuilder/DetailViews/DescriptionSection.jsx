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
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import clsx from "clsx";
import {
  Avatar,
  CardActions,
  CardContent,
  Collapse,
  IconButton,
  Tooltip,
  Typography,
} from "@mui/material";
import useStyles from "./DetailViewStyles";

export default function DescriptionSection({ transform }) {
  const classes = useStyles();

  const [expanded, setExpanded] = React.useState(false);

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };
  return transform && transform.description ? (
    <>
      <CardActions disableSpacing>
        <Tooltip title="Description">
          <IconButton
            className={clsx(classes.expand, {
              [classes.expandOpen]: expanded,
            })}
            onClick={handleExpandClick}
            aria-expanded={expanded}
            aria-label="show more"
            size="large"
          >
            <Avatar aria-label="description" className={classes.descriptionExpander}>
              <ExpandMoreIcon />
            </Avatar>
          </IconButton>
        </Tooltip>
      </CardActions>
      <Collapse in={expanded} timeout="auto" unmountOnExit>
        <CardContent>
          <Typography paragraph>Description:</Typography>
          <Typography component={"span"}>
            <pre className={classes.description}>{transform.description}</pre>
          </Typography>
        </CardContent>
      </Collapse>
    </>
  ) : null;
}
