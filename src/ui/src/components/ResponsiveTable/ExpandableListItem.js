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

/* eslint-disable react/prefer-stateless-function */
import React, { Component } from "react";
// import ReactDOM from "react-dom";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import Accordion from "@mui/material/Accordion";
import AccordionSummary from "@mui/material/AccordionSummary";
import AccordionDetails from "@mui/material/AccordionDetails";
import Typography from "@mui/material/Typography";
import withStyles from "@mui/styles/withStyles";

const styles = {
  summaryText: {
    width: "100%",
  },
  detailsText: {
    width: "100%",
  },
};

/* Expandable component with header text (summary) and expandable description text (details)  */
class ExpandableListItem extends Component {
  // componentWillReceiveProps(nextProps) {
  //   if (nextProps.selected && nextProps.scrollToSelected) {
  //     ReactDOM.findDOMNode(this).scrollIntoView(
  //       nextProps.scrollOptions || { behavior: "smooth", block: "center" }
  //     );
  //   }
  // }

  render() {
    const {
      classes,
      panelClass,
      details,
      selected,
      summary,
      AccordionDetailsProps,
      AccordionDetailsTypographyProps,
      AccordionMoreIconProps,
      AccordionProps,
      AccordionSummaryProps,
      AccordionSummaryTypographyProps,
      SelectedExpansionPanelProps,
    } = this.props;

    const rootProps = selected
      ? { ...AccordionProps, ...SelectedExpansionPanelProps }
      : AccordionProps;

    return (
      <Accordion className={panelClass && panelClass} {...rootProps}>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon {...AccordionMoreIconProps} />}
          {...AccordionSummaryProps}
        >
          <Typography
            classes={{
              root: classes.summaryText,
            }}
            gutterBottom
            variant="subtitle1"
            {...AccordionSummaryTypographyProps}
          >
            {summary}
          </Typography>
        </AccordionSummary>
        <AccordionDetails {...AccordionDetailsProps}>
          <Typography
            classes={{
              root: classes.detailsText,
            }}
            gutterBottom
            component="div"
            {...AccordionDetailsTypographyProps}
          >
            {details}
          </Typography>
        </AccordionDetails>
      </Accordion>
    );
  }
}
export default withStyles(styles)(ExpandableListItem);
