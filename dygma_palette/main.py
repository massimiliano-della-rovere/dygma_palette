#!/bin/env python3

from sys import stderr

from dygma_palette.dygma.keyboard import DygmaKeyboard
from dygma_palette.dygma.utils import detect_dygma_keyboards, palette_backup_restore
from dygma_palette.image import acquire_image, list_acquisition_sources
from dygma_palette.frontend.desktop import run


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
            run(dygma_keyboards, image_generator)


if __name__ == "__main__":
    main()
