# Prototype installation notes

These notes describe the existing device, not a verified fresh installation recipe.

## Runtime

- Raspberry Pi Zero 2 W, Debian 13, Python 3 with gpiozero/lgpio and ALSA `aplay`.
- External OWON backend: https://github.com/jantman/owon-xdm1041-server
- Voice code expects `http://127.0.0.1:8080/api/identify` and `/api/measurement`.
- Live measurements need `timestamp`, `function`, `value`, `unit`. AUTO rejects readings older than three seconds.
- Runtime files are placed under `~/LogiVOX/bin/`; audio under `~/LogiVOX/audio/audio_it/`.
- Existing prototype services are named `logivox`, `logivox-ready`, `logivox-pedal` (user services), and `logivox-ups` (system service). Server and pedal service packaging must be completed before release.
- Included service templates use `/home/sadmin/LogiVOX`; adapt to the actual account.

## Final GPIO mapping

| Function | BCM | Physical pin |
|---|---:|---:|
| Pedal | 17 | 11 |
| READY LED (blue on prototype) | 27 | 13 |
| TALK/AUTO switch, pull-up | 22 | 15 |
| VOICE LED (red on prototype) | 23 | 16 |
| PWR_FAIL, high when external USB power absent | 24 | 18 |
| HALT_DONE, kernel controlled | 26 | 37 |
| I²S BCLK | 18 | 12 |
| I²S LRCLK | 19 | 35 |
| I²S DIN | 21 | 40 |

The green POWER LED is on switched VDD, not a GPIO. The speaker connects only between amplifier OUTP and OUTN.

Audio boot settings: `dtparam=audio=off` and `dtoverlay=max98357a,no-sdmode`. ALSA device: `plughw:CARD=MAX98357A,DEV=0`.

## UPS commissioning

The monitor without `--poweroff` only observes. With `--poweroff`, two seconds of power failure trigger a bounded spoken announcement followed by `systemctl poweroff`. Audio failure does not prevent shutdown. The hardware must remove power when HALT_DONE rises.

Only after verifying the physical shutdown circuit, add `dtoverlay=gpio-poweroff,gpiopin=26` under `[all]` and enable the system UPS service. Do not also claim GPIO24 with `gpio-shutdown`. The overlay changes shutdown behavior and requires the external power-cut circuit. Booting on battery alone also requests shutdown. Reinserting USB while shutdown is underway may require another external-power cycle after shutdown completes.

Full hardware commissioning instructions are pending review. Do not infer hardware validation from the unit tests.
