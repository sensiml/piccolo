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

/* eslint-disable default-case */
/* eslint-disable prefer-destructuring */
import { select } from "d3-selection";
import { scaleIdentity, scaleLinear } from "d3-scale";
import { dispatch } from "d3-dispatch";
import { rebind } from "@d3fc/d3fc-rebind";
import { dataJoin } from "@d3fc/d3fc-data-join";
import { brush as d3Brush, brushX as d3BrushX, brushY as d3BrushY } from "d3-brush";

const brushForOrient = (orient) => {
  switch (orient) {
    case "x":
      return d3BrushX();
    case "y":
      return d3BrushY();
    case "xy":
      return d3Brush();
  }
};

const invertRange = (range) => [range[1], range[0]];

const brushBase = (orient) => {
  const brush = brushForOrient(orient);
  const eventDispatch = dispatch("brush", "start", "end");
  let xScale = scaleIdentity();
  let yScale = scaleIdentity();

  const innerJoin = dataJoin("g", "brush");

  const mapSelection = (selection, xMapping, yMapping) => {
    switch (orient) {
      case "x":
        return selection.map(xMapping);
      case "y":
        return selection.map(yMapping);
      case "xy":
        return [
          [xMapping(selection[0][0]), yMapping(selection[0][1])],
          [xMapping(selection[1][0]), yMapping(selection[1][1])],
        ];
    }
  };

  const percentToSelection = (percent) =>
    mapSelection(
      percent,
      scaleLinear().domain(xScale.range()).invert,
      scaleLinear().domain(invertRange(yScale.range())).invert,
    );

  const selectionToPercent = (selection) =>
    mapSelection(
      selection,
      scaleLinear().domain(xScale.range()),
      scaleLinear().domain(invertRange(yScale.range())),
    );

  const updateXDomain = (selection) => {
    const f = scaleLinear().domain(xScale.domain());
    if (orient === "x") {
      return selection.map(f.invert);
    } else if (orient === "xy") {
      return [f.invert(selection[0][0]), f.invert(selection[1][0])];
    }
  };

  const updateYDomain = (selection) => {
    const g = scaleLinear().domain(invertRange(yScale.domain()));
    if (orient === "y") {
      return [selection[1], selection[0]].map(g.invert);
    } else if (orient === "xy") {
      return [g.invert(selection[1][1]), g.invert(selection[0][1])];
    }
  };

  const transformEvent = (event, brush, container) => {
    if (event.sourceEvent && event.sourceEvent.type === "draw") return;

    const moveBrush = ([start, end]) => {
      container.call(brush).call(brush.move, [start, end]);
    };

    if (event.selection) {
      const mappedSelection = selectionToPercent(event.selection);
      eventDispatch.call(
        event.type,
        {},
        {
          moveBrush,
          selection: mappedSelection,
          windowlSelection: event.selection,
          xDomain: updateXDomain(mappedSelection),
          yDomain: updateYDomain(mappedSelection),
        },
      );
    } else {
      eventDispatch.call(event.type, {}, {});
    }
  };

  const base = (selection) => {
    selection.each((data, index, group) => {
      // set the extent
      brush.extent([
        [xScale.range()[0], yScale.range()[1]],
        [xScale.range()[1], yScale.range()[0]],
      ]);

      // forwards events

      // render
      const container = innerJoin(select(group[index]), [data]);

      brush
        .on("end", (event) => transformEvent(event, brush, container))
        .on("brush", (event) => transformEvent(event, brush, container))
        .on("start", (event) => transformEvent(event, brush, container));

      container.call(brush).call(brush.move, data ? percentToSelection(data) : null);
    });
  };

  base.xScale = (...args) => {
    if (!args.length) {
      return xScale;
    }
    xScale = args[0];
    return base;
  };

  base.yScale = (...args) => {
    if (!args.length) {
      return yScale;
    }
    yScale = args[0];
    return base;
  };

  rebind(base, eventDispatch, "on");
  rebind(base, brush, "filter", "handleSize");

  return base;
};

export const brushX = () => brushBase("x");

export const brushY = () => brushBase("y");

export const brush = () => brushBase("xy");
