from typing import Annotated, Generator, NamedTuple

from cv2.typing import MatLike
from serial.tools.list_ports_linux import SysFS


class AcquisitionSource(NamedTuple):
    source_id: int
    is_reading: bool
    width: int
    height: int


FrameGenerator = Generator[MatLike, StopIteration, None]


class KeyboardUsbPidAndVid(NamedTuple):
    pid: int
    vid: int


class KeyboardUsbIds(NamedTuple):
    keyboard: KeyboardUsbPidAndVid
    bootloader: KeyboardUsbPidAndVid


class KeyboardInfo(NamedTuple):
    vendor: str
    product: str
    model: str
    name: str
    rgbw_mode: bool
    usb: KeyboardUsbIds


class DetectedKeyboard(NamedTuple):
    serial_port: SysFS
    hardware_identifier: KeyboardInfo
    bootloader_mode_detected: bool


class ValueRange(NamedTuple):
    min: int
    max: int


class RGBW(NamedTuple):
    r: Annotated[int, ValueRange(0, 255)]
    g: Annotated[int, ValueRange(0, 255)]
    b: Annotated[int, ValueRange(0, 255)]
    w: Annotated[int, ValueRange(0, 255)] = 0

    def __str__(self) -> str:
        if self.w is None:
            return f"#{self.r:02X}{self.g:02X}{self.b:02X}"
        else:
            return f"#{self.r:02X}{self.g:02X}{self.b:02X}{self.w:02X}"


Palette = tuple[RGBW, RGBW, RGBW, RGBW, RGBW, RGBW, RGBW, RGBW,
                RGBW, RGBW, RGBW, RGBW, RGBW, RGBW, RGBW, RGBW]


class VersionType(NamedTuple):
    major: int
    middle: int
    minor: int
    info: str

