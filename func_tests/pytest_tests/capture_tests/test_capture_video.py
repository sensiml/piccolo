import os
import os.path
import time

import numpy as np
import pandas as pd
import pytest
from requests.exceptions import Timeout, HTTPError, TooManyRedirects

CAPTURE_NAME = "test_capture.csv"
CAPTURE_VIDEO_NAME = "video_test.mp4"
TEST_KEYPOINTS = {
    "trim_sensor_start": 30000,
    "trim_sensor_end": 320000,
    "trim_video_start": 0,
    "trim_video_end": 1,
}


@pytest.fixture
def dsk_with_capture(dsk_random_project):
    dsk = dsk_random_project
    capture_path = os.path.join(os.path.dirname(__file__), f"data/{CAPTURE_NAME}")
    dsk.project.captures.get_or_create(
        CAPTURE_NAME, capture_path, asynchronous=True, capture_info=None
    )

    yield dsk


def test_capture_video_upload(dsk_with_capture):
    dsk = dsk_with_capture
    capture = dsk.project.captures.get_capture_by_filename(CAPTURE_NAME)

    capture_video = capture.capture_videos.new_capture_video(
        {
            "video": os.path.join(
                os.path.dirname(__file__), f"data/{CAPTURE_VIDEO_NAME}"
            ),
            "keypoints": TEST_KEYPOINTS,
        }
    )

    capture_video.insert()

    capture_video.refresh()

    assert capture_video.keypoints == TEST_KEYPOINTS

    capture_video.delete()

    try:
        capture_video.refresh()
    except HTTPError as e:
        assert e.response.status_code == 404
