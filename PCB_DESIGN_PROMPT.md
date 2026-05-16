# Clean-context PCB design prompt

Paste the entire block below into a fresh Claude Code conversation in
this repository. It is self-contained — it does not assume any prior
conversation context, and it explicitly tells you to ignore the tainted
directories from previous attempts.

---

Design a custom PCB for the "Ah! My Groin!" button-triggered audio
device. Final deliverable: Gerber files and a drill file ready to
upload to JLCPCB.

## Read first (source of truth)

- `v2/README.md` — full functional spec, schematic intent, layout
  requirements, KiCad workflow
- `v2/bom.md` — every Amazon ASIN purchased for this build
- `v2/firmware/main.cpp` — pin assignments and timing
- Persistent memory: `MEMORY.md` plus the files it references —
  especially `purchased_components.md` (ASIN registry) and
  `kicad_mcp_setup.md` (env vars for the MCP server)

## Tainted directories — DO NOT touch or reference

- `pcb/` — v1 perfboard-era reference design with broken assumptions
  (wrong DFPlayer Mini, wrong power topology, hand-coded footprints).
- `codex/` — previous procedural-pcbnew attempt that hand-coded
  footprint geometry from arbitrary dimensions. Hole sizes were wrong.
- `claude/` — previous Claude attempt that forked Codex's bad approach
  with cosmetic tweaks, then again with a from-scratch script that
  *still* hand-coded footprints. 116 DRC violations on the second pass.

If any of those directories still exist, ignore them entirely. Do not
import, fork, or reference their contents. Do not even open their
files for "inspiration."

## Hard constraints — non-negotiable

1. **Use KiCad 10's standard footprint library at
   `K:\Program Files\KiCad\10.0\share\kicad\footprints\`.** Do NOT
   hand-code footprints with custom dimensions. Hand-coded footprints
   are how this project's previous attempts got hole sizes wrong (JST-XH
   pitch is 2.50 mm, *not* 2.54 mm — a bug Codex and Claude both shipped).

2. **Schematic-first workflow.** Build a real `.kicad_sch` with proper
   symbols, run ERC, sync the netlist to a fresh `.kicad_pcb`, place
   footprints, route, DRC. Do NOT write a procedural Python script
   that generates a `.kicad_pcb` directly without a schematic. That's
   the hack the previous attempts took, and it skips the validation
   that comes from having a real netlist.

3. **Use the KiCad MCP server** for the schematic and PCB work. It is
   already configured in `.mcp.json` with verified env vars (see
   `kicad_mcp_setup.md` in memory if anything looks off). The MCP
   exposes schematic-capture tools (`add_schematic_component`,
   `add_schematic_wire`, `add_schematic_net_label`,
   `annotate_schematic`, `run_erc`), PCB tools (`sync_schematic_to_board`,
   `place_component`, `route_pad_to_pad`, `autoroute`, `add_zone`),
   and validation (`run_drc`, `get_drc_violations`).

4. **Use `kicad-cli` directly via Bash for DRC and Gerber export** —
   the MCP's wrappers for these have PATH issues on this machine and
   silently produce empty output. Path:
   `K:\Program Files\KiCad\10.0\bin\kicad-cli.exe`.

5. **Refill GND zones in the KiCad GUI before final Gerber export.**
   The SWIG zone-fill API on Windows / KiCad 10 crashes the Python
   helper. Open the board, press B, save, then re-export Gerbers.

6. **Place the new design in a fresh directory named `kicad/`.** Do NOT
   reuse `pcb/`, `codex/`, `claude/`, or any variant.

## Tooling paths (Windows, this machine)

- KiCad 10 root: `K:\Program Files\KiCad\10.0\`
- Bundled Python (has `pcbnew`, `sexpdata`, `kicad-skip`):
  `K:\Program Files\KiCad\10.0\bin\python.exe`
- `kicad-cli`: `K:\Program Files\KiCad\10.0\bin\kicad-cli.exe`
- Standard footprints: `K:\Program Files\KiCad\10.0\share\kicad\footprints\`
- Standard symbols: `K:\Program Files\KiCad\10.0\share\kicad\symbols\`

## Components to mount

Verify each ASIN against `v2/bom.md` and the `purchased_components.md`
memory file before placing. If any of those listings has changed since
this prompt was written, prefer the file content.

### Through-hole

| Ref     | Part                                  | Amazon ASIN     | Footprint to use (standard lib)                                  |
| ------- | ------------------------------------- | --------------- | ---------------------------------------------------------------- |
| U1      | HiLetgo Pro Mini 3.3V / 8MHz          | B07RS911JD      | Two `Connector_PinHeader_2.54mm:PinHeader_1x12_P2.54mm_Vertical` placed 15.24 mm apart (the standard SparkFun Pro Mini row pitch). The module plugs onto the headers; the headers solder to the PCB. |
| U2      | DY-SV17F audio module                 | B0BPSPPW52      | Two `Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical` placed 17.78 mm apart (DY-SV17F row pitch). |
| C1      | 1000 µF aluminum electrolytic radial  | from B0GMKLB2QM | Verify the actual cap diameter and pin pitch from the kit before choosing footprint. Likely `Capacitor_THT:CP_Radial_D10.0mm_P5.00mm`. |
| C4      | 100 µF aluminum electrolytic radial   | from B0GMKLB2QM | Likely `Capacitor_THT:CP_Radial_D6.3mm_P2.50mm`. |
| J1, J2, J3 | JST-XH 2-pin male PCB header     | B0B77CSH85      | `Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical`. **Do not override the pitch.** |
| H1–H4   | M3 mounting holes                     | n/a             | `MountingHole:MountingHole_3.2mm_M3_Pad_TopBottom` so each hole has a copper ring on both layers tied to GND — doubles as ground stitching. |

### Surface mount

| Ref     | Part                          | Amazon ASIN                        | Footprint                                                  |
| ------- | ----------------------------- | ---------------------------------- | ---------------------------------------------------------- |
| Q1, Q3  | AO3401A P-MOSFET, SOT-23      | B08RHFLH1K                         | `Package_TO_SOT_SMD:SOT-23`                                 |
| Q4      | MMBT3904 NPN, SOT-23          | B0D69KD677 (kit, marking `1AM`)    | `Package_TO_SOT_SMD:SOT-23`                                 |
| R1      | 10 kΩ 0805                    | B09538ZBCR (kit)                   | `Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder`  |
| R2      | 100 kΩ 0805                   | B09538ZBCR (kit)                   | same                                                       |
| C2, C6  | 10 µF 0805 ceramic            | B0F5QB3S8V (kit)                   | `Capacitor_SMD:C_0805_2012Metric_Pad1.20x1.40mm_HandSolder` |
| C3, C5  | 0.1 µF 0805 ceramic           | B0F5QB3S8V (kit)                   | same                                                       |

The `_HandSolder` footprint variants have slightly larger pads than
the IPC-spec versions — better for hand assembly with this user's
soldering iron.

### Off-board (wired through JST connectors)

| External                                                | → Connector |
| ------------------------------------------------------- | ----------- |
| 3×AA holder w/ on-off switch (B07C6XC3MP)               | J1 (BAT)    |
| EG STARTS 100mm arcade button (B01LZMANZ7), microswitch only — LED is 12 V and intentionally NOT driven | J2 (BTN)    |
| Adafruit ADA1313 speaker, 3" / 8 Ω / 1 W (B00XW2NPTG)   | J3 (SPK)    |

## Net list

| Net          | Description                                                       |
| ------------ | ----------------------------------------------------------------- |
| `VBATT`      | Battery+ from holder leads (already switched by the holder)       |
| `VSYS`       | After Q3 reverse-polarity FET; powers Pro Mini RAW and Q1 source  |
| `VDFP`       | After Q1; powers DY-SV17F V5 (the 5 V audio rail)                 |
| `Q1_GATE`    | Q4 collector / Q1 gate / R2 pull-up midpoint                      |
| `Q4_BASE`    | Pro Mini D5 → R1 → Q4 base                                       |
| `BTN_IN`     | Pro Mini D2 ↔ button microswitch via J2 (Pro Mini internal pullup) |
| `TRIG_OUT`   | Pro Mini D6 → DY-SV17F IO1                                       |
| `BUSY_IN`    | Pro Mini D7 ← DY-SV17F BUSY pin (LOW while playing)              |
| `SPK_P`, `SPK_N` | DY-SV17F SPK+ / SPK- → J3 (bridge-tied — never tie to GND)   |
| `GND`        | Common ground                                                    |

## Schematic structure

Power chain: J1 → Q3 (reverse-polarity P-FET, source=`VBATT`,
drain=`VSYS`, gate=`GND`) → C1 (bulk on `VSYS`) → Pro Mini RAW pin.
C2 + C3 decouple `VSYS` near the Pro Mini.

DY-SV17F gate: Q1 (high-side P-FET, source=`VSYS`, drain=`VDFP`,
gate=`Q1_GATE`). The Pro Mini at 3.3 V can't fully switch off Q1's
gate (which sits at 4.5 V `VSYS`), so a level shifter is required.
Q4 (NPN, base via R1 from D5, emitter=`GND`, collector=`Q1_GATE`)
provides that. R2 (100 kΩ pull-up `VSYS` → `Q1_GATE`) keeps Q1 OFF
when Q4 is OFF (sleep mode).

DY-SV17F decoupling: C4 (100 µF) + C5 (0.1 µF) + C6 (10 µF) on
`VDFP`, all within 5 mm of the module's V5 pin.

Audio: SPK+ / SPK- straight from DY-SV17F to J3, parallel pair, both
on F.Cu, 0.5 mm wide minimum, away from any digital signal trace.

Digital: D6 → DY-SV17F IO1 (single trace), D7 ← BUSY (single trace),
D2 ↔ J2.1 (one trace via the PCB).

## PCB requirements

- 2-layer FR4
- **2.0 mm thickness** (drop survival)
- HASL surface finish (cheapest, fine)
- Copper pour on F.Cu and B.Cu, both tied to `GND`, stitched with
  vias near every component
- Connectors clustered on **one edge** so the wire bundle exits the
  same side of the enclosure
- Mounting holes at the four corners, M3 NPTH with copper rings tied
  to `GND` (use `MountingHole_3.2mm_M3_Pad_TopBottom`)
- All component reference designators on F.Silkscreen sized ≥ 0.85 mm
  (KiCad's silkscreen size guard silently drops smaller text)
- Polarity markers on J1 (`+` / `-`) and J3 (`+` / `-`); signal
  markers on J2 (`S` / `G`)
- DRC clean (0 violations, 0 unconnected items) and 3D render visually
  verified before exporting Gerbers

## Workflow (the right way)

1. Read the spec files listed at the top.
2. Create `kicad/` directory in the project root.
3. Have the MCP server create a fresh KiCad project there.
4. Build the schematic in the MCP. Add every symbol from the BOM,
   wire them per the net list above, label every net, annotate
   reference designators, run ERC. Fix any errors.
5. Sync the schematic to the PCB (this brings the netlist over).
6. Assign each schematic symbol the correct footprint from the
   standard library — never custom geometry.
7. Place footprints with intent: modules at the top edge so the FTDI
   end of the Pro Mini overhangs (programmable in-circuit), connectors
   along the bottom edge, discretes between modules.
8. Route. Power and audio on F.Cu wide, signals on B.Cu narrow,
   speaker as a tight pair. Use FreeRouting via the MCP if available;
   otherwise manual.
9. Run DRC. Fix every violation. Repeat until clean.
10. **Open the PCB in the KiCad GUI** and press `B` to fill GND zones
    (do not try this from the MCP — SWIG zone fill crashes Python on
    Windows here). Save.
11. Re-run DRC after the zone fill. Still clean? Good.
12. Render a 3D view top + bottom and verify visually.
13. Export Gerbers via `kicad-cli pcb export gerbers` and drill files
    via `kicad-cli pcb export drill`. Bundle into a zip.

## When in doubt

- Ask the user. Don't guess at hole sizes, pad shapes, or mechanical
  dimensions.
- Especially ask when you can't find an exact-matching standard
  footprint — there's almost always a generic one (pin headers,
  generic SOT-23, generic radial cap) that's correct.
- The user has been burned by silent guesses in two previous
  attempts. They prefer "stop and ask" over "ship something wrong."

---

End of prompt.
