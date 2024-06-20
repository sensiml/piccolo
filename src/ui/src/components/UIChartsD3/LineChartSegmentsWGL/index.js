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

/* eslint-disable no-param-reassign */
/* eslint-disable no-use-before-define */
import _ from "lodash";
import PropTypes from "prop-types";

import React, { useEffect, useState, useMemo, useRef } from "react";

import FormGroup from "@mui/material/FormGroup";
import FormControlLabel from "@mui/material/FormControlLabel";
import Checkbox from "@mui/material/Checkbox";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import PauseIcon from "@mui/icons-material/Pause";
import { Box, Stack, Slider } from "@mui/material";

import * as d3 from "d3";
import * as fc from "d3fc";

import LabelColoredName from "components/LabelColoredName";
import { IconButtonRounded } from "components/UIButtons";
import { DEFAULT_COLORS } from "store/labels/domain";

import { filterFormatSecondsToDuration } from "filters";

import useStyles from "./LineChartSegmentsWGLStyle";
import { brushX } from "./d3fcAdjustedBrush";

import { styled } from "@mui/material/styles";

const AudioSlider = styled(Slider)(() => ({
  "& .MuiSlider-thumb": {
    transition: "none",
  },
  "& .MuiSlider-track": {
    transition: "none",
  },
}));

const SEGMENT_COLOR = "#0071C5";

const xScale = d3.scaleLinear();
const yScale = d3.scaleLinear();

const LineChartSegments = ({
  audioFile,
  data,
  seriesNameList,
  segmentData,
  newSegment,
  editingSegment,
  onSementMove,
  onNewSegmentMove,
  onSetEditedSegment,
  audioFileSampleRate = 16000,
  isReadOnlyMode = false,
}) => {
  const classes = useStyles();
  const audioRef = useRef(null);
  const audioTimerRef = useRef();

  const [activeEditingSegment, setActiveEditingSegment] = useState(-1);
  const [domainData, setDomainData] = useState([1, 1]);

  const [zoomRangeDomain, setZoomRangeDomain] = useState([0, 0]);
  const [zoomRange, setZoomRange] = useState([0, 1]);

  const [unselectedSeries, setUnselectedSeries] = useState([]);

  const [isAudioPlaying, setIsAudioPlaying] = useState(false);
  const [audioCurrentTime, setAudioCurrentTime] = useState(0);
  const [audioDurationTime, setAudioDurationTime] = useState(0);

  const colors = d3.scaleOrdinal(DEFAULT_COLORS).domain([...seriesNameList]);
  const yExtent = fc.extentLinear().accessors([(d) => d.value]);
  const xExtent = fc.extentLinear().accessors([(d) => d.sequence]);

  let aciveBrashId = -1;
  let isNewSementCreating = false;
  let brushedNavigationRange = [0, 1];

  const getSegmentId = (id) => {
    return `segment_${id}`;
  };

  const dataNavigation = useMemo(() => {
    return data[0];
  }, [data]);

  const dataMainChart = useMemo(() => {
    const nameIndexes = data.reduce((acc, dataItem, index) => {
      if (dataItem[0]?.name) {
        acc[index] = dataItem[0]?.name;
      }
      return acc;
    }, {});
    return data.filter((_el, index) => !unselectedSeries.includes(nameIndexes[index]));
  }, [data, unselectedSeries]);

  /**
   * d3 elements
   */
  const d3ElementLine = fc
    .seriesCanvasLine()
    .mainValue((d) => d.value)
    .crossValue((d) => d.sequence);

  const d3ElementLineSeries = fc
    .seriesCanvasRepeat()
    .xScale(xScale)
    .yScale(yScale)
    .series(d3ElementLine)
    .decorate((context, _data, index) => {
      if (_data[index][0]?.name && colors(_data[index][0]?.name)) {
        context.strokeStyle = colors(_data[index][0]?.name);
      } else {
        context.strokeStyle = colors(index);
      }
    })
    .orient("horizontal");

  const navigationLineSeries = fc
    .seriesCanvasLine()
    .mainValue((d) => d.value)
    .crossValue((d) => d.sequence)
    .decorate((context) => {
      context.strokeStyle = SEGMENT_COLOR;
    });

  const invertSelection = (selection = [0, 0]) => {
    const start = Math.round(xScale.invert(selection[0]));
    const end = Math.round(xScale.invert(selection[1]));
    return [start, end];
  };

  const handleUnSelectSeries = (checked, sensor) => {
    if (checked) {
      setUnselectedSeries(unselectedSeries.filter((sensorName) => sensorName !== sensor));
    } else if (unselectedSeries.length < seriesNameList.length - 1) {
      // disable to unSelect las item
      setUnselectedSeries([...unselectedSeries, sensor]);
    }
  };

  const handleSegmentChanges = (evt, id) => {
    if (evt.selection) {
      const [start, end] = invertSelection(evt.selection);
      onSementMove(start, end, id);
    }
  };

  const handleNewSegmentChanges = (evt, id) => {
    if (evt.selection) {
      const [start, end] = invertSelection(evt.selection);
      onNewSegmentMove(start, end, id);
    }
  };

  const drawEditableSegment = (start, end, color, id, _zoomRange) => {
    const container = document.querySelector("d3fc-svg");
    if (!container) {
      return;
    }
    const svgArea = d3.select(container).select("svg");

    setActiveEditingSegment(id);
    if (aciveBrashId !== id) {
      const brushToRemove = svgArea.select(".brushes").select(`#band_brash_${aciveBrashId}`);
      brushToRemove.select(".selection").attr("stroke-width", "0");
    }

    const brashBand = d3.brushX().on("end", (evt) => {
      if (evt?.mode) {
        handleSegmentChanges(evt, id, color);
      }
    });

    const svgAreaWidth = svgArea.node().getBoundingClientRect().width;
    const svgAreaHeight = svgArea.node().getBoundingClientRect().height;

    const brashExtend = [
      [0, 0],
      [svgAreaWidth, svgAreaHeight],
    ];
    if (zoomRange[0] !== 0) {
      // start moving area horizontal, vertical
      brashExtend[0] = [xScale(zoomRange[0]), 0];
    }
    if (zoomRange[1] !== 1) {
      // end moving area horizontal, vertical
      brashExtend[1] = [svgAreaWidth + _.multiply(svgAreaWidth, 1 - zoomRange[1]), svgAreaHeight];
    }
    brashBand.extent(brashExtend);

    const brush = svgArea
      .select(".brushes")
      .append("g")
      .call(brashBand)
      .call(brashBand.move, [xScale(start), xScale(end)])
      .attr("id", `band_brash_${id}`)
      .attr("class", "brash");

    aciveBrashId = id;

    brush.selectAll(".overlay").remove();
    brush
      .selectAll(".selection")
      .attr("fill", color)
      .attr("fill-opacity", "0.5")
      .attr("stroke", SEGMENT_COLOR)
      .attr("stroke-width", "2");
    d3.brushSelection(brush);
  };

  const drawNewSegment = (svgArea, id) => {
    const brashBand = d3.brushX().on("end", (evt) => {
      if (evt?.mode) {
        handleNewSegmentChanges(evt, id);
      }
    });

    const brush = svgArea
      .select(".brushes")
      .append("g")
      .call(brashBand)
      .attr("id", `band_brash_${id}`)
      .attr("class", "brash");

    d3.brushSelection(brush);
  };

  const drawSegmentBand = fc
    .annotationSvgBand()
    .orient("vertical")
    .xScale(xScale)
    .yScale(yScale)
    .fromValue((d) => d.start)
    .toValue((d) => d.end)
    .decorate((sel) => {
      sel
        .attr("id", (d) => getSegmentId(d.id))
        .style("fill", (d) => d.color)
        .style("opacity", "0.5")
        .attr("cursor", "pointer");

      sel.on("click", (e, dataV) => {
        if (!isNewSementCreating) {
          const { id } = dataV;
          onSetEditedSegment(id);
          // d3.select(`#${getSegmentId(id)}`).remove();
          // drawEditableSegment(start, end, color, id);
        }
      });
    });

  const drawSelectedSegmentBand = (start, end, color, id) => {
    const segmentBand = fc
      .annotationSvgBand()
      .orient("vertical")
      .xScale(xScale)
      .yScale(yScale)
      .fromValue(start)
      .toValue(end)
      .decorate((sel) => {
        sel
          .attr("id", getSegmentId(id))
          .attr("fill-opacity", "0.5")
          .attr("fill", color)
          .attr("cursor", "pointer")
          .attr("stroke", SEGMENT_COLOR)
          .attr("stroke-width", "2")
          .attr("class", "brash");
      });
    return segmentBand;
  };

  const drawSegments = (newSegmentId, editingSegmentId) => {
    const container = document.querySelector("d3fc-svg");
    if (!container) {
      return;
    }
    const svgArea = d3.select(container).select("svg");
    const activeSegment = editingSegmentId || activeEditingSegment;

    d3.select(container)
      .on("draw", () => {
        const segmentToEdit = segmentData.find((el) => activeSegment === el.id);
        d3.select(".svg-plot-area").selectAll(".brushes").remove();
        const getData = (_segmentData) => {
          if (zoomRangeDomain[0]) {
            // filter segments according to zoomed area
            return _segmentData.filter(
              (el) =>
                activeSegment !== el.id &&
                el.end > zoomRangeDomain[0] &&
                zoomRangeDomain[1] > el.start,
            );
          }
          return _segmentData.filter((el) => activeSegment !== el.id);
        };
        svgArea.datum(getData(segmentData));
        svgArea.call(drawSegmentBand);
        svgArea.append("g").attr("class", "brushes");

        if (segmentToEdit) {
          if (isReadOnlyMode) {
            svgArea
              .datum([1])
              .select(".brushes")
              .append("g")
              .call(
                drawSelectedSegmentBand(
                  segmentToEdit.start,
                  segmentToEdit.end,
                  segmentToEdit.color,
                  segmentToEdit.id,
                ),
              );
          } else {
            drawEditableSegment(
              segmentToEdit.start,
              segmentToEdit.end,
              segmentToEdit.color,
              segmentToEdit.id,
              zoomRangeDomain,
            );
          }
        }

        if (newSegmentId) {
          drawNewSegment(svgArea, newSegmentId);
        }
        svgArea
          .append("g")
          .append("line")
          .attr("id", "line")
          .attr("x1", 0)
          .attr("stroke-width", 3)
          .attr("y1", 0)
          .attr("x2", 0)
          .attr("y2", 500);
        svgArea.append("use").attr("xlink:href", "#line");
      })
      .on("measure", (_e) => {
        /* Disabled
          const { width, height } = event.detail;
          xScale.range([0, width]).domain(zoomRangeDomain);
         yScale.range([height, 0]).domain(domainData);
        */
      });

    container.requestRedraw();
  };

  const handleSetChartLineProgress = (progress) => {
    const container = document.querySelector("d3fc-svg");
    const svgArea = d3.select(container).select("svg");
    const xDomain = xScale(progress * audioFileSampleRate);

    svgArea.select("line").attr("x1", xDomain).attr("x2", xDomain).attr("stroke", "red");
  };

  let preSelection = d3.scaleLinear().range();

  const handleNavigationBrush = (evt) => {
    // limit minimum size to 10px
    if (evt.windowlSelection && evt.windowlSelection[1] - evt.windowlSelection[0] < 5) {
      evt.moveBrush(preSelection);
    } else {
      preSelection = evt.windowlSelection;
    }

    // limit minimum of selection to 10 samples
    if (evt.xDomain && evt.xDomain[1] - evt.xDomain[0] < 10) {
      return;
    }

    if (evt.selection && evt.selection !== [0, 1]) {
      brushedNavigationRange = evt.selection;
      setZoomRange(brushedNavigationRange);

      const indexRange = [Math.round(evt.xDomain[0]), Math.round(evt.xDomain[1])];
      redraw(indexRange);
    }
  };

  const brushNavigation = brushX()
    .on("brush", handleNavigationBrush)
    .on("end", handleNavigationBrush);

  const navigationMulti = fc
    .seriesSvgMulti()
    .series([brushNavigation])
    // eslint-disable-next-d3ElementLine consistent-return
    .mapping((_data, index, series) => {
      switch (series[index]) {
        case brushNavigation:
          return brushedNavigationRange;
        default:
          return brushedNavigationRange;
      }
    });

  const navigatorChart = fc
    .chartCartesian(xScale.copy(), yScale.copy())
    .yAxisWidth(0)
    .yDomain(yExtent(dataNavigation))
    .xDomain(xExtent(dataNavigation))
    .svgPlotArea(navigationMulti)
    .canvasPlotArea(navigationLineSeries);

  // main

  const multi1 = fc.seriesSvgMulti().series([]);

  const redraw = (indexRange = zoomRangeDomain) => {
    setZoomRangeDomain(indexRange);
    let updData = [...dataMainChart];
    if ((indexRange[0] || indexRange[1]) && d3.select("#chart")) {
      updData = dataMainChart.map((dataItem) =>
        _.filter(dataItem, (el) => el.sequence > indexRange[0] && el.sequence < indexRange[1]),
      );
    }

    const domaninData = updData.reduce((acc, elData) => _.union(acc, elData), []);

    const xDomain = xExtent(domaninData);
    const yDomain = yExtent(domaninData);
    const updChart = fc
      .chartCartesian({
        xScale,
        yScale,
        xAxis: {
          bottom: (scale, _data) => {
            return fc.axisBottom(scale);
          },
        },
      })
      .xDomain(xDomain)
      .yDomain(yDomain)
      .svgPlotArea(multi1)
      .canvasPlotArea(d3ElementLineSeries);

    d3.select("#chart").datum(updData).call(updChart);

    return setDomainData(yDomain);
  };

  const handleAudioTimerStop = () => {
    clearInterval(audioTimerRef.current);
  };

  const handleAudioTimerStart = () => {
    // Clear any timers already running
    handleAudioTimerStop();

    audioTimerRef.current = setInterval(() => {
      if (audioRef.current.ended) {
        setIsAudioPlaying(false);
        handleAudioTimerStop();
      }
      handleSetChartLineProgress(audioRef.current.currentTime);
      setAudioCurrentTime(audioRef.current.currentTime);
    }, [50]);
  };

  const handleAudioPlay = () => {
    setIsAudioPlaying(true);
    handleAudioTimerStart();
    audioRef.current.play();
  };

  const handleAudioPause = () => {
    handleAudioTimerStop();
    setIsAudioPlaying(false);
    audioRef.current.pause();
  };

  const handleAudioSliderScrub = (value) => {
    // Stop if timer already running
    if (isAudioPlaying) {
      handleAudioTimerStop();
      audioRef.current.pause();
    }
    handleSetChartLineProgress(value);
    setAudioCurrentTime(value);
    audioRef.current.currentTime = value;
  };

  const handleAudioSliderScrubEnd = () => {
    // If was playing before scrub will play
    if (isAudioPlaying) {
      handleAudioPlay();
    }
  };

  useEffect(() => {
    // rect radius
    if (!_.isEmpty(dataMainChart)) {
      redraw();
      brushedNavigationRange = zoomRange;
    }
    d3.select("#navigator-chart").datum(dataNavigation).call(navigatorChart);
    d3.selectAll(".handle")
      .attr("fill", SEGMENT_COLOR)
      .attr("width", 8)
      .attr("heigt", 34)
      .attr("y", 4)
      .attr("ry", 10);

    d3.select("#navigator-chart").selectAll(".overlay").attr("pointer-events", "none");
  }, [dataNavigation, dataMainChart]);

  const clearChart = () => {
    d3.selectAll("#chart").remove("*");
  };

  useEffect(() => {
    return () => clearChart();
  }, []);

  useEffect(() => {
    if (segmentData) {
      drawSegments();
      brushedNavigationRange = zoomRange;
    }
  }, [segmentData, zoomRangeDomain, domainData]);

  useEffect(() => {
    if (!_.isEmpty(newSegment)) {
      setActiveEditingSegment(-1);
      isNewSementCreating = true;
      if (!newSegment.start) {
        drawSegments(newSegment.id);
      } else if (newSegment.color) {
        d3.select(`#band_brash_${newSegment.id}`)
          .selectAll(".selection")
          .attr("fill", newSegment.color)
          .attr("fill-opacity", "0.5")
          .attr("stroke", newSegment.color)
          .attr("stroke-width", "2");
      }
    } else {
      isNewSementCreating = false;
      drawSegments();
    }
  }, [newSegment]);

  useEffect(() => {
    if (!_.isEmpty(editingSegment) && activeEditingSegment !== editingSegment.id) {
      setActiveEditingSegment(editingSegment.id);
      drawSegments(undefined, editingSegment.id, undefined);
    }
  }, [editingSegment]);

  useEffect(() => {
    // Pause and clean up after unmount component
    return () => {
      audioRef.current?.pause();
      handleAudioTimerStop();
    };
  }, []);

  useEffect(() => {
    if (audioFile) {
      audioRef.current = new Audio(audioFile);
      audioRef.current.addEventListener("loadedmetadata", () => {
        const { duration } = audioRef.current;
        setAudioDurationTime(duration);
      });
    }
  }, [audioFile]);

  return (
    <div className="base__container">
      <div id="chart" style={{ height: "500px" }} />
      <FormGroup row className={classes.legendWrapper}>
        {seriesNameList.map((sensor) => (
          <FormControlLabel
            key={sensor}
            control={
              <Checkbox
                style={{ display: "none" }}
                checked={!unselectedSeries.includes(sensor)}
                onChange={(event) => handleUnSelectSeries(event.target.checked, sensor)}
                name={sensor}
              />
            }
            label={
              <LabelColoredName
                className={unselectedSeries.includes(sensor) ? classes.unSelectedLegendValue : ""}
                name={sensor}
                color={colors(sensor)}
              />
            }
          />
        ))}
      </FormGroup>
      <div id="navigator-chart" style={{ height: "100px", marginRight: "48px" }} />
      {audioRef.current ? (
        <Stack sx={{ paddingLeft: "1rem", marginRight: "calc(48px + 1rem)" }}>
          <AudioSlider
            aria-label="audio-player-time-indicator"
            size="small"
            value={audioCurrentTime}
            min={0}
            max={audioDurationTime}
            step={0.1}
            onChange={(e) => handleAudioSliderScrub(e.target.value)}
            onChangeCommitted={handleAudioSliderScrubEnd}
          />
          <Box
            sx={{
              display: "grid",
              alignItems: "center",
              justifyContent: "space-between",
              gridTemplateColumns: "5rem auto 5rem",
              fontSize: "0.875rem",
            }}
          >
            <Box sx={{ marginTop: "-1rem", display: "flex", justifyContent: "flex-start" }}>
              {filterFormatSecondsToDuration(audioCurrentTime)}
            </Box>
            <Box>
              {isAudioPlaying ? (
                <IconButtonRounded color="primary" onClick={handleAudioPause}>
                  <PauseIcon />
                </IconButtonRounded>
              ) : (
                <IconButtonRounded color="primary" onClick={handleAudioPlay}>
                  <PlayArrowIcon />
                </IconButtonRounded>
              )}
            </Box>
            <Box sx={{ marginTop: "-1rem", display: "flex", justifyContent: "flex-end" }}>
              -{filterFormatSecondsToDuration(audioDurationTime - audioCurrentTime)}
            </Box>
          </Box>
        </Stack>
      ) : null}
    </div>
  );
};

LineChartSegments.propTypes = {
  onSementMove: PropTypes.func,
  segmentData: PropTypes.array.isRequired,
};

LineChartSegments.defaultProps = {
  onSementMove: () => {},
};

export default LineChartSegments;
