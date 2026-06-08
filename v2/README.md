# Ah! My Groin! — v2 PCB Design (recommended)

v1 (in `pcb/`) is a working design but inherits complexity the project doesn't
need. v2 is what you should actually build. Same energy efficiency, simpler
firmware, fewer parts, and real drop-resistance — which is the failure mode
that killed the previous hand-soldered unit.

## TL;DR — what changed and why

| Aspect              | v1 (`pcb/`)                          | v2 (this folder)                         | Why                                                                    |
| ------------------- | ------------------------------------ | ---------------------------------------- | ---------------------------------------------------------------------- |
| Audio module        | DFPlayer Mini (WWZMDiB clone)        | **DY-SV17F**                             | Onboard 4 MB flash; no SD card; no clone variants; 24-bit DAC; 5 W amp |
| Storage             | microSD, FAT32, 0001.mp3 in root     | Onboard flash, files loaded via USB once | One less thing to lose, corrupt, or forget to format                   |
| MCU ↔ audio link    | SoftwareSerial 9600 baud + library   | One trigger pin + one BUSY pin           | No library, no timing fudges, no clone-specific delays                 |
| Firmware            | ~150 lines, DFPlayer library         | ~60 lines, no library                    | Less to break                                                          |
| Modules mounted     | Female 0.1″ sockets (can unseat)     | **Soldered through plated through-holes**| The fix for the "fell apart when dropped" failure                      |
| External connectors | Phoenix screw terminals (vibrate)    | **JST-XH 2.54 mm latching**              | Crimp-and-locked, ride out shocks                                      |
| PCB thickness       | 1.6 mm                               | **2.0 mm**                               | +$1 for 5 boards from JLCPCB; less flex on impact                      |
| MCU                 | HiLetgo Pro Mini 3.3V/8MHz           | Same — **reuses the 3 you already own**  | No reason to throw them away                                           |
| Per-build cost      | ~$25                                 | ~$22                                     | DY-SV17F ≈ DFPlayer cost; net saved on SD card                         |

## Why this is the right architecture

The previous hand-built unit you made for your friend "came unsoldered when
kids dropped it" — that's a mechanical failure mode, not an electrical one.
The whole v2 design pivots on that: solder joints under shock are the enemy.

Specifically:
1. **Female header sockets are the single biggest drop-failure point** in
   hobby PCBs. The module sits in a socket, the socket pins are TH-soldered
   to the PCB, and the module's own pins are friction-fit into the socket.
   Drop it hard and the friction-fit gives. v2 skips sockets — modules go
   pin-through PCB and get soldered on the bottom layer. The module is now
   mechanically part of the PCB.
2. **Screw terminals back themselves out under vibration.** JST-XH crimped
   connectors latch positively and don't move under repeated shock.
3. **A 2.0 mm PCB flexes ~40 % less than a 1.6 mm PCB** under the same
   impact, and the cost difference at JLCPCB scale is negligible.
4. **Conformal coating** (an acrylic spray like MG Chemicals 419D, $10/can)
   over the populated board encapsulates every joint. Optional but very much
   recommended for a unit going to a kid.

The DY-SV17F audio module switch is a separate win. The DFPlayer Mini exists
for use cases this project doesn't have (large SD card libraries, multi-track
sequencing, EQ control). Trading it for the DY-SV17F drops:
- The SD card and all its corruption / format / compatibility risk.
- The SoftwareSerial protocol and the WWZMDiB clone's 2-second command-gap
  penalty.
- The DFPlayer library dependency.
- About 90 lines of firmware.

In return: 4 MB onboard flash (~30 seconds of MP3 at decent quality), USB
file loading from your PC, a clean trigger-pin interface, and a slightly
better audio path. ~$5 from any Amazon vendor.

## 1. Block diagram

```
   3×AA holder ──► Q3 (rev polarity P-MOSFET) ──► VSYS ──┬─────────┐
   (with built-in                                        │         │
    on/off switch)                                       ▼         ▼
                                                   ┌─────────┐ ┌─────────┐
                                                   │ Pro Mini│ │  Q1     │
                                                   │  RAW    │ │ P-MOSFET├──► VDFP ──► DY-SV17F V5
                                                   └────┬────┘ └────┬────┘
                                                        │           ▲
                                                   D5 (GATE_CTRL) ──► Q4 NPN level shifter
                                                   D6 (TRIG)  ─────────────────► DY-SV17F IO0 (right pin 1)
                                                   D7 (BUSY)  ◄───────────────── DY-SV17F CON3/BUSY (left pin 7)
                                                   D2 (BTN)   ◄────── J2 ◄── EG STARTS microswitch
                                                                                DY-SV17F SPK+/− ──► J3 ──► speaker
```

Power switch lives on the LAMPVPATH battery holder, not on the PCB — so
there's no SW1 in v2. The holder's leads (red = +, black = GND) terminate
in J1 and that's the system's "after-switch" rail.

## 2. Net list

| Net          | Description                                                      |
| ------------ | ---------------------------------------------------------------- |
| `VBATT`      | Battery+ from holder leads (already switched by the holder)      |
| `VSYS`       | After Q3 (reverse-protection FET); powers Pro Mini RAW + Q1.S    |
| `VDFP`       | After Q1; powers DY-SV17F V5                                     |
| `PFET_GATE`  | Q1 gate / Q4 NPN collector / R2 pullup                           |
| `GND`        | Battery− and system ground                                       |
| `BTN_IN`     | D2 ← microswitch                                                 |
| `TRIG_OUT`   | D6 → DY-SV17F IO0 (pulse LOW to trigger `00001.mp3`)             |
| `BUSY_IN`    | D7 ← DY-SV17F BUSY pin (LOW = playing)                           |
| `GATE_CTRL`  | D5 → R1 → Q4 base                                                |

## 3. Components

| Ref     | Part                                  | Footprint                                                        |
| ------- | ------------------------------------- | ---------------------------------------------------------------- |
| U1      | HiLetgo Pro Mini 3.3 V / 8 MHz module | 2× `PinSocket_1x12_P2.54mm_Vertical` (soldered as TH headers)    |
| U2      | DY-SV17F audio module                 | DIP-18, 2.5 mm metric pitch, 20.5 mm row pitch (v3); see PINOUTS.md |
| Q1      | AO3401A P-MOSFET                      | `SOT-23`                                                         |
| Q3      | AO3401A P-MOSFET (reverse polarity)   | `SOT-23`                                                         |
| Q4      | MMBT3904 NPN BJT                      | `SOT-23`                                                         |
| R1      | 10 kΩ ±1 % 0805                       | `R_0805_2012Metric`                                              |
| R2      | 100 kΩ ±1 % 0805                      | `R_0805_2012Metric`                                              |
| C1      | 1000 µF / 10 V electrolytic           | `CP_Radial_D10.0mm_P5.00mm`                                      |
| C2      | 10 µF X5R 0805                        | `C_0805_2012Metric`                                              |
| C3      | 0.1 µF X7R 50 V 0805                  | `C_0805_2012Metric`                                              |
| C4      | 100 µF / 10 V electrolytic            | `CP_Radial_D6.3mm_P2.50mm`                                       |
| C5      | 0.1 µF X7R 50 V 0805                  | `C_0805_2012Metric`                                              |
| C6      | 10 µF X5R 0805                        | `C_0805_2012Metric`                                              |
| J1      | JST-XH 2-pin (battery)                | `JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical`                          |
| J2      | JST-XH 2-pin (button)                 | same                                                             |
| J3      | JST-XH 2-pin (speaker)                | same                                                             |
| H1–H4   | M3 mounting holes                     | `MountingHole_3.2mm_M3`                                          |

DY-SV17F symbol+footprint: not in stock KiCad libs. v3 uses the stock
`PinHeader_1x09_P2.54mm_Vertical` footprint with per-pad position
overrides at build time (in `kicad/build_v3.py`) to reach the true
2.5 mm metric pitch. **2 rows of 9 pins (DIP-18), 2.5 mm pitch within
each row, 20.5 mm pad-center-to-pad-center between rows, body ≈ 26 × 23
mm.** Pin map (verified against physical module 2026-05-19):

```
        LEFT side             RIGHT side
        (top → bottom)        (top → bottom)
        ┌─────────────┐       ┌─────────────┐
    1   │ SPK+        │   1   │ TX  / IO0   │  ← TRIG_OUT (D6)
    2   │ SPK−        │   2   │ RX  / IO1   │
    3   │ DACL        │   3   │ IO2         │
    4   │ DACR        │   4   │ IO3         │
    5   │ V33         │   5   │ ONE_LINE/IO4│
    6   │ V5  (VDFP)  │   6   │ IO5         │
    7   │ CON3/BUSY   │   7   │ IO6         │
        │  → BUSY_IN (D7) and 10 kΩ pull-down to GND
    8   │ CON2        │   8   │ IO7         │
    9   │ CON1        │   9   │ GND         │
        └─────────────┘       └─────────────┘
```

(Pin numbering and orientation: verify against the silkscreen on your
specific module before laying out — DY-SV17F clones occasionally renumber.)

## 4. Connection table

### J1 — Battery (JST-XH 2-pin)

| Pin | Net      |
| --- | -------- |
| 1   | `VBATT`  |
| 2   | `GND`    |

The LAMPVPATH 3×AA holder's red lead crimps into J1.1; black into J1.2. The
holder's built-in slide switch is the system's master power switch.

### Q3 — Reverse-polarity P-MOSFET (AO3401A)

| Pin   | Net      |
| ----- | -------- |
| 1 G   | `GND`    |
| 2 D   | `VSYS`   |
| 3 S   | `VBATT`  |

### Q1 — DY-SV17F gate P-MOSFET (AO3401A)

| Pin   | Net          |
| ----- | ------------ |
| 1 G   | `PFET_GATE`  |
| 2 D   | `VDFP`       |
| 3 S   | `VSYS`       |

### Q4 — NPN level shifter (MMBT3904)

| Pin   | Net           |
| ----- | ------------- |
| 1 B   | (R1 ← `GATE_CTRL`) |
| 2 E   | `GND`         |
| 3 C   | `PFET_GATE`   |

### Decoupling

| Cap | From   | To    | Place near                          |
| --- | ------ | ----- | ----------------------------------- |
| C1  | `VSYS` | `GND` | Q3 drain / battery input            |
| C2  | `VSYS` | `GND` | Pro Mini RAW pin                    |
| C3  | `VSYS` | `GND` | Pro Mini RAW pin                    |
| C4  | `VDFP` | `GND` | DY-SV17F V5 pin                     |
| C5  | `VDFP` | `GND` | DY-SV17F V5 pin                     |
| C6  | `VDFP` | `GND` | DY-SV17F V5 pin                     |

### J2 — Button (JST-XH 2-pin)

| Pin | Net       |
| --- | --------- |
| 1   | `BTN_IN`  |
| 2   | `GND`     |

EG STARTS button: wire only the 4.8 mm spade microswitch terminals (`COM` →
J2.2, `NO` → J2.1). The 6.3 mm LED spades are 12 V and intentionally not
driven.

### J3 — Speaker (JST-XH 2-pin)

| Pin | Net (DY-SV17F)         |
| --- | ---------------------- |
| 1   | DY-SV17F pin 9 (SPK+)  |
| 2   | DY-SV17F pin 10 (SPK-) |

### U1 — Pro Mini header pin connections

| Pin label | Net               |
| --------- | ----------------- |
| RAW       | `VSYS`            |
| GND (×2)  | `GND`             |
| D2        | `BTN_IN`          |
| D5        | `GATE_CTRL`       |
| D6        | `TRIG_OUT`        |
| D7        | `BUSY_IN`         |
| All other | NC                |

### U2 — DY-SV17F header pin connections

(Side / pin numbering — left/right as printed on the silkscreen, pin 1 at top.)

| Side / pin       | Label      | Net        |
| ---------------- | ---------- | ---------- |
| Right 1          | TX / IO0   | `TRIG_OUT` |
| Left 7           | CON3/BUSY  | `BUSY_IN` *and* `CON3` (via 10 kΩ pull-down) |
| Right 9          | GND        | `GND`      |
| Left 6           | V5         | `VDFP`     |
| Left 1           | SPK+       | J3.1       |
| Left 2           | SPK−       | J3.2       |
| Left 5           | V33        | `V33`      |
| Left 8           | CON2       | `CON2`     |
| Left 9           | CON1       | `CON1`     |

All other DY-SV17F pins (IO1-7, DACL, DACR) are NC.

**Mode configuration**: I/O Independent Mode 0. Set via:
- J8 shunt 1-2  → CON1 = GND
- J9 shunt 2-3  → CON2 = V33
- J10 unshunted, plus 10 kΩ pull-down R3 between CON3 and GND  → CON3 = GND at boot, BUSY output free afterwards

In Independent Mode 0, grounding IO0 plays `00001.mp3`. (Grounding IO1 would play `00002.mp3`, IO2 → `00003.mp3`, etc.) The real CON1/CON2/CON3 truth table is in `PINOUTS.md`.

## 5. Layout rules

Everything from `pcb/README.md` §6 still applies, plus:

- **PCB thickness: 2.0 mm.** Specify in JLCPCB / PCBWay order.
- **Solder modules through-hole, no sockets.** The Pro Mini gets pin
  headers (or naked pins) soldered to the PCB *and* to the module — solder
  joints on both sides of the PCB. Same for the DY-SV17F.
- **JST-XH connector orientation**: all three connectors on one edge of the
  board, with their wire-exit direction pointing toward where wires will
  enter the enclosure. This minimizes wire flexing inside the case.
- **No vias under the audio modules' speaker pads.** Keep speaker traces
  on top layer, 0.6 mm wide, pour-isolated from the GND plane only by the
  required clearance.
- **Pour GND plane on both layers.** Stitch with vias every 5 mm.
- **Fillet radius the corners of the board** (3 mm rounded corners) to
  reduce stress concentration if dropped on a corner.
- **Mounting holes**: 4× M3 NPTH at the corners, 6 mm keep-out, with
  solid copper rings on both layers (acts as a ground tie point and adds
  drop stiffness around the screws).
- **Test points**: VSYS, VDFP, PFET_GATE, BUSY_IN, GND.

## 6. Reliability checklist (the v2 actually-survives-kids list)

After the boards arrive and during assembly:

- [ ] PCB thickness measured, confirmed 2.0 mm
- [ ] Pro Mini soldered with pins through PCB **and soldered on both
      sides** (top and bottom of PCB)
- [ ] DY-SV17F soldered the same way
- [ ] Each electrolytic cap (C1, C4) has its leads bent 90° before soldering
      so the body sits flush; trim leads short after solder
- [ ] All three JST connectors locked in fully when populated; tug-test
      each pre-crimped wire
- [ ] All wires entering the enclosure have a hot-glue strain relief at
      the entry point
- [ ] PCB mounted on 4× M3 standoffs, **not** floating against the
      enclosure walls
- [ ] After full functional test, conformal-coat the populated board
      (mask the JST connectors, the SW1 actuator, and the SD-card slot
      areas first — actually no SD slot in v2, scratch that — and the
      Pro Mini's FTDI header end if you want to reflash later)
- [ ] Drop test from 1 m onto carpet before shipping to friend

## 7. Bring-up procedure

Same multimeter triage as v1 §9, with these additions specific to v2:

1. With Pro Mini and DY-SV17F unpopulated, confirm `VSYS` and `VDFP`
   gate as expected.
2. Populate Pro Mini, flash the v2 firmware (`v2/firmware/main.cpp`),
   confirm idle current < 1 mA before sleep, < 50 µA after sleep.
3. **Before populating DY-SV17F**, load audio onto it via USB:
   1. Connect a USB cable from PC to the DY-SV17F's USB pads (or use a
      programming jig if you have one).
   2. The module appears as a removable flash drive.
   3. Drop your `00001.mp3` file in the root (five-digit filename, per DY-SV17F datasheet).
   4. Eject and disconnect.
4. Populate DY-SV17F. Press the button. Audio should play within ~200 ms.
5. Measure peak current during playback at the battery: expect 100–200 mA
   spikes.

## 8. Firmware

In `v2/firmware/main.cpp`. ~60 lines, no library dependencies. Key
differences from v1:
- No SoftwareSerial, no DFPlayer library
- `playAudio()` is: power-up → pulse IO0 LOW → fixed playback delay → power-down
  (BUSY-readout variant available on builds with the 10 kΩ pull-down on CON3
  + D7=`INPUT_PULLUP`; the current main.cpp uses the fixed-delay variant
  with D7=`INPUT` to keep mode-select working on Kelly's no-resistor v2 board)

## 9. KiCad MCP servers — concrete options

You asked about installing one before fabricating. As of May 2026, three are
worth knowing about:

| Server                              | Scope                                                                                          | Install                            |
| ----------------------------------- | ---------------------------------------------------------------------------------------------- | ---------------------------------- |
| **`oaslananka/kicad-mcp-pro`**      | Broadest. Schematic + placement + routing (FreeRouting integration) + DRC/ERC + Gerber export. | `pip install kicad-mcp-pro`        |
| **`mixelpixx/KiCAD-MCP-Server`**    | Similar feature claims; ~900 stars; MCP 2025-06-18 spec compliant.                              | npm clone + build                  |
| **`Finerestaurant/kicad-mcp-python`** | Uses KiCad's official IPC-API. Narrower scope (PCB element manipulation, no schematic gen yet). | poetry install                     |

**Recommendation: `kicad-mcp-pro`.** It has the broadest feature surface and
a documented Claude Code config. Caveat I want to be honest about: I haven't
test-driven it against this specific design. The README promises more than
any community MCP server has delivered for me historically — treat its
placement and auto-routed traces as a *starting point*, then verify in the
KiCad GUI before exporting Gerbers.

Realistic workflow:

1. Install **KiCad ≥ 9** and enable the IPC API:
   `Preferences → Plugins → Enable IPC API Server`.
2. `pip install kicad-mcp-pro`. Add to `~/.claude.json` under
   `mcpServers`, with `KICAD_MCP_PROJECT_DIR` pointing to a new folder
   like `v2/kicad/` (don't commit kicad-generated binaries to the repo).
3. Have me drive the MCP server to enter the schematic from §4 and an
   initial PCB layout from §5.
4. **Open the result in KiCad's GUI manually.** Sanity-check placement,
   inspect every auto-routed trace, fix any DRC violations, do a 3D
   render to check for component-body collisions.
5. Export Gerbers (either via the MCP or `File → Plot` in the GUI).
6. Upload the zip to JLCPCB / PCBWay.

What the MCP saves: the ~1 hour of clicking to enter ~20 components and
their footprints. What it does *not* save: layout judgment, DRC
iteration, and the final pre-fab review. Plan for the second part.

References:
- [kicad-mcp-pro](https://github.com/oaslananka/kicad-mcp-pro)
- [mixelpixx/KiCAD-MCP-Server](https://github.com/mixelpixx/KiCAD-MCP-Server)
- [Finerestaurant/kicad-mcp-python](https://github.com/Finerestaurant/kicad-mcp-python)
