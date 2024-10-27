from __future__ import annotations

from typing import TYPE_CHECKING
from serial.tools.list_ports import comports as list_serial_ports

from dygma_palette.dygma.descriptors import (
    FirmwareVersionDescriptor, HardwareIdentifierDescriptor,
    HardwareVersionDescriptor,
    KeyboardLayoutDescriptor, PaletteDescriptor, SettingsVersionDescriptor)

if TYPE_CHECKING:
    from dygma_palette.dygma.utils import DetectedKeyboard


class DygmaKeyboard:
    def __init__(self, keyboard: DetectedKeyboard):
        self.keyboard = keyboard

    @property
    def device(self) -> str:
        return self.keyboard.serial_port.device

    @property
    def serial_number(self) -> str:
        return self.keyboard.serial_port.serial_number  # pyright: ignore [reportReturnType]

    @property
    def color_components_size(self) -> int:
        return 4 if self.keyboard.hardware_identifier.rgbw_mode else 3

    @property
    def rgbw_mode(self) -> bool:
        return self.keyboard.hardware_identifier.rgbw_mode 

    firmware_version = FirmwareVersionDescriptor()
    hardware_identifier = HardwareIdentifierDescriptor()
    hardware_version = HardwareVersionDescriptor()
    keyboard_layout = KeyboardLayoutDescriptor()
    palette = PaletteDescriptor()
    settings_version = SettingsVersionDescriptor()

