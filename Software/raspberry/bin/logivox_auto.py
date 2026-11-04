"""Pure TALK/AUTO decisions, independent of GPIO, networking and audio."""
from collections import deque
import math

# Base SI units. These are speech filters, not instrument accuracy claims.
ABS_FLOORS = {'V': .001, 'A': .000001, 'OHM': 1., 'OHMS': 1.,
              'Ω': 1., 'F': 1e-9, 'HZ': .1, 'C': .1, '°C': .1}


class TalkButton:
    """Short action on release; one long action after 2 s; release to arm."""
    def __init__(self, debounce=.05, hold=2.):
        self.debounce, self.hold = debounce, hold
        self.candidate = self.stable = None
        self.since = 0.
        self.armed = False
        self.down = None
        self.long_sent = False

    def update(self, pressed, now):
        if pressed != self.candidate:
            self.candidate, self.since = pressed, now
        if now - self.since >= self.debounce and self.stable != pressed:
            self.stable = pressed
            if not pressed:
                short = self.down is not None and not self.long_sent
                self.armed, self.down = True, None
                if short:
                    return 'talk'
            elif self.armed:
                self.armed = False
                self.down = now
                self.long_sent = False
        if self.stable and pressed and self.down is not None:
            if not self.long_sent and now - self.down >= self.hold:
                self.long_sent = True
                return 'toggle_auto'
        return None


class AutoReader:
    """Speak stable significant changes; commit only after successful playback."""
    def __init__(self, stable_seconds=1., relative_change=.01,
                 relative_stability=.002, min_interval=3., stale_seconds=3.):
        self.stable_seconds = stable_seconds
        self.relative_change = relative_change
        self.relative_stability = relative_stability
        self.min_interval = min_interval
        self.stale_seconds = stale_seconds
        self.samples = deque()
        self.last_timestamp = None
        self.last_spoken = None
        self.last_spoken_at = -math.inf
        self.signature = None

    def invalidate(self):
        self.samples.clear()
        self.last_timestamp = None
        self.signature = None

    @staticmethod
    def normalized(m):
        value = float(m['value'])
        if not math.isfinite(value):
            raise ValueError('Non-finite measurement')
        signature = (str(m['function']).upper(), str(m['unit']).upper(),
                     str(m.get('mode', '')).upper(), value >= 1e9)
        return signature, value

    def update(self, m, now, wall_now):
        try:
            signature, value = self.normalized(m)
            stamp = float(m['timestamp'])
            if not math.isfinite(stamp) or not 0 <= wall_now - stamp <= self.stale_seconds:
                raise ValueError('Stale measurement')
        except (KeyError, TypeError, ValueError):
            self.invalidate()
            return False
        if self.last_timestamp is not None and stamp <= self.last_timestamp:
            return False
        if signature != self.signature or (self.last_timestamp is not None and
                                            stamp - self.last_timestamp > self.stale_seconds):
            self.samples.clear()
        self.signature, self.last_timestamp = signature, stamp
        self.samples.append((stamp, value))
        # Keep the sample at/before the start of the stability window.
        while len(self.samples) > 1 and self.samples[1][0] <= stamp - self.stable_seconds:
            self.samples.popleft()
        if len(self.samples) < 3 or stamp - self.samples[0][0] < self.stable_seconds:
            return False
        floor = ABS_FLOORS.get(signature[1], 1e-12)
        low = min(v for _, v in self.samples)
        high = max(v for _, v in self.samples)
        if not signature[3] and high-low > max(floor, abs(value)*self.relative_stability):
            return False
        if now-self.last_spoken_at < self.min_interval:
            return False
        if self.last_spoken is None or self.last_spoken[0] != signature:
            return True
        if signature[3]:
            return False  # Open/overrange is announced once, not repeatedly.
        old = self.last_spoken[1]
        return abs(value-old) >= max(floor, abs(old)*self.relative_change)

    def spoken(self, measurement, now):
        self.last_spoken = self.normalized(measurement)
        self.last_spoken_at = now
