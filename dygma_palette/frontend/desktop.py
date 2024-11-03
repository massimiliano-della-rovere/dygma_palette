from contextlib import contextmanager
from math import sqrt
from typing import Callable

import cv2
import numpy as np
from cv2.typing import MatLike


from dygma_palette.auxillary_types import Palette, RGBW


def wait_for_key(timeout: int) -> int:
    return cv2.waitKey(timeout)


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


def show_image(image: MatLike, window_name: str = "Image") -> None:
   cv2.imshow(window_name, image) 


def show_centroids(centroids: MatLike,
                   window_name: str = "Palette",
                   bar_width: int = 150,
                   bar_height: int = 150) -> None:
    bars = []
    rgb_values = []
    for bgr in centroids:
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
    cv2.imshow(window_name, image)


def close_window(window_name: str) -> None:
    cv2.destroyWindow(window_name)


def close_all_windows():
    cv2.destroyAllWindows()
    

def process_centroids(centroids: MatLike,
                      window_name: str = "",
                      color_key_function: Callable[[MatLike], int] | None = calculate_perceived_brightness) -> Palette:

    if callable(color_key_function):
        np.apply_along_axis(color_key_function, axis=1, arr=centroids).argsort()

    if window_name:
        show_palette(centroids, window_name=window_name)

    # opencv color components order is BGR not RGB
    return Palette(
        RGBW(r, g, b)
        for b, g, r in np.uint8(centroids).tolist())  # pyright: ignore [reportGeneralTypeIssues]

