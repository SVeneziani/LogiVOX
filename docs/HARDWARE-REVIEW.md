# Hardware review before fabrication

Updated 2026-11-04 from the saved builder files. Original design files were copied unchanged. The prototype was manually reworked; this snapshot is not yet a fabrication release. No old Gerbers are included.

## PCB design-rule check

KiCad CLI check with schematic parity enabled:

- 0 DRC violations.
- 0 unconnected items.
- 8 schematic/PCB parity warnings, listed below.

The previous clearance, thermal connection, unconnected copper and silkscreen findings are no longer reported under the saved project rules. A clean DRC does not independently validate manufacturing limits or circuit operation.

## Schematic/PCB parity

- Impronta mancante BT1 (Battery_Cell)
- (SW1) non corrisponde al valore del simbolo (TALK_AUTO)
- Impronta mancante TP1 (GND)
- Impronta mancante TP2 (VDD_5V)
- Impronta mancante TP3 (BCLK)
- Impronta mancante TP4 (LRCLK)
- Impronta mancante TP5 (DIN)
- Impronta mancante TP6 (PEDALE_IN)

BT1 and TP1–TP6 may be intentionally absent from the PCB; document that intent or reconcile them before release. SW1 has a value/name mismatch with the schematic (TALK_AUTO), not a reported connectivity mismatch.
