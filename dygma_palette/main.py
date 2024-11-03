#!/bin/env python3

from sys import stderr

from dygma_palette.constants import PALETTE_SIZE
from dygma_palette.dygma.keyboard import DygmaKeyboard
from dygma_palette.dygma.utils import detect_dygma_keyboards, palette_backup_restore
from dygma_palette.image import (
    acquire_image, extract_centroids, list_acquisition_sources)
from dygma_palette.frontend.desktop import (
    close_window, close_all_windows, process_centroids, show_centroids,
    show_image, wait_for_key)


def main() -> None:
    acquisition_devices = filter(
        lambda acquisition_source: acquisition_source.is_reading,
        list_acquisition_sources())
    try:
        acquisition_device = next(acquisition_devices)
    except StopIteration:
        print("no acquisition devices found.", file=stderr)
        exit(1)

    dygma_keyboards = tuple(
        DygmaKeyboard(detected_keyboard)
        for detected_keyboard in detect_dygma_keyboards())
    if not dygma_keyboards:
        print("no Dygma keyboards found.", file=stderr)
        exit(2)

    with palette_backup_restore(dygma_keyboards):
        with acquire_image(acquisition_device) as image_generator:
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


if __name__ == "__main__":
    main()
