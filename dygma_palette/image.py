from contextlib import contextmanager
from itertools import count
from math import sqrt
from typing import Callable, Generator

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


def calculate_perceived_brightness(bgr: MatLike) -> int:
    # http://alienryderflex.com/hsp.html
    return round(
        sqrt(.299 * bgr[2] ** 2
           + .587 * bgr[1] ** 2
           + .114 * bgr[0] ** 2))


def calculate_color_for_label(bgr: MatLike) -> tuple[int, int, int]:
    if calculate_perceived_brightness(bgr) > 127.0:
        return (0, 0, 0)
    else:
        return (255, 255, 255)
    

def show_palette(centers: MatLike,
                 caption: str = "Palette",
                 bar_width: int = 150,
                 bar_height: int = 150) -> None:
    bars = []
    rgb_values = []
    for bgr in centers:
        bar = np.zeros((bar_height, bar_width, 3), np.uint8)
        bar[:] = bgr
        rgb_values.append((int(bgr[2]), int(bgr[1]), int(bgr[0])))
        bars.append(bar)

    image = np.hstack(bars)
    for index, rgb in enumerate(rgb_values):
        image = cv2.putText(
            img=image,
            text=f"{index + 1}: #{rgb[0]:2X}{rgb[1]:2X}{rgb[2]:2X}",
            org=(5 + bar_width * index, bar_height - 10),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.5,
            color=calculate_color_for_label(rgb),
            thickness=1,
            lineType=cv2.LINE_AA,
            bottomLeftOrigin=False)
    cv2.imshow(caption, image)


def extract_palette(image: MatLike,
                    palette_size: int,
                    image_window_name: str = "",
                    palette_window_name: str = "",
                    color_key_function: Callable[[MatLike], int] | None = calculate_perceived_brightness) -> Palette:
    # https://www.alanzucconi.com/2015/05/24/how-to-find-the-main-colours-in-an-image/
    # https://www.youtube.com/watch?v=90s4SomOSa0

    if image_window_name:
       cv2.imshow(image_window_name, image) 

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

    if callable(color_key_function):
        np.apply_along_axis(color_key_function, axis=1, arr=centers).argsort()

    if palette_window_name:
        show_palette(centers, caption=palette_window_name)

    # opencv color components order is BGR not RGB
    return Palette(
        RGBW(r, g, b)
        for b, g, r in np.uint8(centers).tolist())  # pyright: ignore [reportGeneralTypeIssues]
