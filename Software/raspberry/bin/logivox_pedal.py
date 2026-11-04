#!/usr/bin/env python3
"""LogiVOX foot pedal: read OWON measurement and speak it from WAV fragments."""
import json, os, struct, tempfile, urllib.request, wave
import logging, math, time
import signal, threading
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from logivox import play, STOP
from logivox_auto import AutoReader, TalkButton

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / 'audio' / 'audio_it'
API = 'http://127.0.0.1:8080/api/measurement'

UNITS = {'RES':'OHMS', 'VOLT':'VOLTS', 'CURR':'AMPERES', 'CAP':'FARADS',
         'FREQ':'HERTZ', 'FRE':'HERTZ', 'TEMP':'DEGREES', 'TEM':'DEGREES',
         'DIO':'VOLTS', 'CONT':'OHMS', 'CON':'OHMS'}

def number_parts(n):
    if n == 0: return [0]
    if n < 0: return ['MINUS'] + number_parts(-n)
    out = []
    if n >= 100:
        h = (n // 100) * 100
        out.append(h); n %= 100
    if n: out.append(n)
    return out

def measurement_parts(m):
    fn = str(m.get('function', '')).upper()
    value = float(m['value'])
    if value >= 1e9:
        return ['OPEN' if fn in ('CONT', 'CON') else 'OUT_OF_RANGE']
    unit = UNITS.get(fn, str(m.get('unit', '')).upper())
    if not math.isfinite(value):
        raise ValueError('Misura non finita')
    scales = [(1e6, 'MEGA'), (1e3, 'KILO'), (1, None),
              (1e-3, 'MILLI'), (1e-6, 'MICRO'), (1e-9, 'NANO'), (1e-12, 'PICO')]
    index = next((i for i, (scale, _) in enumerate(scales)
                  if abs(value) >= scale), len(scales) - 1) if value else 2
    def rounded(i):
        return (Decimal(str(value)) / Decimal(str(scales[i][0]))).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP)
    scaled = rounded(index)
    if abs(scaled) >= 1000 and index > 0:
        index -= 1
        scaled = rounded(index)
    prefix = scales[index][1]
    whole = int(abs(scaled))
    if whole >= 1000:
        return ['OUT_OF_RANGE']
    cents = int((abs(scaled) - whole) * 100)
    parts = (['MINUS'] if scaled < 0 else []) + number_parts(whole)
    if cents:
        parts += ['POINT'] + ([0] if cents < 10 else []) + number_parts(cents)
    if prefix: parts.append(prefix)
    parts.append(unit)
    return parts

def build_wav(parts):
    files = [AUDIO / f'{p}.wav' for p in parts]
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        out = Path(f.name)
    with wave.open(str(out), 'wb') as dst:
        # Normalize every fragment to signed PCM16 for aplay.
        dst.setparams((1, 2, 16000, 0, 'NONE', 'not compressed'))
        for path in files:
            with wave.open(str(path), 'rb') as src:
                data = src.readframes(src.getnframes())
                if src.getsampwidth() == 1:
                    data = b''.join(struct.pack('<h', (b - 128) << 8) for b in data)
                dst.writeframes(data)
    return out

def read_measurement():
    with urllib.request.urlopen(API, timeout=4) as response:
        return json.load(response)

class PedalEdge:
    """One press after a stable release; ignores contact bounce and held pedal."""
    def __init__(self, delay=0.05):
        self.delay = delay
        self.candidate = None
        self.since = 0
        self.stable = None
        self.armed = False

    def update(self, pressed, now):
        if pressed != self.candidate:
            self.candidate = pressed
            self.since = now
        if now - self.since < self.delay or pressed == self.stable:
            return False
        self.stable = pressed
        if not pressed:
            self.armed = True
            return False
        fire = self.armed
        self.armed = False
        return fire


def speak_parts(parts):
    path = build_wav(parts)
    try:
        play(path)
    finally:
        path.unlink(missing_ok=True)


def main():
    from gpiozero import DigitalInputDevice
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: STOP.set())
    lock = threading.Lock()
    control = {'auto': False, 'version': 0}
    manual = threading.Event()

    def audio_worker():
        policy = AutoReader()
        version = 0
        next_poll = 0.
        error_logged_at = -math.inf
        while not STOP.is_set():
            with lock:
                enabled, current = control['auto'], control['version']
            if current != version:
                version = current
                policy = AutoReader()
                try:
                    speak_parts(['auto_on' if enabled else 'auto_off'])
                except Exception:
                    logging.exception('Annuncio AUTO non riuscito')
                next_poll = 0.
                continue
            requested = manual.is_set()
            if requested:
                manual.clear()
            if not requested and (not enabled or time.monotonic() < next_poll):
                STOP.wait(.02)
                continue
            next_poll = time.monotonic() + .25
            try:
                measurement = read_measurement()
                # Do not speak old readings when the USB instrument stops updating.
                age = time.time() - float(measurement['timestamp'])
                if not 0 <= age <= 3:
                    raise ValueError('Misura non aggiornata')
                parts = measurement_parts(measurement)
                should_speak = requested or policy.update(measurement, time.monotonic(), time.time())
                with lock:
                    unchanged = control['version'] == version
                if should_speak and (requested or unchanged):
                    logging.info('%s: misura %s; tracce %s', 'TALK' if requested else 'AUTO', measurement, parts)
                    speak_parts(parts)
                    policy.spoken(measurement, time.monotonic())
            except Exception:
                policy.invalidate()
                now = time.monotonic()
                if requested or now-error_logged_at >= 30:
                    logging.exception('Errore lettura o riproduzione')
                    error_logged_at = now
                if requested:
                    try:
                        speak_parts(['no_info'])
                    except Exception:
                        logging.exception('Avviso misura non disponibile fallito')
                STOP.wait(.25)

    with DigitalInputDevice(17, pull_up=True) as pedal, DigitalInputDevice(22, pull_up=True) as talk:
        edge, key = PedalEdge(), TalkButton()
        worker = threading.Thread(target=audio_worker, name='logivox-audio', daemon=True)
        worker.start()
        logging.info('Pedale GPIO17; TALK/AUTO GPIO22 (pin15); LED voce GPIO23 (pin16); AUTO disattivato')
        while not STOP.is_set():
            now = time.monotonic()
            pedal_pressed = edge.update(pedal.is_active, now)
            action = key.update(talk.is_active, now)
            if pedal_pressed or action == 'talk':
                logging.info('Richiesta manuale: %s', 'pedale' if pedal_pressed else 'Talk')
                manual.set()  # Coalesce requests rather than queue old measurements.
            if action == 'toggle_auto':
                with lock:
                    control['auto'] = not control['auto']
                    control['version'] += 1
                    logging.info('AUTO=%s', control['auto'])
            STOP.wait(.01)
        worker.join(timeout=6)

if __name__ == '__main__': main()
