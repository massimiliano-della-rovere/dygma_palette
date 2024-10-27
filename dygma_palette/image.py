from contextlib import contextmanager
from itertools import count
from typing import Generator

import cv2
import numpy as np
from cv2.typing import MatLike


from dygma_palette.auxillary_types import AcquisitionSource, FrameGenerator, Palette, RGBW


def list_acquisition_sources() -> Generator[AcquisitionSource, None, None]:
    for source_id in count(0):
        try:
            source = cv2.VideoCapture(source_id)
            if not source.isOpened():
                break
        except Exception:
            break

        is_reading, _ = source.read()
        width = source.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = source.get(cv2.CAP_PROP_FRAME_HEIGHT)
        source.release()

        yield AcquisitionSource(
            source_id=source_id,
            is_reading=is_reading,
            width=int(width),
            height=int(height))


def get_frame(acquisition_source: cv2.VideoCapture) -> FrameGenerator:
    while True:
        ret, frame = acquisition_source.read()
        if not ret:
            continue

        try:
            yield frame
        except StopIteration:
            break


@contextmanager
def acquire_image(acquistion_source: AcquisitionSource,
                  requested_width: int | None=None,
                  requested_height: int | None=None) -> Generator[FrameGenerator, None, None]:
    
    active_source = cv2.VideoCapture(acquistion_source.source_id)
    if not active_source.isOpened():
        raise RuntimeError(f"{acquistion_source} doesn't work")

    if requested_width is not None and requested_width < acquistion_source.width:
        active_source.set(cv2.CAP_PROP_FRAME_WIDTH, float(requested_width))
    if requested_height is not None and requested_height < acquistion_source.height:
        active_source.set(cv2.CAP_PROP_FRAME_HEIGHT, float(requested_height))

    frame_grabber = get_frame(active_source)
    try:
        yield frame_grabber
    finally:
        frame_grabber.send(StopIteration())
        active_source.release()


def extract_palette(image: MatLike, palette_size: int) -> Palette:
    # https://www.alanzucconi.com/2015/05/24/how-to-find-the-main-colours-in-an-image/
    # https://www.youtube.com/watch?v=90s4SomOSa0

    height, width, color_depth = image.shape

    data = np.reshape(image, (height * width, color_depth))
    data = np.float32(data)

    number_of_clusters = palette_size
    termination_criteria = \
        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    flags = cv2.KMEANS_RANDOM_CENTERS
    attempts = 10
    _, _, centers = cv2.kmeans(
        data=data,  # pyright: ignore [reportArgumentType, reportCallIssue]
        K=number_of_clusters,
        bestLabels=None,  # pyright: ignore [reportArgumentType, reportCallIssue]
        criteria=termination_criteria,
        attempts=attempts,
        flags=flags)  # pyright: ignore [reportArgumentType, reportCallIssue]

    # opencv color components order is BGR not RGB
    return Palette(
        RGBW(r, g, b)
        for b, g, r in np.uint8(centers).tolist())  # pyright: ignore [reportGeneralTypeIssues]

