#!/bin/env python3

from ast import literal_eval
from sys import stderr

from dygma_palette.auxillary_types import Palette, RGBW
from dygma_palette.dygma.keyboard import DygmaKeyboard
from dygma_palette.dygma.utils import detect_dygma_keyboards


def restore_palette_using_stdout_backup() -> None:
    text_backup = input(
        "paste here the first line of output by main.py, the one that looks "
        "like a dict with str keys and tuple of 16 RGBW instances as values: ")

    simplified_text = text_backup.replace("RGBW", "") \
                                 .replace("r=", "") \
                                 .replace("g=", "") \
                                 .replace("b=", "") \
                                 .replace("w=", "")
    backup = literal_eval(simplified_text)

    detected_keyboards = {
        (keyboard := DygmaKeyboard(configuration)).neuron_identifier: keyboard
        for configuration in detect_dygma_keyboards() 
    } 

    for neuron_identifier, palette in backup.items():
        try:
            keyboard = detected_keyboards[neuron_identifier]
        except KeyError:
            print(
                f"Keyboard with {neuron_identifier=} not found, skipping!",
                file=stderr)
        else:
            keyboard.palette = Palette(RGBW._make(color) for color in palette)
            print(f"Restored palette in keyboard with {neuron_identifier=}.")


if __name__ == "__main__":
    restore_palette_using_stdout_backup()
