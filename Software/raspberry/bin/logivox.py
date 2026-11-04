#!/usr/bin/python3
"""LogiVOX status and WAV playback. GPIO numbers use BCM numbering."""
import argparse
import array
import fcntl
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import threading
import time
import urllib.request
import wave

ROOT = Path(__file__).resolve().parents[1]
STOP = threading.Event()

def healthy():
    try:
        state = subprocess.check_output(
            ['nmcli', '-g', 'GENERAL.STATE', 'device', 'show', 'wlan0'],
            timeout=3, text=True)
        if not state.strip().startswith('100'):
            return False
        with urllib.request.urlopen('http://127.0.0.1:8080/api/identify', timeout=4) as r:
            identity = json.load(r).get('identity', '').upper().split(',')
        return len(identity) >= 2 and identity[0] == 'OWON' and identity[1] == 'XDM1041'
    except Exception:
        return False

def ready():
    from gpiozero import LED
    with LED(27, initial_value=False) as led:
        successes = 0
        previous = None
        announced = False
        while not STOP.is_set():
            successes = min(3, successes + 1) if healthy() else 0
            active = successes == 3
            led.value = active
            if active != previous:
                print('READY=' + str(active), flush=True)
                previous = active
            if active and not announced:
                announced = announce('reset')
            STOP.wait(2)

def announce(name):
    """Bounded status audio; shares the pedal lock without claiming its LED."""
    path = ROOT / 'audio' / 'audio_it' / (name + '.wav')
    lockpath = Path(os.environ.get('XDG_RUNTIME_DIR', '/tmp')) / 'logivox-voice.lock'
    try:
        with lockpath.open('a') as lock:
            deadline = time.monotonic() + 2
            while True:
                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if STOP.is_set() or time.monotonic() >= deadline:
                        return False
                    time.sleep(0.05)
            subprocess.run(['aplay', '-q', '--buffer-time=80000', '-D',
                            'plughw:CARD=MAX98357A,DEV=0', str(path)],
                           check=True, timeout=3)
        print('ANNOUNCEMENT=' + name, flush=True)
        return True
    except Exception as exc:
        print('Annuncio non riprodotto: ' + str(exc), flush=True)
        return False

def envelope(data, width):
    if width == 1:
        samples = [x - 128 for x in data]
        scale = 128.0
    else:
        samples = array.array('h', data)
        scale = 32768.0
    if not samples:
        return 0.0
    rms = math.sqrt(sum(x*x for x in samples) / len(samples)) / scale
    return 0.0 if rms < 0.003 else min(1.0, math.sqrt(rms / 0.16))

def play(path):
    from gpiozero import PWMLED
    with wave.open(str(path), 'rb') as wav:
        if wav.getsampwidth() not in (1, 2) or wav.getcomptype() != 'NONE':
            raise ValueError('Usare un WAV PCM a 8 o 16 bit, mono o stereo.')
        width = wav.getsampwidth()
        step = max(1, round(wav.getframerate() * 0.02))
        levels = []
        while data := wav.readframes(step):
            levels.append(envelope(data, width))
        interval = step / wav.getframerate()
    lockpath = Path(os.environ.get('XDG_RUNTIME_DIR', '/tmp')) / 'logivox-voice.lock'
    with lockpath.open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with PWMLED(23, frequency=100, initial_value=0) as led:
            proc = subprocess.Popen(['aplay', '-q', '--buffer-time=80000',
                '-D', 'plughw:CARD=MAX98357A,DEV=0', str(path)])
            try:
                start = time.monotonic() + 0.08
                for i, level in enumerate(levels):
                    if STOP.wait(max(0, start + i*interval - time.monotonic())):
                        break
                    if proc.poll() is not None:
                        break
                    led.value = level
                while proc.poll() is None and not STOP.wait(0.05):
                    pass
                if proc.poll() is not None and proc.returncode:
                    raise RuntimeError('Riproduzione fallita: ' + str(proc.returncode))
            finally:
                led.off()
                if proc.poll() is None:
                    proc.terminate()
                    try:
                        proc.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['ready', 'play', 'check', 'announce-ready', 'announce-shutdown'])
    parser.add_argument('file', nargs='?', type=Path, default=ROOT/'audio'/'alice.wav')
    args = parser.parse_args()
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: STOP.set())
    if args.command == 'ready':
        ready()
    elif args.command.startswith('announce-'):
        raise SystemExit(0 if announce('reset' if args.command == 'announce-ready' else 'shutdown') else 1)
    elif args.command == 'check':
        ok = healthy()
        print('Wi-Fi e OWON operativi' if ok else 'Wi-Fi o OWON non disponibile')
        raise SystemExit(0 if ok else 1)
    else:
        play(args.file.resolve())

if __name__ == '__main__':
    main()
