# Ah My Groin v2 KiCad Board

This folder contains a generated KiCad 10 first-pass PCB for the v2 board described in `../v2/README.md`.

Files:

- `ah_my_groin_v2.kicad_pro` - KiCad project
- `ah_my_groin_v2.kicad_pcb` - PCB layout
- `ah_my_groin_v2.kicad_sch` - companion schematic file
- `generate_v2_board.py` - deterministic board generator
- `drc.json` - latest KiCad CLI DRC report

Regenerate the PCB with KiCad's bundled Python:

```powershell
& 'K:\Program Files\KiCad\10.0\bin\python.exe' .\generate_v2_board.py
```

Run DRC:

```powershell
& 'K:\Program Files\KiCad\10.0\bin\kicad-cli.exe' pcb drc --format json --output '.\drc.json' '.\ah_my_groin_v2.kicad_pcb'
```

Current validation: 0 DRC violations and 0 unconnected items.

Layer note: only `F.SilkS` / `B.SilkS` silkscreen graphics are printed on the board. `F.Fab`, `B.Fab`, `Cmts.User`, `Dwgs.User`, hidden footprint properties, ratsnest lines, and selection/highlight graphics are KiCad editor aids unless they are explicitly included in a plot/export job. The generator keeps the manufactured silkscreen intentionally sparse, but restores useful component/test-point labels on `F.Fab` and assembly notes on `Cmts.User` so they remain visible in KiCad without overlapping pads or creating silkscreen DRC errors.

C6 uses the same generated 0805-style two-pad footprint as C2/C3/C5: 1.8 mm pad-center pitch with 0.85 mm wide pads, leaving about 0.95 mm copper-to-copper pad gap before solder mask expansion. KiCad DRC reports no clearance issue there.

U1 models the HiLetgo Pro Mini 3.3 V / 8 MHz module with the two 1x12 side headers, the top auxiliary pads `GND`, `A6`, `A7`, `DTR`, `TXO`, `RXI`, `VCC`, `GND`, `GND`, and the inner `A4` / `A5` pads. Only `RAW`, the required side-header signals, and the extra `GND` pads are connected by this v2 board; the other auxiliary pads are present for fit/orientation accuracy and left NC.
