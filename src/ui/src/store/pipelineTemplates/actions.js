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

import guitarImg from "assets/images/guitar.jpg";
import kwSpottingImg from "assets/images/keyword_spotting.jpg";
import vibrationImg from "assets/images/vibration_classification.png";
import gestureImg from "assets/images/gesture_recognition.png";
import activityImg from "assets/images/activity_recognition.png";

import audioData from "./data/audioData.json";
import KWSpottingData from "./data/KWSpottingData.json";
import vibrationClassification from "./data/vibrationClassificationData.json";
import gestureClassification from "./data/gestureClassificationData.json";
import activityClassification from "./data/activityClassificationData.json";
import { SET_PIPELINE_TEMPLATES } from "./actionTypes";

export const loadPipelineTemplates = () => {
  return {
    type: SET_PIPELINE_TEMPLATES,
    payload: [
      { ...KWSpottingData, img: kwSpottingImg },
      { ...vibrationClassification, img: vibrationImg },
      { ...activityClassification, img: activityImg },
      { ...gestureClassification, img: gestureImg },
      { ...audioData, img: guitarImg },
    ],
  };
};
