import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'bin'))
from logivox_auto import AutoReader, TalkButton

def m(value, t, function='VOLT', unit='V'):
    return dict(value=value, timestamp=1000+t, function=function, unit=unit)

class AutoTests(unittest.TestCase):
    def feed(self, a, value, start, count=7, **kwargs):
        return [a.update(m(value, start+i*.25, **kwargs), start+i*.25, 1000+start+i*.25)
                for i in range(count)]

    def test_initial_then_silent_and_significant_change(self):
        a=AutoReader()
        self.assertFalse(any(self.feed(a, 5, 0, 4)))
        self.assertTrue(a.update(m(5, 1), 1, 1001))
        a.spoken(m(5, 1), 1)
        self.assertFalse(any(self.feed(a, 5.002, 2)))
        self.assertTrue(any(self.feed(a, 5.1, 5)))

    def test_noise_and_ramp_do_not_settle(self):
        a=AutoReader()
        for i in range(100):
            t=i*.25
            self.assertFalse(a.update(m(5 + i*.02, t), t, 1000+t))

    def test_new_mode_and_open_once(self):
        a=AutoReader()
        a.spoken(m(1e9, 0), 0)
        self.assertFalse(any(self.feed(a, 1e9, 4)))
        self.assertTrue(any(self.feed(a, 5, 7)))
        a.spoken(m(5, 9), 9)
        self.assertTrue(any(self.feed(a, 5, 13, function='RES', unit='OHM')))

    def test_stale_and_repeated_samples_never_stable(self):
        a=AutoReader()
        for i in range(30):
            self.assertFalse(a.update(m(5, 0), i*.25, 1000+i*.25))
        self.assertFalse(a.update(m(float('nan'), 9), 9, 1009))
        self.assertTrue(any(self.feed(a, 5, 10)))

    def test_zero_noise_floor_and_polarity(self):
        a=AutoReader();a.spoken(m(0, 0), 0)
        self.assertFalse(any(self.feed(a, .0001, 4)))
        self.assertTrue(any(self.feed(a, -.01, 7)))

    def test_cooldown(self):
        a=AutoReader();a.spoken(m(5, 0), 0)
        self.assertFalse(any(self.feed(a, 6, .25)))
        self.assertTrue(any(self.feed(a, 6, 3)))

class TalkTests(unittest.TestCase):
    def arm(self, b):
        b.update(False,0);b.update(False,.1)
    def test_short_only_on_release(self):
        b=TalkButton();self.arm(b)
        b.update(True,.2);self.assertIsNone(b.update(True,.3))
        b.update(False,.5);self.assertEqual(b.update(False,.6),'talk')
    def test_long_once_and_no_short_on_release(self):
        b=TalkButton();self.arm(b);b.update(True,.2);b.update(True,.3)
        self.assertEqual(b.update(True,2.4),'toggle_auto')
        self.assertIsNone(b.update(True,9))
        b.update(False,10);self.assertIsNone(b.update(False,10.1))
    def test_held_at_boot_and_bounce(self):
        b=TalkButton();b.update(True,0);self.assertIsNone(b.update(True,5))
        self.arm(b)
        for p,t in [(True,.2),(False,.21),(True,.22),(False,.23),(False,.4)]:
            self.assertIsNone(b.update(p,t))
