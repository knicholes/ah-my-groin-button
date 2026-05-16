# Ah! My Groin! — Custom PCB Design Spec

This directory is the source of truth for the fabricated PCB. Everything needed
to draw the schematic in KiCad, lay out the board, and export Gerbers that will
work on the first run is here. Anything in `circuit_diagrams.md`,
`perfboard_layout_guide.md`, or `SIMPLE_PERFBOARD_GUIDE.md` at the repo root is
older / perfboard-era and should not be used to spec the PCB.

## 1. Top-level decisions (locked in 2026-05-05)

| Decision        | Choice                                                           |
| --------------- | ---------------------------------------------------------------- |
| Power           | 3×AA holder, 4.5 V nominal, wired to a 2-pin terminal block      |
| MCU             | Arduino Pro Mini 3.3 V / 8 MHz (module on female headers)        |
| Audio           | DFPlayer Mini (module on female headers)                         |
| Button          | EG STARTS 100mm dome — microswitch only, LED unused, to terminal|
| Speaker         | External 8 Ω / 2 W, wired to a 2-pin terminal block              |
| Power switch    | Onboard SPDT slide switch (through-hole, 2.54 mm pitch)          |
| DFPlayer gating | High-side P-MOSFET driven by an NPN level shifter from D5        |
| Reverse-polarity| P-MOSFET in series with the battery+ rail                        |
| Board           | 2-layer, 1.6 mm FR4, HASL, ~60 × 50 mm, JLCPCB-class fab         |

## 2. The bug fixes baked into this design

These are the issues with the perfboard-era docs; the PCB design corrects them:

1. **DFPlayer Mini has no "Enable" pin.** Power-gating is done by a high-side
   P-MOSFET (Q1) on the DFPlayer's VCC, controlled via an NPN (Q3) level
   shifter from the Pro Mini's D5. D5-HIGH ⇒ DFPlayer powered; D5-LOW ⇒
   DFPlayer fully off. Software in `ah-my-groin/src/main.cpp` already drives
   D5 the right direction (`digitalWrite(DFPLAYER_ENABLE, HIGH)` to play).
2. **Bidirectional serial is required.** D3 → DFPlayer RX *and* D4 ← DFPlayer
   TX are both routed. The DFPlayer library calls into `dfPlayer.begin(...)`
   need the return path; the simple perfboard guide omitted it.
3. **3 V was below DFPlayer Mini's spec.** 3×AA gives 4.5 V nominal (3.3 V at
   end-of-life), comfortably inside the DFPlayer's 3.2–5.0 V window and giving
   the audio amp the headroom it needs. The Pro Mini's onboard MIC5205 LDO
   regulates 4.5 V → 3.3 V for the ATmega.

## 3. Net list

| Net          | Description                                                      |
| ------------ | ---------------------------------------------------------------- |
| `VBATT_RAW`  | Battery+ raw (J1.1, before switch and reverse-protection)        |
| `VBATT_SW`   | After SW1 (switched battery+, before reverse protection)         |
| `VSYS`       | System 4.5 V rail, after Q2 (powers Pro Mini RAW + Q1 source)    |
| `VDFP`       | DFPlayer VCC, after Q1 (gated by D5)                             |
| `PFET_GATE`  | Q1 gate / Q3 collector / R2 (gate-control mid-node)              |
| `GND`        | Battery− and system ground                                       |
| `BTN_IN`     | Pro Mini D2, internal pull-up enabled in firmware                |
| `SW_TX`      | Pro Mini D3 → (R4) → DFPlayer RX                                 |
| `SW_RX`      | Pro Mini D4 ← DFPlayer TX                                        |
| `GATE_CTRL`  | Pro Mini D5 → R1 → Q3 base                                       |

## 4. Components (see `bom.csv` for part numbers)

| Ref  | Part                                  | Footprint (KiCad lib)                                            |
| ---- | ------------------------------------- | ---------------------------------------------------------------- |
| U1   | Arduino Pro Mini 3.3 V / 8 MHz module | 2× `PinSocket_1x12_P2.54mm_Vertical` (Connector_PinSocket_2.54mm)|
| U2   | DFPlayer Mini module                  | 2× `PinSocket_1x8_P2.54mm_Vertical`  (Connector_PinSocket_2.54mm)|
| Q1   | AO3401A P-MOSFET (DFPlayer gate)      | `SOT-23` (Package_TO_SOT_SMD)                                    |
| Q2   | AO3401A P-MOSFET (reverse polarity)   | `SOT-23`                                                         |
| Q3   | MMBT3904 NPN BJT                      | `SOT-23`                                                         |
| R1   | 10 kΩ ±1 % 0805                       | `R_0805_2012Metric` (Resistor_SMD)                               |
| R2   | 100 kΩ ±1 % 0805                      | `R_0805_2012Metric`                                              |
| R4   | 1 kΩ ±1 % 0805                        | `R_0805_2012Metric`                                              |
| C1   | 1000 µF / 10 V electrolytic           | `CP_Radial_D10.0mm_P5.00mm` (Capacitor_THT)                      |
| C2   | 10 µF X5R 0805                        | `C_0805_2012Metric` (Capacitor_SMD)                              |
| C3   | 0.1 µF X7R 50 V 0805                  | `C_0805_2012Metric`                                              |
| C4   | 100 µF / 10 V electrolytic            | `CP_Radial_D6.3mm_P2.50mm`                                       |
| C5   | 0.1 µF X7R 50 V 0805                  | `C_0805_2012Metric`                                              |
| C6   | 10 µF X5R 0805                        | `C_0805_2012Metric`                                              |
| SW1  | E-Switch EG1218 SPDT slide (or equiv) | `SW_Slide_1P2T_CK_OS102011MS2QN1` or vendor footprint            |
| J1   | Battery 2-pin terminal, 3.5 mm pitch  | `TerminalBlock_Phoenix_MPT-0,5-2-3.5_1x02_P3.50mm_Horizontal`    |
| J2   | Button 2-pin terminal, 3.5 mm pitch   | same                                                             |
| J3   | Speaker 2-pin terminal, 3.5 mm pitch  | same                                                             |

DFPlayer Mini does **not** ship in KiCad's stock symbol/footprint libraries.
Two clean ways to add it:
- SnapEDA: search "DFPlayer Mini" → download symbol+footprint, drop into a
  project-local library.
- Or roll your own: 2× 1×8 0.1″ female sockets, 16-pin total, body 20.4 × 21.6 mm,
  header pitch 2.54 mm, header rows spaced 17.78 mm (700 mil) apart.

Pro Mini *is* in KiCad's stock library (`MCU_Module:Arduino_Pro_Mini`) but only
as a symbol; the standard 2× 1×12 footprint above is what you actually need.

## 5. Connection table (the schematic, exhaustively)

### J1 — Battery terminal block

| Pin | Net          |
| --- | ------------ |
| 1   | `VBATT_RAW`  |
| 2   | `GND`        |

### SW1 — SPDT slide switch (used as SPST: ON / OFF)

| Pin | Net          |
| --- | ------------ |
| 1 (common)         | `VBATT_RAW`  |
| 2 (throw 1, "ON")  | `VBATT_SW`   |
| 3 (throw 2, "OFF") | NC           |

### Q2 — AO3401A reverse-polarity P-MOSFET

| Pin    | Net         |
| ------ | ----------- |
| 1 G    | `GND`       |
| 2 D    | `VSYS`      |
| 3 S    | `VBATT_SW`  |

Operation: when the user inserts cells correctly, V<sub>GS</sub> = 0 − 4.5 = −4.5 V → ON.
Insert reversed and V<sub>GS</sub> swings positive; FET stays off and the body
diode is also reverse-biased — load is disconnected, nothing fries.

### Q1 — AO3401A DFPlayer gate P-MOSFET

| Pin    | Net          |
| ------ | ------------ |
| 1 G    | `PFET_GATE`  |
| 2 D    | `VDFP`       |
| 3 S    | `VSYS`       |

### Q3 — MMBT3904 NPN level shifter

| Pin    | Net          |
| ------ | ------------ |
| 1 B    | (R1 → D5)    |
| 2 E    | `GND`        |
| 3 C    | `PFET_GATE`  |

### R1 — 10 kΩ (NPN base resistor)

`GATE_CTRL` ↔ Q3 base. Limits Pro Mini source current to ~0.3 mA.

### R2 — 100 kΩ (P-MOSFET gate pull-up)

`VSYS` ↔ `PFET_GATE`. Holds Q1 OFF when Q3 is OFF (sleep).

### R4 — 1 kΩ (DFPlayer RX series)

Pro Mini D3 ↔ DFPlayer pin 2 (RX). Belt-and-suspenders against bus contention
during boot/upload; harmless at 9600 baud.

### Decoupling

| Cap | From   | To    | Place near                          |
| --- | ------ | ----- | ----------------------------------- |
| C1  | `VSYS` | `GND` | Q2 drain / battery input            |
| C2  | `VSYS` | `GND` | Pro Mini RAW pin                    |
| C3  | `VSYS` | `GND` | Pro Mini RAW pin (same area as C2)  |
| C4  | `VDFP` | `GND` | DFPlayer VCC pin                    |
| C5  | `VDFP` | `GND` | DFPlayer VCC pin (same area as C4)  |
| C6  | `VDFP` | `GND` | DFPlayer VCC pin (same area as C4)  |

C1 (1000 µF) absorbs speaker transients on the battery rail and helps damp
the WWZMDiB clone's idle-hiss; C4 (100 µF) + C6 (10 µF) hold up VDFP during
the ~150 mA audio current spikes.

### J2 — Button terminal block

| Pin | Net       |
| --- | --------- |
| 1   | `BTN_IN`  |
| 2   | `GND`     |

Pro Mini's internal pull-up holds D2 high; the button shorts to GND, ISR fires
on FALLING edge.

**Wire the EG STARTS button's 4.8 mm spade terminals only** — those are the
microswitch (`COM` and `NO`). `COM` → J2.2 (`GND`), `NO` → J2.1 (`BTN_IN`).
The two 6.3 mm spade terminals are the 12 V LED — leave them unconnected, the
LED is not driven from this board.

### J3 — Speaker terminal block

| Pin | Net (DFPlayer pin)     |
| --- | ---------------------- |
| 1   | DFPlayer pin 8 (SPK_1) |
| 2   | DFPlayer pin 6 (SPK_2) |

**SPK_1 and SPK_2 are bridge-tied — never tie either to GND.**

### U1 — Pro Mini header pin connections

(Standard SparkFun / clone Pro Mini, 2× 1×12 single-row layout. Pin numbering
below is by silkscreen label, not header position.)

| Pin label | Net                              |
| --------- | -------------------------------- |
| RAW       | `VSYS`                           |
| GND (×2)  | `GND`                            |
| VCC       | (no connect or test point only)  |
| RST       | (no connect)                     |
| TXO (D1)  | (no connect)                     |
| RXI (D0)  | (no connect)                     |
| D2        | `BTN_IN`                         |
| D3        | (R4) → `SW_TX`                   |
| D4        | `SW_RX`                          |
| D5        | `GATE_CTRL`                      |
| D6–D13    | (no connect, optional test pads) |
| A0–A7     | (no connect)                     |

Layout note: place U1 with its FTDI 6-pin end (DTR, TXO, RXI, VCC, GND, GND)
overhanging the board edge so an FTDI cable can plug in without removing the
module.

### U2 — DFPlayer Mini header pin connections

Pin numbers per DFRobot DFR0299 datasheet (1–8 on one row, 9–16 on the other).

| Pin | Label    | Net              |
| --- | -------- | ---------------- |
| 1   | VCC      | `VDFP`           |
| 2   | RX       | `SW_TX` (via R4) |
| 3   | TX       | `SW_RX`          |
| 4   | DAC_R    | NC               |
| 5   | DAC_L    | NC               |
| 6   | SPK_2    | J3.2             |
| 7   | GND      | `GND`            |
| 8   | SPK_1    | J3.1             |
| 9   | IO_1     | NC               |
| 10  | GND      | `GND`            |
| 11  | IO_2     | NC               |
| 12  | ADKEY_1  | NC               |
| 13  | ADKEY_2  | NC               |
| 14  | USB+     | NC               |
| 15  | USB-     | NC               |
| 16  | BUSY     | NC (optional test pad) |

## 6. Layout rules

- **2 layers.** Top = signal + parts, bottom = ground pour. Stitch grounds
  with vias every 5–10 mm in the pour.
- **Ground pour on both layers**, hatched-or-solid, tied at every component's
  GND pin and at all four mounting holes (which are non-plated, M3, in the
  corners).
- **Trace widths**:
  - Power (`VSYS`, `VDFP`, `GND` returns from speaker / DFPlayer): 0.6 mm minimum
  - Battery feed (J1 → SW1 → Q2 → C1): 1.0 mm
  - Signal (`SW_TX`, `SW_RX`, `BTN_IN`, `GATE_CTRL`): 0.25 mm
- **Clearance**: 0.2 mm minimum (JLCPCB economy).
- **Vias**: 0.6 mm OD / 0.3 mm drill default; size up power vias to 0.8 / 0.4.
- **Speaker traces** (DFPlayer SPK_1/SPK_2 → J3): keep both traces parallel
  and short, 0.5 mm width, away from the SoftwareSerial pair.
- **Decoupling placement**: C2/C3 within 5 mm of Pro Mini RAW. C4/C5/C6 within
  5 mm of DFPlayer VCC. C1 within 10 mm of Q2 drain.
- **Q3 placement**: between Q1 and the Pro Mini D5 pin, NPN base resistor
  R1 right at the Pro Mini side.
- **Q2 placement**: right at J1, before SW1 in the path. (Switch sees raw
  battery so reversed cells with the switch ON still don't damage anything;
  Q2 blocks before the load.)
- **Test-point pads**: drop a labeled 1.5 mm round pad on each of `VBATT_SW`,
  `VSYS`, `VDFP`, `GATE_CTRL`, `GND` for bring-up multimetering.
- **Mounting holes**: 4× M3 non-plated, 3.2 mm drill, 6 mm keep-out, in the
  corners.
- **Silkscreen**: label every connector with what plugs into it
  ("BATTERY +/−", "BUTTON", "SPEAKER"), and put a polarity ⊕ next to J1.1.
  This is the kind of mistake a tired user makes once.
- **Edge clearance**: 0.5 mm component-to-edge minimum.

## 7. KiCad workflow (what to actually do in the GUI)

1. `kicad-cli` is fine for Gerber export but **drawing the board has to happen
   in the GUI.** Open KiCad ≥ 7.0.
2. New project: `pcb/ah-my-groin.kicad_pro` (this directory).
3. **Schematic** (`Eeschema`):
   1. Import the DFPlayer Mini symbol+footprint from SnapEDA into a
      project-local lib at `pcb/lib/dfplayer.kicad_sym` and
      `pcb/lib/dfplayer.pretty/`.
   2. Place all symbols from §4. Wire per the connection table in §5.
   3. Annotate (Tools → Annotate Schematic).
   4. Run **ERC**. Expected: zero errors, zero warnings — except possibly
      "no-connect" flags on intentionally-unused module pins, which you
      should explicitly mark with the `No Connection` flag instead of leaving
      floating.
   5. Assign footprints (Tools → Assign Footprints) per the table in §4.
4. **PCB** (`Pcbnew`):
   1. Update PCB from schematic.
   2. Set board outline to a 60 × 50 mm rectangle on `Edge.Cuts` (or whatever
      fits your enclosure — just keep the connectors on one edge).
   3. Place per §6.
   4. Route signal, then power. Keep the SoftwareSerial pair together and
      short (< 30 mm).
   5. Pour GND on F.Cu and B.Cu, both connected to the GND net.
   6. Run **DRC**. Fix every error and every warning. Don't ship with DRC
      warnings — JLCPCB won't catch them and you'll get exactly what you sent.
5. **3D check** (View → 3D Viewer): rotate the board, confirm no part bodies
   collide and that the Pro Mini's FTDI end is accessible.
6. **Export Gerbers**:
   - File → Plot. Layers: F.Cu, B.Cu, F.Mask, B.Mask, F.SilkS, B.SilkS,
     F.Paste, B.Paste, Edge.Cuts. Format: Gerber. Use Protel filename
     extensions: ON. Plot.
   - File → Fabrication Outputs → Drill Files. Format: Excellon. Drill
     Origin: Absolute. Units: mm. PTH and NPTH in separate files.
7. **Bundle**: zip the `gerbers/` and `drill/` outputs together. Upload to
   JLCPCB / PCBWay.

## 8. Pre-fab verification checklist

Run through this **before** you click "place order":

- [ ] ERC clean
- [ ] DRC clean (zero warnings, zero errors)
- [ ] Every net in §3 exists in the schematic and is connected to every
      component listed for it
- [ ] BOM in `bom.csv` matches every reference designator on the board
- [ ] Q1 source = `VSYS`, drain = `VDFP` (not reversed)
- [ ] Q2 source = `VBATT_SW`, drain = `VSYS` (not reversed)
- [ ] Q3 collector goes to PFET_GATE, emitter to GND (not reversed — common
      mistake with SOT-23 BJT pinout vs MOSFET pinout)
- [ ] DFPlayer SPK_1 and SPK_2 land on J3, neither tied to GND
- [ ] J1 silkscreen shows ⊕ on pin 1 (`VBATT_RAW`)
- [ ] Pro Mini RAW pin connects to `VSYS`, *not* `VBATT_RAW` (the switch is
      between them)
- [ ] FTDI end of Pro Mini overhangs board edge or is otherwise accessible
- [ ] 4× M3 mounting holes present
- [ ] Gerber zip opens cleanly in an online viewer (e.g. JLCPCB's preview)
      and shows the full board, not a fragment
- [ ] Drill file is included in the zip

## 9. Bring-up procedure (after boards arrive)

Build one board. Don't populate the modules yet.

1. Apply 4.5 V across J1 with current limit set to 100 mA. With SW1 OFF,
   confirm zero current. Flip SW1 ON; expect tens of µA.
2. Reverse the bench supply leads on J1. Confirm current stays near zero
   and `VSYS` stays at 0 V (Q2 doing its job). Restore correct polarity.
3. With Pro Mini and DFPlayer module sockets still empty, measure `VSYS`
   at the test point: should read battery voltage − a few mV (Q2 R<sub>DS(on)</sub>).
4. Probe `PFET_GATE` to GND: should read ~`VSYS` (R2 holding Q1 off).
   Measure `VDFP`: should be 0 V.
5. Tack a wire from `GATE_CTRL` to `VSYS`. `PFET_GATE` should drop to
   near 0 V (Q3 saturated), and `VDFP` should rise to within ~50 mV of
   `VSYS`. Remove wire.
6. Plug the Pro Mini in. Power on. Pro Mini's onboard 3.3 V LED should
   light. Idle current ≈ 5–10 mA before sleep, < 1 mA after.
7. Plug the DFPlayer in (with formatted SD card containing `/0001.mp3`).
   Press button → expect audio.

If any step fails, see the test-point voltages first; the design is
intentionally easy to triage with a multimeter.

## 10. Notes that will bite you if ignored

- **DFPlayer SD-card requirements**: FAT32, file named exactly `0001.mp3`
  (or place it in a `/mp3` folder as `/mp3/0001.mp3` if you call
  `dfPlayer.playMp3Folder(1)` instead of `dfPlayer.play(1)`). SanDisk cards
  are the most reliable; many no-name cards will silently not play.
- **Pro Mini power LED**: leave the firmware comment about removing the LED
  in `circuit_diagrams.md`; that LED draws ~3 mA continuous and undoes a lot
  of the deep-sleep work in `main.cpp`. Desolder it before final assembly.
- **Pin 5 polarity**: firmware drives D5 HIGH to *power on* the DFPlayer.
  If you ever swap the gate topology (e.g. drop the NPN, drive Q1 gate
  directly), you'll invert the polarity and audio will play in sleep
  instead of when the button is pressed. Don't do that without updating
  `DFPLAYER_ENABLE` semantics in firmware.
- **Reverse-polarity FET is on the battery+ side, before the switch**:
  meaning if SW1 is OFF and a user reversed the cells, no protection is
  active because no current is flowing anyway. This is fine — protection
  only matters when current *would otherwise* flow.

## 11. Purchased-component quirks (verify on receipt)

These are the *specific* parts the user bought, not generics. Each has a
known issue that's easier to catch before populating than after.

### U1 — HiLetgo Pro Mini 3.3V/8MHz (Amazon B07RS911JD, 3-pack)
- **Verify the crystal before soldering anything.** A recurring complaint on
  this listing is that some units ship with a **16 MHz crystal** soldered
  onto the 3.3 V board. ATmega328P is out of spec at 16 MHz / 3.3 V — it'll
  appear to work on the bench and fail intermittently in the field. Eyeball
  the crystal can: it must read `8.000` (not `16.000`).
- Bootloader is pre-installed. Program via FTDI cable on the 6-pin header.
- Power LED on the board draws ~3 mA continuous; desolder it before final
  assembly to preserve the deep-sleep gains in `main.cpp`.

### U2 — WWZMDiB Mini MP3 Module (Amazon B0CH2WZT5Q, 5-pack)
This is almost certainly an MH2024K-24SS clone (the slowest/fussiest
DFPlayer variant per Garry's Blog characterization). Plan accordingly:
- **Bench-test each unit before soldering it down.** Reported DOA / smoking
  rates on this listing are non-trivial — one experienced reviewer had
  5/5 fail and 2 smoke. Apply 4.5 V to a unit on a breadboard, send it a
  play command, and confirm audio out before committing it to the PCB.
- **Audio file must be `.mp3`, not `.wav`.** The MH2024K clone does not
  reliably decode WAV. The comment at the top of `ah-my-groin/src/main.cpp`
  says `0001.wav` — that has to become `0001.mp3` on the SD card. (No code
  change needed; `dfPlayer.play(1)` selects by track index, not filename.)
- **Allow ~2 seconds between commands in firmware.** Faster sequences
  silently drop commands on this clone. `main.cpp` only issues one
  `play()` per button press, so this is fine for current behavior — but
  don't add fancier sequencing without padding the gaps.
- **Volume command may be ignored** — the MH2024K is known to play at max
  volume regardless of `setVolume()`. If output is too loud, mitigate with
  speaker selection, not software.
- **Polarity: SPK_1 (pin 8) = positive, SPK_2 (pin 6) = negative.** The
  schematic table in §5 is correct; just don't second-guess it during
  assembly.
- SD card: FAT32, SanDisk preferred. Place `0001.mp3` directly in the root
  (matches the `play(1)` call in firmware).

### BTN — EG STARTS 100mm Big Dome (Amazon B01LZMANZ7)
- **Two terminal pairs on the back, do not confuse them.** The 4.8 mm
  spades are the microswitch (`COM` + `NO`); these are what we wire to J2.
  The 6.3 mm spades are the LED, **rated for 12 V** with an internal
  current-limiting resistor sized for 12 V. Running it from the 4.5 V rail
  would not light it; we're not driving the LED at all by design choice.
- Microswitch is voltage-independent (mechanical contact), works fine on
  the 3.3 V Pro Mini logic level with the internal pull-up.
- Mounting hole: ~100 mm panel cutout. Confirm the enclosure has space
  before drilling.
