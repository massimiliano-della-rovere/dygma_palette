from dygma_palette.auxillary_types import KeyboardInfo, KeyboardUsbIds, KeyboardUsbPidAndVid


CHARSET = "utf-8"
BAUDRATE = 115200
PALETTE_SIZE = 16  # 16 colors in the palette


HARDWARE_IDENTIFIERS = (
    # from https://github.com/Dygmalab/Bazecor/tree/development/src/api/hardware-dygma-*/index.ts
    KeyboardInfo(
        vendor="Dygma",
        product="Defy",
        model="wired",
        name="Dygma Defy wired",
        rgbw_mode=True,
        usb=KeyboardUsbIds(
            keyboard=KeyboardUsbPidAndVid(vid=0x35ef, pid=0x0010),
            bootloader=KeyboardUsbPidAndVid(vid=0x35ef, pid=0x0011),
        ),
    ),
    KeyboardInfo(
        vendor="Dygma",
        product="Defy",
        model="wireless",
        name="Dygma Defy wireless",
        rgbw_mode=True,
        usb=KeyboardUsbIds(
            keyboard=KeyboardUsbPidAndVid(vid=0x35ef, pid=0x0012),
            bootloader=KeyboardUsbPidAndVid(vid=0x35ef, pid=0x0013),
        ),
    ), 
    KeyboardInfo(
        vendor="Dygma",
        product="Raise",
        model="ANSI",
        name="Dygma Raise ANSI",
        rgbw_mode=False,
        usb=KeyboardUsbIds(
            keyboard=KeyboardUsbPidAndVid(vid=0x1209, pid=0x2201),
            bootloader=KeyboardUsbPidAndVid(vid=0x1209, pid=0x2200),
        ),
    ), 
    KeyboardInfo(
        vendor="Dygma",
        product="Raise",
        model="ISO",
        name="Dygma Raise ISO",
        rgbw_mode=False,
        usb=KeyboardUsbIds(
            keyboard=KeyboardUsbPidAndVid(vid=0x1209, pid=0x2201),
            bootloader=KeyboardUsbPidAndVid(vid=0x1209, pid=0x2200),
        ),
    ), 
    KeyboardInfo(
        vendor="Dygma",
        product="Raise2",
        model="ANSI",
        name="Dygma Raise 2 ANSI",
        rgbw_mode=False,
        usb=KeyboardUsbIds(
            keyboard=KeyboardUsbPidAndVid(vid=0x35ef, pid=0x0021),
            bootloader=KeyboardUsbPidAndVid(vid=0x35ef, pid=0x0020),
        ),
    ), 
    KeyboardInfo(
        vendor="Dygma",
        product="Raise2",
        model="ISO",
        name="Dygma Raise 2 ISO",
        rgbw_mode=False,
        usb=KeyboardUsbIds(
            keyboard=KeyboardUsbPidAndVid(vid=0x35ef, pid=0x0021),
            bootloader=KeyboardUsbPidAndVid(vid=0x35ef, pid=0x0022),
        ),
    ), 
)
