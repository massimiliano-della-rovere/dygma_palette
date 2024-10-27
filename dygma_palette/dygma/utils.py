from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, TYPE_CHECKING

from serial import Serial
from serial.tools.list_ports import comports as list_serial_ports

from dygma_palette.auxillary_types import DetectedKeyboard
from dygma_palette.constants import CHARSET, HARDWARE_IDENTIFIERS, BAUDRATE


if TYPE_CHECKING:
    from dygma_palette.dygma.keyboard import DygmaKeyboard


def detect_dygma_keyboards() -> Generator[DetectedKeyboard, None, None]:
    for serial_port in list_serial_ports():
        if serial_port.pid is None or serial_port.vid is None:
            continue
        
        for hardware_identifier in HARDWARE_IDENTIFIERS:
            usb_ids = hardware_identifier.usb
            for key, bootloader_mode_detected in (("keyboard", False),
                                                  ("bootloader", True)):
                usb_section = getattr(usb_ids, key)
                if (
                    usb_section.pid != serial_port.pid or
                    usb_section.vid != serial_port.vid
                ):
                    continue

                keyboard_params = DetectedKeyboard(
                    serial_port=serial_port,
                    hardware_identifier=hardware_identifier,
                    bootloader_mode_detected=bootloader_mode_detected)

                if hardware_identifier.product.startswith("Raise"):
                    # ugly solution to avoid circular import
                    from dygma_palette.dygma.keyboard import DygmaKeyboard
                    model = DygmaKeyboard(keyboard_params).keyboard_layout
                    if 1 != len({model, serial_port.product, hardware_identifier.product}):
                        continue

                yield keyboard_params


def neuron_io(device: str, request: str) -> Generator[str, None, None]:
    with Serial(port=device, baudrate=BAUDRATE) as connection:
        connection.write(f"{request}\n".encode(CHARSET))
        while "." != (received := connection.readline()
                                            .strip()
                                            .decode(CHARSET)):
            yield received


@contextmanager
def palette_backup_restore(dygma_keyboards: tuple[DygmaKeyboard, ...]) -> Generator[None, None, None]:
    original_palette = {
        dygma_keyboard.serial_number: dygma_keyboard.palette
        for dygma_keyboard in dygma_keyboards
    }
    print(original_palette)
    try:
        yield
    finally:
        for dygma_keyboard in dygma_keyboards:
            dygma_keyboard.palette = original_palette[dygma_keyboard.serial_number]

