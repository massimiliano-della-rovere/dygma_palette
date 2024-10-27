from __future__ import annotations

from abc import ABCMeta, abstractmethod
from itertools import chain, islice
from re import compile as re_compile
from typing import TYPE_CHECKING

from dygma_palette.auxillary_types import Palette, RGBW, VersionType 
from dygma_palette.constants import PALETTE_SIZE
from dygma_palette.dygma.utils import neuron_io, rgb2rgbw


if TYPE_CHECKING:
    from dygma_palette.dygma.keyboard import DygmaKeyboard


version_parser = re_compile(r"^\D*(\d+)\.(\d+)\.(\d+)\W*(.*)$").search


class DygmaRaiseBaseDescriptor(metaclass=ABCMeta):
    def __set_name__(self, owner: DygmaKeyboard, name: str) -> None:
        self.name = name

    def _neuron_io(self, device: str, request: str) -> tuple[str, ...]:
        return tuple(neuron_io(device, request))

    @property
    @abstractmethod
    def command(self) -> str:
        raise NotImplementedError


class FirmwareVersionDescriptor(DygmaRaiseBaseDescriptor):
    @property
    def command(self) -> str:
        return "version"

    def __get__(self, dygma_keyboard: DygmaKeyboard, objtype=None) -> VersionType:
        request = self.command
        reply = self._neuron_io(dygma_keyboard.device, request)
        return VersionType._make(
            int(value) if index != 3 else value
            for index, value in enumerate(version_parser(reply[0]).groups())) # pyright: ignore [reportOptionalMemberAccess]


class HardwareIdentifierDescriptor(DygmaRaiseBaseDescriptor):
    @property
    def command(self) -> str:
        return "hardware.identifier"

    def __get__(self, dygma_keyboard: DygmaKeyboard, objtype=None) -> str:
        request = self.command
        reply = self._neuron_io(dygma_keyboard.device, request)
        return reply[0]


class HardwareVersionDescriptor(DygmaRaiseBaseDescriptor):
    @property
    def command(self) -> str:
        return "hardware.version"

    def __get__(self, dygma_keyboard: DygmaKeyboard, objtype=None) -> str:
        request = self.command
        reply = self._neuron_io(dygma_keyboard.device, request)
        return reply[0]


class KeyboardLayoutDescriptor(DygmaRaiseBaseDescriptor):
    @property
    def command(self) -> str:
        return "hardware.layout"

    def __get__(self, dygma_keyboard: DygmaKeyboard, objtype=None) -> str:
        request = self.command
        reply = self._neuron_io(dygma_keyboard.device, request)
        return reply[0]


class PaletteDescriptor(DygmaRaiseBaseDescriptor):
    @property
    def command(self) -> str:
        return "palette"

    def __get__(self, dygma_keyboard: DygmaKeyboard, objtype=None) -> Palette:
        request = self.command
        reply = self._neuron_io(dygma_keyboard.device, request)
        color_components = iter(int(x) for x in reply[0].split(" "))
        return Palette( 
            RGBW._make(
                islice(
                    color_components,
                    dygma_keyboard.color_components_size))
            for _ in range(PALETTE_SIZE))
     
    def __set__(self, dygma_keyboard: DygmaKeyboard, palette: Palette) -> None:
        if len(palette) != PALETTE_SIZE:
            raise ValueError(f"len(palette) != {PALETTE_SIZE}")

        if dygma_keyboard.rgbw_mode:
            palette = Palette(rgb2rgbw(color) for color in palette)
            print(f"new RGBW {palette=}")

        color_components = " ".join(
            str(n)
            for n in chain.from_iterable(
                color[:dygma_keyboard.color_components_size]
                for color in palette))
        request = f"palette {color_components}"
        self._neuron_io(dygma_keyboard.device, request)

        
class SettingsVersionDescriptor(DygmaRaiseBaseDescriptor):
    @property
    def command(self) -> str:
        return "settings.version"

    def __get__(self, dygma_keyboard: DygmaKeyboard, objtype=None) -> int:
        request = self.command
        reply = self._neuron_io(dygma_keyboard.device, request)
        return int(reply[0])

