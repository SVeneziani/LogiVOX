# Hardware review before fabrication

This source snapshot is a working draft, not a fabrication release. The prototype was manually reworked. No old Gerbers are included.

Current KiCad DRC / schematic parity results:


## violations

- Violazione clearance ( clearance 0.2000 mm; reale 0.0750 mm)
  - Via [/J1-15] su F.Cu - B.Cu {'x': 112.0, 'y': 89.5}
  - Pista [/PWR_FAIL] su F.Cu, lung. 22.0165 mm {'x': 128.55, 'y': 89.0}
- Via is not connected or connected on only one layer
  - Via [GND] su F.Cu - B.Cu {'x': 152.0, 'y': 97.5}
- Silkscreen clipped by board edge
  - Rettangolo su Edge.Cuts {'x': 58.5, 'y': 80.0}
  - Rettangolo su F.Silkscreen {'x': 213.0, 'y': 85.0}
- Silkscreen clipped by board edge
  - Rettangolo su Edge.Cuts {'x': 58.5, 'y': 80.0}
  - Rettangolo di Step-Up_5V_2A1 su F.Silkscreen {'x': 179.0, 'y': 120.0}

## unconnected_items

- Missing connection between items
  - Piazzola PTH  17 [GND] di U1 {'x': 156.607359, 'y': 97.191938}
  - Via [GND] su F.Cu - B.Cu {'x': 152.0, 'y': 97.5}

## schematic_parity

- Impronta mancante BT1 (Battery_Cell)
- Impronta mancante TP1 (GND)
- Impronta mancante TP2 (VDD_5V)
- Impronta mancante TP3 (BCLK)
- Impronta mancante TP4 (LRCLK)
- Impronta mancante TP5 (DIN)
- Impronta mancante TP6 (PEDALE_IN)
