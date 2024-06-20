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
import ImageUploading from "react-images-uploading";
import { Button, Tooltip } from "@mui/material";
import PermMediaIcon from "@mui/icons-material/PermMedia";
import useStyles from "./ProjectDescriptionStyles";

const ProjectImageSelector = ({ setProjectImage }) => {
  const classes = useStyles();
  const [images, setImages] = React.useState([]);
  const onChange = (imageList) => {
    // data for submit
    setImages(imageList);
    if (imageList && imageList.length > 0) {
      setProjectImage(imageList[0]);
    }
  };

  return (
    <ImageUploading value={images} onChange={onChange} dataURLKey="data_url">
      {({ imageList, onImageUpload }) => (
        <span>
          <div className={classes.imageSelectorWrapper}>
            <span>
              <Tooltip title="Select Image">
                <Button
                  onClick={onImageUpload}
                  startIcon={<PermMediaIcon />}
                  color="primary"
                  variant="contained"
                >
                  Select Image
                </Button>
              </Tooltip>
            </span>
          </div>
          <div className={classes.imageSelectionWrapper}>
            {imageList.map((image, index) => (
              <div key={index} className="image-item">
                <img src={image.data_url} alt="" className={classes.SelectedImageStyle} />
              </div>
            ))}
          </div>
        </span>
      )}
    </ImageUploading>
  );
};
export default ProjectImageSelector;
