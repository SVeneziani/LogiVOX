import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'bin'))
from logivox_pedal import PedalEdge


class PedalTests(unittest.TestCase):
    def test_press_hold_release(self):
        p = PedalEdge()
        self.assertFalse(p.update(False, 0))
        self.assertFalse(p.update(False, .1))
        self.assertFalse(p.update(True, .2))
        self.assertTrue(p.update(True, .3))
        self.assertFalse(p.update(True, 10))
        p.update(False, 11)
        p.update(False, 11.1)
        p.update(True, 12)
        self.assertTrue(p.update(True, 12.1))

    def test_bounce(self):
        p = PedalEdge()
        p.update(False, 0)
        p.update(False, .1)
        for state, t in [(True, .2), (False, .21), (True, .22), (False, .23)]:
            self.assertFalse(p.update(state, t))
        p.update(True, .4)
        self.assertTrue(p.update(True, .5))

    def test_held_at_start(self):
        p = PedalEdge()
        self.assertFalse(p.update(True, 0))
        self.assertFalse(p.update(True, 1))
        p.update(False, 2)
        p.update(False, 2.1)
        p.update(True, 3)
        self.assertTrue(p.update(True, 3.1))
