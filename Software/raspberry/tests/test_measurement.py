import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'bin'))
from logivox_pedal import measurement_parts


class MeasurementTests(unittest.TestCase):
    def test_base_volts(self):
        self.assertEqual(measurement_parts(dict(function='VOLT', value=4.9)),
                         [4, 'POINT', 90, 'VOLTS'])

    def test_rounding_next_scale(self):
        self.assertEqual(measurement_parts(dict(function='VOLT', value=.999999)), [1, 'VOLTS'])

    def test_negative(self):
        self.assertEqual(measurement_parts(dict(function='VOLT', value=-4.9)),
                         ['MINUS', 4, 'POINT', 90, 'VOLTS'])

    def test_zero(self):
        self.assertEqual(measurement_parts(dict(function='VOLT', value=0)), [0, 'VOLTS'])

    def test_available_fragments(self):
        audio = Path(__file__).resolve().parents[2] / 'audio_it'
        if not (audio / '0.wav').exists():
            self.skipTest('Optional voice pack not distributed; install licensed WAV files first')
        for value in [4.9, 12, 999.999, .999999, 999999.9, .00041302, 1e-12, 0, -4.9]:
            for part in measurement_parts(dict(function='VOLT', value=value)):
                self.assertTrue((audio / f'{part}.wav').exists(), (value, part))

    def test_invalid(self):
        with self.assertRaises(ValueError):
            measurement_parts(dict(function='VOLT', value=float('nan')))


if __name__ == '__main__':
    unittest.main()
