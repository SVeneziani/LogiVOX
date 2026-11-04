#!/usr/bin/env python3
"""Monitor PWR_FAIL (BCM24). HALT_DONE belongs exclusively to the kernel."""
import argparse
import logging
import os
import pwd
from pathlib import Path
import subprocess
import time


class PowerLoss:
    def __init__(self, delay=2.0):
        self.delay = delay
        self.since = None
        self.reported = False

    def update(self, failed, now):
        if not failed:
            self.since = None
            self.reported = False
            return False
        if self.since is None:
            self.since = now
        if not self.reported and now - self.since >= self.delay:
            self.reported = True
            return True
        return False


def request_poweroff():
    # Play as the application owner, sharing its runtime audio lock.
    root = Path(__file__).resolve().parents[1]
    owner = pwd.getpwuid(root.stat().st_uid)
    command = ['/usr/bin/env', 'XDG_RUNTIME_DIR=/run/user/' + str(owner.pw_uid),
               '/usr/bin/python3', str(root / 'bin' / 'logivox.py'), 'announce-shutdown']
    if os.geteuid() != owner.pw_uid:
        command = ['/usr/sbin/runuser', '-u', owner.pw_name, '--'] + command
    try:
        subprocess.run(command, check=True, timeout=6)
    except Exception:
        logging.exception('Annuncio non disponibile: proseguo con lo spegnimento')
    # Audio errors must never prevent a safe shutdown.
    subprocess.run(['/usr/bin/systemctl', 'poweroff'], check=True, timeout=15)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--poweroff', action='store_true', help='Enable real shutdown; default is monitor only')
    args = parser.parse_args()
    from gpiozero import DigitalInputDevice
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    # External pull-up in the UPS detector; no internal pull resistor.
    with DigitalInputDevice(24, pull_up=None, active_state=True) as signal:
        state = PowerLoss()
        previous = None
        logging.info('UPS mode: %s', 'POWER OFF ENABLED' if args.poweroff else 'MONITOR ONLY')
        while True:
            failed = signal.is_active
            if failed != previous:
                logging.info('PWR_FAIL=%s: USB %s', int(failed), 'absent' if failed else 'present')
                previous = failed
            if state.update(failed, time.monotonic()):
                if args.poweroff:
                    logging.warning('USB absent for 2 seconds: requesting orderly poweroff')
                    # Failure exits the process; systemd restarts it and retries.
                    request_poweroff()
                    # Do not submit repeated shutdown requests while services stop.
                    while True:
                        time.sleep(1)
                else:
                    logging.warning('TEST: would request orderly poweroff')
            time.sleep(0.05)


if __name__ == '__main__':
    main()
