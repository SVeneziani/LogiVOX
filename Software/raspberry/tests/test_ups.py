import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'bin'))
from logivox_ups import PowerLoss


class PowerLossTests(unittest.TestCase):
    def test_normal_usb(self):
        state = PowerLoss()
        self.assertFalse(state.update(False, 0))
        self.assertFalse(state.update(False, 10))

    def test_loss_once(self):
        state = PowerLoss()
        self.assertFalse(state.update(True, 0))
        self.assertFalse(state.update(True, 1.99))
        self.assertTrue(state.update(True, 2))
        self.assertFalse(state.update(True, 10))

    def test_glitch_and_return(self):
        state = PowerLoss()
        state.update(True, 0)
        self.assertFalse(state.update(False, 1))
        self.assertFalse(state.update(True, 2))
        self.assertFalse(state.update(True, 3))
        self.assertTrue(state.update(True, 4))

    def test_battery_boot(self):
        state = PowerLoss()
        self.assertFalse(state.update(True, 100))
        self.assertTrue(state.update(True, 102))

    def test_rearm_monitor(self):
        state = PowerLoss()
        state.update(True, 0)
        self.assertTrue(state.update(True, 2))
        state.update(False, 3)
        state.update(True, 4)
        self.assertTrue(state.update(True, 6))


if __name__ == '__main__':
    unittest.main()
