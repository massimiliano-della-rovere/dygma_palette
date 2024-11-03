from typing import Callable

import cv2
import numpy as np
from cv2.typing import MatLike


from dygma_palette.auxillary_types import FrameGenerator, Palette
from dygma_palette.constants import PALETTE_SIZE
from dygma_palette.dygma.keyboard import DygmaKeyboard
from dygma_palette.image import (
    calculate_color_for_label, calculate_perceived_brightness,
    centroids_to_palette, extract_centroids)


def wait_for_key(timeout: int) -> int:
    return cv2.waitKey(timeout)


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
        show_centroids(centroids, window_name=window_name)

    # opencv color components order is BGR not RGB
    return centroids_to_palette(centroids)

def run(dygma_keyboards: tuple[DygmaKeyboard, ...],
        image_generator: FrameGenerator) -> None:
    try:
        for image_number, image in enumerate(image_generator):
            image_window_name = f"Image {image_number}"
            palette_window_name = f"Palette {image_number}"
            centroids = extract_centroids(
                image=image,
                palette_size=PALETTE_SIZE)
            show_image(image, window_name=image_window_name)
            show_centroids(centroids, window_name=palette_window_name)

            palette = process_centroids(centroids)
            print(f"new {palette=}")
            for dygma_keyboard in dygma_keyboards:
                dygma_keyboard.palette = palette

            key = wait_for_key(timeout=0)
            close_window(image_window_name)
            close_window(palette_window_name)
            if (key & 0xFF) == ord("q"):
                break
    except KeyboardInterrupt:
        print("restoring default palette")
    finally:
        close_all_windows()

