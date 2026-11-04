# LogiVOX

**A voice for your bench multimeter.**

LogiVOX is a DIY speaking companion for the **OWON XDM1041**, built by Sergio Veneziani using a Raspberry Pi Zero 2 W, USB communication, a MAX98357A I²S amplifier, a foot pedal and a custom enclosure.

[Documentazione italiana](README.it.md) · [Hardware review](docs/HARDWARE-REVIEW.md) · [TALK/AUTO](docs/TALK-AUTO.md)

## Project status

The assembled prototype works and has been tested by its builder. This repository is a **private preparation draft**, not yet a reproducible fabrication release. Hardware files still have DRC/parity items to review, enclosure CAD is not included yet, and redistributable audio/licensing choices are pending.

## Features

- Press the foot pedal or briefly press TALK to hear a reading.
- Hold TALK for two seconds to toggle AUTO, with spoken confirmation.
- AUTO speaks stable, significant changes instead of repeating every few seconds.
- Italian prerecorded number/unit fragments: normal operation does not require a cloud TTS service.
- READY and VOICE indicators.
- Battery-backed orderly shutdown, followed by hardware power disconnection.
- An existing OWON server supplies the USB connection, web dashboard and measurement API.

Only the OWON XDM1041 has been tested with this build. AUTO defaults to off at startup. FORCE OFF cuts power directly; it is not an orderly software shutdown.

## Repository layout

- `Software/raspberry/bin/`: voice playback, pedal/TALK/AUTO and UPS services.
- `Software/raspberry/tests/`: hardware-independent logic tests.
- `Software/raspberry/services/`: existing service templates (paths currently reference the prototype user).
- `Software/tools/`: local voice generation helper for macOS.
- `hardware/kicad/`: current schematic/PCB/project snapshot.
- `docs/`: current pinout, operating notes and outstanding hardware review.
- `enclosure/`: CAD exports pending.

## Tests

```sh
python3 -m unittest discover -s Software/raspberry/tests -v
```

The optional audio-file presence test is skipped when the voice pack is absent. This does not validate audio playback or the physical UPS.

## Installation status

See [installation notes](docs/INSTALLATION.md). The prototype runs Debian 13 on a Raspberry Pi Zero 2 W. A clean-device installation guide and complete service packaging are still being prepared; do not treat the current files as a one-click installer.

## Credits

- Design, assembly, mechanical enclosure and bench testing: **Sergio Veneziani**.
- Development and troubleshooting assistance: OpenAI ChatGPT/Codex; additional debugging with Cursor.
- USB/web/API backend: [Jason Antman's owon-xdm1041-server](https://github.com/jantman/owon-xdm1041-server), licensed MIT by its author. The backend is a separate dependency and is not vendored here.
- SCPI research credited by that backend: [TheHWcave/OWON-XDM1041](https://github.com/TheHWcave/OWON-XDM1041).
- Initial inspiration: [Arduino-Based Speech Add-on for Modern Multimeters with SCPI Protocol](https://www.pcbway.com/project/shareproject/Arduino_Based_Speech_Add_on_for_Modern_Multimeters_with_SCPI_Protocol_95abefd4.html). The original Arduino sketch is not included in this repository.

## Licensing

Licenses for LogiVOX software, hardware and documentation are **not yet selected**. No blanket open-source license is asserted in this draft. Third-party projects retain their own licenses. Generated voice recordings are deliberately excluded pending redistribution-rights review.
