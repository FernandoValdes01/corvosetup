import unittest

from hardware import HidDeviceInfo, g213_zone_packet, g733_zone_packet, parse_color


class PacketTests(unittest.TestCase):
    def test_hidapi_structure_matches_installed_abi(self):
        fields = [name for name, _type in HidDeviceInfo._fields_]
        self.assertLess(fields.index("next"), fields.index("bus_type"))

    def test_parse_color_scales_brightness(self):
        self.assertEqual(parse_color("#FF8040", 50), (128, 64, 32))

    def test_g213_packet_targets_zone(self):
        packet = g213_zone_packet(3, "#112233")
        self.assertEqual(packet[:10], bytes([0x11, 0xFF, 0x0C, 0x3A, 3, 1, 0x11, 0x22, 0x33, 2]))

    def test_g733_packet_targets_top_zone(self):
        packet = g733_zone_packet(1, "#204060", 50)
        self.assertEqual(packet[:10], bytes([0x11, 0xFF, 0x04, 0x3E, 1, 1, 0x10, 0x20, 0x30, 2]))


if __name__ == "__main__":
    unittest.main()
