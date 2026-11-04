import sys
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'bin'))
from logivox_ups import request_poweroff

class ShutdownAnnouncementTests(unittest.TestCase):
    @patch('logivox_ups.subprocess.run')
    def test_announcement_before_shutdown(self, run):
        request_poweroff()
        self.assertEqual(run.call_count, 2)
        self.assertIn('announce-shutdown', run.call_args_list[0].args[0])
        self.assertEqual(run.call_args_list[1].args[0], ['/usr/bin/systemctl', 'poweroff'])

    @patch('logivox_ups.subprocess.run')
    def test_audio_failure_still_shuts_down(self, run):
        run.side_effect = [subprocess.TimeoutExpired('audio', 6), None]
        with self.assertLogs(level='ERROR'):
            request_poweroff()
        self.assertEqual(run.call_args.args[0], ['/usr/bin/systemctl', 'poweroff'])

if __name__ == '__main__':
    unittest.main()
