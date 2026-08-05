"""HID protocol adapters for the Logitech G213 and G733."""

from __future__ import annotations

import ctypes
import ctypes.util
from dataclasses import dataclass

LOGITECH_VENDOR_ID = 0x046D
G213_PRODUCT_ID = 0xC336
G733_PRODUCT_ID = 0x0AB5


class HardwareError(RuntimeError):
    pass


class HidDeviceInfo(ctypes.Structure):
    pass


HidDeviceInfoPointer = ctypes.POINTER(HidDeviceInfo)
HidDeviceInfo._fields_ = [
    ("path", ctypes.c_char_p),
    ("vendor_id", ctypes.c_ushort),
    ("product_id", ctypes.c_ushort),
    ("serial_number", ctypes.c_wchar_p),
    ("release_number", ctypes.c_ushort),
    ("manufacturer_string", ctypes.c_wchar_p),
    ("product_string", ctypes.c_wchar_p),
    ("usage_page", ctypes.c_ushort),
    ("usage", ctypes.c_ushort),
    ("interface_number", ctypes.c_int),
    ("next", HidDeviceInfoPointer),
    ("bus_type", ctypes.c_int),
]


@dataclass(frozen=True)
class DeviceStatus:
    connected: bool
    accessible: bool
    detail: str = ""


class HidApi:
    def __init__(self) -> None:
        library = ctypes.util.find_library("hidapi-hidraw") or "libhidapi-hidraw.so.0"
        try:
            self.lib = ctypes.CDLL(library)
        except OSError as error:
            raise HardwareError("No se encontro libhidapi-hidraw") from error

        self.lib.hid_init.restype = ctypes.c_int
        self.lib.hid_enumerate.argtypes = [ctypes.c_ushort, ctypes.c_ushort]
        self.lib.hid_enumerate.restype = HidDeviceInfoPointer
        self.lib.hid_free_enumeration.argtypes = [HidDeviceInfoPointer]
        self.lib.hid_open_path.argtypes = [ctypes.c_char_p]
        self.lib.hid_open_path.restype = ctypes.c_void_p
        self.lib.hid_close.argtypes = [ctypes.c_void_p]
        self.lib.hid_write.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_size_t]
        self.lib.hid_write.restype = ctypes.c_int
        self.lib.hid_read_timeout.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_size_t, ctypes.c_int]
        self.lib.hid_read_timeout.restype = ctypes.c_int
        self.lib.hid_error.argtypes = [ctypes.c_void_p]
        self.lib.hid_error.restype = ctypes.c_wchar_p

        if self.lib.hid_init() != 0:
            raise HardwareError("No se pudo iniciar HIDAPI")

    def paths(self, product_id: int, interface_number: int) -> list[bytes]:
        result: list[bytes] = []
        devices = self.lib.hid_enumerate(LOGITECH_VENDOR_ID, product_id)
        current = devices
        try:
            while current:
                info = current.contents
                if info.interface_number == interface_number and info.path:
                    result.append(info.path)
                current = info.next
        finally:
            if devices:
                self.lib.hid_free_enumeration(devices)
        return list(dict.fromkeys(result))

    def status(self, product_id: int, interface_number: int) -> DeviceStatus:
        paths = self.paths(product_id, interface_number)
        if not paths:
            return DeviceStatus(False, False, "No conectado")
        handle = self.lib.hid_open_path(paths[0])
        if not handle:
            return DeviceStatus(True, False, "Sin permisos HID")
        self.lib.hid_close(handle)
        return DeviceStatus(True, True, "Disponible")

    def exchange(self, product_id: int, interface_number: int, packet: bytes) -> None:
        paths = self.paths(product_id, interface_number)
        if not paths:
            raise HardwareError("El dispositivo no esta conectado")
        handle = self.lib.hid_open_path(paths[0])
        if not handle:
            raise HardwareError("No hay permisos para acceder al dispositivo HID")
        try:
            output = (ctypes.c_ubyte * len(packet)).from_buffer_copy(packet)
            written = self.lib.hid_write(handle, output, len(packet))
            if written < 0:
                detail = self.lib.hid_error(handle) or "error desconocido"
                raise HardwareError(f"Error escribiendo al dispositivo: {detail}")
            response = (ctypes.c_ubyte * 64)()
            self.lib.hid_read_timeout(handle, response, len(response), 120)
        finally:
            self.lib.hid_close(handle)


def parse_color(color: str, brightness: int = 100) -> tuple[int, int, int]:
    value = color.removeprefix("#")
    if len(value) != 6:
        raise ValueError(f"Color no valido: {color}")
    scale = max(0, min(100, brightness)) / 100
    return tuple(round(int(value[index:index + 2], 16) * scale) for index in (0, 2, 4))


def g213_zone_packet(zone: int, color: str, enabled: bool = True) -> bytes:
    red, green, blue = parse_color(color if enabled else "#000000")
    packet = bytearray(20)
    packet[:10] = bytes([0x11, 0xFF, 0x0C, 0x3A, zone, 0x01, red, green, blue, 0x02])
    return bytes(packet)


def g733_zone_packet(zone: int, color: str, brightness: int, enabled: bool = True) -> bytes:
    red, green, blue = parse_color(color if enabled else "#000000", brightness)
    state = 1 if enabled and (red or green or blue) else 0
    packet = bytearray(20)
    packet[:10] = bytes([0x11, 0xFF, 0x04, 0x3E, zone, state, red, green, blue, 0x02])
    return bytes(packet)


class LogitechLights:
    G213_INTERFACE = 1
    G733_INTERFACE = 3

    def __init__(self) -> None:
        self.hid = HidApi()

    def statuses(self) -> dict[str, DeviceStatus]:
        return {
            "keyboard": self.hid.status(G213_PRODUCT_ID, self.G213_INTERFACE),
            "headset": self.hid.status(G733_PRODUCT_ID, self.G733_INTERFACE),
        }

    def apply_keyboard(self, config: dict) -> None:
        colors = config.get("zones", ["#00AEEF"] * 5)
        enabled = bool(config.get("enabled", True))
        for zone, color in enumerate(colors[:5], start=1):
            self.hid.exchange(G213_PRODUCT_ID, self.G213_INTERFACE, g213_zone_packet(zone, color, enabled))

    def apply_headset(self, config: dict) -> None:
        enabled = bool(config.get("enabled", True))
        brightness = int(config.get("brightness", 100))
        colors = [config.get("bottom", "#00AEEF"), config.get("top", "#00AEEF")]
        for zone, color in enumerate(colors):
            self.hid.exchange(G733_PRODUCT_ID, self.G733_INTERFACE, g733_zone_packet(zone, color, brightness, enabled))
