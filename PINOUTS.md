# Correct module pinouts — reference for v3 PCB re-spin

The v2 PCB (`kicad/ahmygroin.kicad_pcb`) has multiple footprint/routing bugs around U1 (Pro Mini) and U2 (DY-SV17F) that I (Claude) introduced. The hand-wire workaround for the existing v2 boards is in `SOLDERING_GUIDE.md` → *Hardware erratum* section. **This file is the source of truth for what a corrected v3 layout must do.**

If anything below disagrees with `v2/README.md`, `v2/bom.md`, or the v2 .kicad_sch / .kicad_pcb, this file wins. Those files were written before the bugs were identified.

Verified against the physical modules by user Kelly on 2026-05-19. If you re-verify against a new module revision and find a discrepancy, update this file and bump the revision date.

---

## U1 — Arduino Pro Mini 3.3 V / 8 MHz (HiLetgo, Amazon B07RS911JD)

**Form factor:** Two parallel 1 × 12 long-edge solder pads on 0.1″ (2.54 mm) pitch, plus a 1 × 6 FTDI programming header on one short edge. Long-edge row spacing **15.24 mm (0.6″)** centre-to-centre.

**Orientation convention:** "top" = the FTDI short-edge end of the module. "Left" and "right" are as seen looking down at the component side of the module, FTDI at the top.

### Left long edge (top to bottom)

| # | Pad label (silkscreen) | Arduino name | v2/v3 net | Notes |
|---|---|---|---|---|
| 1 | `TXO` / `TX1` | D1 | — | Unused. Also accessible on FTDI header. |
| 2 | `RXI` / `RX0` | D0 | — | Unused. Also accessible on FTDI header. |
| 3 | `RST` | RESET | — | Unused. Also accessible on FTDI header. |
| 4 | `GND` | GND | **/GND** | Required. |
| 5 | `2` | D2 | **/BTN_IN** | Required. INT0 button input. |
| 6 | `3` | D3 | — | Unused in v2 firmware. |
| 7 | `4` | D4 | — | Unused in v2 firmware. |
| 8 | `5` | D5 | **/GATE_CTRL** | Required. NPN base via R1 → P-FET gate. |
| 9 | `6` | D6 | **/TRIG_OUT** | Required. **Idles LOW** (not HIGH — see *Phantom power* below); driven HIGH just before the power gate opens, then pulsed LOW to trigger DY-SV17F IO0, then returned LOW after the gate closes. |
| 10 | `7` | D7 | **/BUSY_IN** | Required. Reads DY-SV17F BUSY (LOW during playback). Firmware must set this as plain `INPUT` (no pullup) — see CON3 note in U2 table. |
| 11 | `8` | D8 | — | Unused. |
| 12 | `9` | D9 | — | Unused. |

### Right long edge (top to bottom)

| # | Pad label (silkscreen) | Arduino name | v2/v3 net | Notes |
|---|---|---|---|---|
| 1 | `RAW` | VIN | **/VSYS** | Required. Battery feed after Q3 reverse-polarity FET. |
| 2 | `GND` | GND | /GND (optional) | Can also use this GND instead of left pin 4. |
| 3 | `RST` | RESET | — | Mirror of left pin 3. |
| 4 | `VCC` (sometimes printed `V3.3`, `ACC`, `+3.3`) | VCC | **/V33_MCU** (was `/V33` through v3.1 — **bug**) | 3.3 V output of the Pro Mini's onboard regulator. This rail is **always on**. It must NOT be bonded to the module's `V33` pin or to the mode-select jumper rail — doing so phantom-powers the gated module. See *Phantom power* below. |
| 5 | `A3` | A3 / D17 | — | Unused. |
| 6 | `A2` | A2 / D16 | — | Unused. |
| 7 | `A1` | A1 / D15 | — | Unused. |
| 8 | `A0` | A0 / D14 | — | Unused. |
| 9 | `13` | D13 (LED) | — | Unused. On-board LED. |
| 10 | `12` | D12 | — | Unused. |
| 11 | `11` | D11 | — | Unused. |
| 12 | `10` | D10 | — | Unused. |

### FTDI 6-pin programming header (short edge)

Standard SparkFun convention, pin 1 closest to the corner of the board nearest TXO:

| # | Pad label | Net (for in-circuit FTDI cable use) |
|---|---|---|
| 1 | `GND` | /GND |
| 2 | `CTS` (or another `GND` on some clones) | /GND |
| 3 | `VCC` | (driven by FTDI cable at 3.3 V; same net as right-edge pin 4) |
| 4 | `RXI` | (FTDI TX → Pro Mini RX) |
| 5 | `TXO` | (Pro Mini TX → FTDI RX) |
| 6 | `DTR` | (used for auto-reset on flash) |

The FTDI header is **not** wired to the PCB in any version — the Pro Mini is meant to be programmed by plugging an FTDI cable directly onto these pins while the Pro Mini is socketed on the carrier PCB. The header overhangs the top edge of the carrier PCB.

---

## U2 — DY-SV17F audio module (Amazon B0BPSPPW52, 2-pack)

**Form factor:** Two parallel 1 × 9 long-edge solder pads on **2.5 mm metric pitch** (not 2.54 mm/0.1″). DIP-18 outline. Long-edge row spacing **20.5 mm** pad-center to pad-center. Outer board ≈ 26 × 23 mm (user-calipered 2026-05-20: 26.3 × 23.08 mm).

**Orientation convention:** "top" = the end of the module nearest the USB/microSD/SPK terminals (refer to the silkscreen "DY-SV17F" text orientation; pin 1 is at top-left when the text is upright). "Left" and "right" are as seen looking down at the component side.

### Left long edge (top to bottom)

| # | Pad label (silkscreen) | Function | v2/v3 net | Notes |
|---|---|---|---|---|
| 1 | `SPK+` | Speaker output + | **/SPK_P** | Required. Drives J3 pin 1. |
| 2 | `SPK-` | Speaker output − | **/SPK_N** | Required. Drives J3 pin 2. |
| 3 | `DACL` | Line-level DAC output (left ch.) | — | Unused for this build. |
| 4 | `DACR` | Line-level DAC output (right ch.) | — | Unused. |
| 5 | `V33` | 3.3 V output (internal regulator) | **/V33** | This is an **output**, and it is dead whenever Q1 has the module gated off. That is exactly what makes it the correct reference for the mode-select jumper rail. It must **not** be tied to the Pro Mini's `VCC` (two regulator outputs back-driving each other, plus phantom power — see below). |
| 6 | `V5` | 5 V power input | **/VDFP** | Required. Gated by Q1 P-FET from VSYS. |
| 7 | `CON3` / `BUSY` | Mode select pin 3 / BUSY output | **/BUSY_IN** *and* **/CON3** | Required. Dual-purpose: sampled at boot for mode selection (first ~30 ms after power-on), then drives BUSY low during playback. In v3, biased LOW via a **10 kΩ pull-down resistor (R3) to GND** so the chip samples Independent Mode 0 at boot, while the push-pull BUSY output can still drive the line HIGH afterward. **Firmware must keep D7 as `INPUT` (no internal pullup) — a pullup here fights the boot-time pull-down and selects the wrong mode.** |
| 8 | `CON2` | Mode select pin 2 | **/CON2** | Required, and must be HIGH for Independent Mode 0. Its HIGH reference must be the **module's own `V33` output**, never an always-on rail — see *Phantom power* below. |
| 9 | `CON1` | Mode select pin 1 | **/CON1** | Required. Set HIGH or LOW via J8 jumper. |

### Right long edge (top to bottom)

| # | Pad label (silkscreen) | Function | v2/v3 net | Notes |
|---|---|---|---|---|
| 1 | `TX` / `IO0` | UART TX / IO trigger 0 | **/TRIG_OUT** | Required. **Trigger input.** Firmware pulses this LOW for ≥20 ms to start playback of `00001.mp3`. (In Independent Mode 0, each IO pin plays one fixed track: IO0 → 00001, IO1 → 00002, …) |
| 2 | `RX` / `IO1` | UART RX / IO trigger 1 | — | Unused. Would play `00002.mp3` if grounded. |
| 3 | `IO2` | IO trigger 2 | — | Unused. |
| 4 | `IO3` | IO trigger 3 | — | Unused. |
| 5 | `ONE_LINE` / `IO4` | One-line serial / IO trigger 4 | — | Unused. |
| 6 | `IO5` | IO trigger 5 | — | Unused. |
| 7 | `IO6` | IO trigger 6 | — | Unused. |
| 8 | `IO7` | IO trigger 7 | — | Unused. |
| 9 | `GND` | Ground | **/GND** | Required. |

### Mode configuration for "pulse IO0 LOW → play 00001.mp3 once, then idle"

The real DY-SV17F mode-select truth table (CON1, CON2, CON3 sampled during the first ~30 ms after V5/V33 come up):

| CON1 | CON2 | CON3 | Mode |
|------|------|------|------|
| GND  | GND  | GND  | I/O Integrated Mode 0 |
| GND  | GND  | V33  | UART |
| V33  | GND  | GND  | I/O Integrated Mode 1 |
| V33  | GND  | V33  | Standard MP3 (key-control: NEXT/PREV/PLAY/EQ/RPT on IO0-4) |
| GND  | V33  | GND  | **I/O Independent Mode 0** ← what this build uses |
| V33  | V33  | GND  | I/O Independent Mode 1 |

(Source: DY-SV17F datasheet via Electropeak's interface guide, verified empirically on Kelly's module on 2026-06-07. The original PINOUTS.md table here was wrong — see [[dy-sv17f-mode-select]] memory.)

In **I/O Independent Mode 0**, each IO pin is wired to one fixed track: IO0 plays `00001.mp3`, IO1 plays `00002.mp3`, etc. Pulse the chosen pin LOW for ≥20 ms to play. Pin going back HIGH lets the current track finish; the module stops on its own.

| Pin | State at boot | How achieved on v3 |
|---|---|---|
| CON1 | GND  | J8 shunt across pads 1↔2 |
| CON2 | V33  | J9 shunt across pads 2↔3 |
| CON3 | GND  | 10 kΩ pull-down resistor (R3) to GND. J10 left unshunted so it can also be used to override the mode during bring-up. |

The on-board J8/J9/J10 jumpers (3-pin selectors, layout `GND / CON_x / V33`) must connect via the v3 PCB traces to the corresponding DY-SV17F CON pins. **In v2 these traces are missing — the CON nets exist only at the jumpers, not at the U2 footprint.**

### Phantom power — the rule that governs every line into the module (2026-07)

**Rule: while Q1 has the module gated off, every DY-SV17F pin driven by the Pro Mini must be at 0 V.**

Every CMOS input has protection diodes to its own supply rail. Put a voltage on an input pin of a chip whose supply is at 0 V, and current flows *in through that pin*, through the diode, and onto the internal rail. The chip half-wakes at about one diode drop below the feeding voltage and sits there in permanent brown-out, drawing real current while appearing to be "off". That is phantom power, and the v2/v3.1 design has two paths for it:

| Path | Mechanism | Fix |
|---|---|---|
| **IO0** (`/TRIG_OUT`, Pro Mini D6) | Firmware idled D6 HIGH at 3.3 V into the unpowered module's trigger input. | Firmware idles D6 **LOW**; raises it HIGH only in the window between the gate opening and the trigger pulse. |
| **CON2** (`/CON2`, via J9 pads 2–3) | The jumper's V33 rail was fed from the Pro Mini's always-on `VCC`, so CON2 sat at 3.3 V forever. | Reference CON2 to the **module's own `V33` output pin**, which collapses to 0 V when the gate closes. |

Measured on Kelly's built v2 board, 2026-07:

| Condition | Idle current |
|---|---|
| As built (both phantom paths live, both LEDs still fitted) | 14.44 mA |
| Both Pro Mini LEDs removed | 12.95 mA |
| Both phantom paths closed + firmware `sleep_bod_disable()` + unused pins pulled up | **0.15 mA** |

That is a ~86× reduction — from about a week on 3×AA to roughly 18–24 months at 2–3 presses/day.

Diagnostic fingerprints, so this is recognisable next time:

* The module's `V5` pin reads ~2.5 V while the module is supposed to be off (3.3 V in, minus a diode drop).
* Lifting the module's `GND` wire makes several mA vanish — proof current is entering somewhere other than `V5`.
* Lifting `IO0` makes the current go *up*, not down: the pin floats LOW, which in Independent Mode 0 means "play", so the half-powered chip keeps trying to start.
* Periodic faint clicking with no button press = the module brown-out retry looping.

**Cold-boot consequence.** A phantom-powered module is pre-warmed, so it responds to a trigger almost instantly. Once phantom power is removed it boots genuinely from 0 V and needs time to bring up its internal regulator and read flash. `BOOT_MS` in `v2/firmware/main.cpp` was 50 ms and worked only by accident; it is now **1000 ms**. If you ever fix a phantom-power path and playback goes silent, this is why — the trigger pulse is landing before the module is awake.

**Netlist change — DONE in v3.2 (`build_v3.py`, 2026-07-25).** The old `/V33` net is split in two:

* `/V33_MCU` — Pro Mini `VCC` (right-edge pad 4) only. Always on. Goes nowhere near the module.
* `/V33` — the module's `V33` output pin (left-edge pad 5) and J8/J9/J10 pad 3 only. Gated, because it collapses when Q1 closes.

Nothing else consumes the jumper rail: CON1 is strapped to GND (J8 pads 1–2) and CON3 uses the R3 pull-down, so CON2 is the only load on `/V33`. The split was free.

`kicad/verify_v3.py` asserts this permanently — it fails the build if `J5.4` ever reappears on `/V33`, or if `J6.5` (the module's own V33 output) ever leaves it. Do not "simplify" these back into one net.

### USB / file loading

The DY-SV17F has on-board 4 MB SPI flash that enumerates as a USB mass-storage device when the module is connected to a PC. Load `00001.mp3` (five-digit filename, per datasheet) to the root of the drive. No microSD card.

**Warning:** plugging USB into the DY-SV17F while the module is also installed in the PCB will back-feed the V33 rail through the module's internal 3.3 V LDO and power the Pro Mini. This is harmless but means the Pro Mini's status LED will come on without the battery — don't confuse that for actual battery-on behaviour during bring-up.

USB-side pads on the module: separate from the long-edge pins, on the short edge near the USB connector cutout. Not routed through the carrier PCB in v2 or planned for v3.

---

## v2 → v3 design changes (all FIXED in v3 by `kicad/build_v3.py`, 2026-05-20)

The v2 PCB had six layout bugs that prompted the v3 re-spin. All structural fixes are now in `kicad/ahmygroin.kicad_pcb`:

1. **DY-SV17F footprint:** changed from 2 × 8 / 17.78 mm to **2 × 9 / 20.5 mm row pitch / 2.5 mm pin pitch**. (Stock library has only 2.54 mm pitch; `kicad/build_v3.py` overrides each pad position to the true 2.5 mm metric at build time.) Pad assignments per the U2 tables above.
2. **DY-SV17F net routing:** J6 (left side) carries `/SPK_P`, `/SPK_N`, `/V33`, `/VDFP`, `/BUSY_IN`, `/CON1`, `/CON2`; J7 (right side) carries `/TRIG_OUT` on **pad 1 (IO0)** and `/GND` on pad 9. Old fabricated J7 assignments (`/VDFP` on pad 2, etc.) are discarded.
3. **CON1/CON2/CON3 traces:** in v3 the schematic netlist connects J8/J9/J10 middle pins to the J6 footprint pads 9, 8, 7 (these connections were missing entirely in v2). Trace routing is left to the autorouter — see "Routing" below.
7. **CON3 mode-select pull-down (NEW for v3.1, 2026-06-07):** add 10 kΩ resistor R3 between `/CON3` (= `/BUSY_IN`) and GND, so the module samples CON3=LOW during boot mode-detect. Without this, the chip's mode is undefined and our v2 board only works by accident.
8. **TRIG_OUT lands on IO0, not IO1 (FIX for v3.1, 2026-06-07):** the original v3 had `/TRIG_OUT` on J7 pad 2 (= module RX/IO1). In Independent Mode 0 that pin plays 00002.mp3, not 00001.mp3. Moved to J7 pad 1 (= module TX/IO0).
4. **Pro Mini J5 power pins:** `/VSYS` now lives on J5 pad 1 (RAW) and `/V33` on J5 pad 4 (VCC). Old pad 11/12 assignments (D10/D11) are cleared.
5. **C4 placement:** moved from (60, 14) to (50, 40) — south of the DY-SV17F footprint, clear of the module body.
6. **J1 / J3 polarity silkscreen:** `+`/`−` text labels added next to pad 1 and pad 2 on the battery (J1) and speaker (J3) JST-XH connectors.

Plus: **TP1** test point added on the `/V33` net (between C2 and Q1, labeled "V33" on the silkscreen).

## v3.2 build pipeline (fully scripted, 2026-07-25)

Three scripts, run in order, all headless. Use **KiCad's bundled Python**, not a
system one — `pcbnew` is only importable from there:

```
K = "K:\Program Files\KiCad\10.0\bin\python.exe"

& $K kicad\build_v3.py      # footprints, nets, placements, GND zones, silkscreen
& $K kicad\route_v3.py      # DSN -> Freerouting -> SES -> import -> fill zones
& $K kicad\verify_v3.py     # the pre-fab gate; exit 0 = safe to fab
```

`build_v3.py` deliberately produces an **unrouted** board (its own v2 routing
logic no longer matches v3 placements). `route_v3.py` closes that gap.

Two things about `route_v3.py` that are not obvious and will bite anyone who
rewrites it:

* **It exports a zone-free copy of the board to DSN.** If the GND pours are in
  the `.dsn`, Freerouting reads GND as an already-poured plane and routes *zero*
  copper for it — 29 unrouted nets instead of 50. The fill then fragments into
  islands and silently orphaned C4's ground pad. Exporting without the pours
  forces GND to be routed as real tracks; the pours are still in the saved
  board, so ground gets both a guaranteed track path and a plane over it.
* **Each `pcbnew` step runs in its own subprocess.** Chaining
  `LoadBoard`/`SaveBoard`/`ExportSpecctraDSN`/`ImportSpecctraSES` in one
  interpreter makes the SWIG wrapper hand back a bare `SwigPyObject` partway
  through; every method call after that dies with `AttributeError`.

**Java:** Freerouting 2.x is compiled for **Java 25** (`class file version
69.0`). The system JDK here is 21 and cannot start it. A local Temurin JRE 25
is unpacked under `%USERPROFILE%\.kicad-mcp\jre25\` — nothing is installed
system-wide. `route_v3.py` defaults to that location; override it with the
`ROUTE_JAVA` and `ROUTE_JAR` environment variables if yours lives elsewhere.

Nets routed: VBATT, VSYS, V33, V33_MCU, VDFP, GND, SPK_P, SPK_N, TRIG_OUT,
BUSY_IN, GATE_CTRL, BTN_IN, Q1_GATE, Q4_BASE, CON1, CON2.

## Pre-fab verification — `kicad/verify_v3.py`

Run it and read the last line. `PASS` means fab; anything else means stop. It
checks four things, two of which KiCad's DRC structurally *cannot*:

1. **Module body keep-outs.** J4/J5 and J6/J7 are plain pin headers, so their
   courtyards cover the header strips only — not the Pro Mini PCB or the
   DY-SV17F package that plug in and overhang in every direction. DRC will
   happily pass a board with a resistor pinned underneath a module. That was v2
   bug #1 and it cost a whole fabrication round. The checker derives each body
   rectangle from the live pad positions, so moving a header in `build_v3.py`
   moves its keep-out automatically.
2. **Electrical intent.** Netlist assertions for the rules that look right and
   are wrong: the phantom-power split (`J5.4` off `/V33`), the reverse-polarity
   FET orientation (`Q3.3`=drain→`/VBATT`, `Q3.2`=source→`/VSYS`), the Q1 load
   switch, the R3 pull-down, and a dangling-net sweep.
3. **Silkscreen vs. pads and edges.** The board's assembly silk is injected as
   free-standing `gr_text`, and KiCad's "silk over pad" rule only fires for
   *footprint* silk. Silk over a pad gets squeegeed away by paste or wicks into
   the joint, so the label you most needed is the one that goes missing.
4. **Routing completeness** — tracks, zones filled, unconnected count.

Current state of `kicad/ahmygroin.kicad_pcb`:

```
module bodies   DY-SV17F x[53.71 76.79] y[ 1.85 28.15]
                Pro Mini x[13.73 31.51] y[ 5.46 38.48]     0 parts underneath
silkscreen      60 free texts, 0 over a pad, 0 off-board
routing         148 tracks/vias   2 zones (2 filled)   0 unconnected
kicad-cli drc   0 violations, 0 unconnected items
```

### The 1:1 paper fit check — do this before paying for fabrication

`kicad/fab/v3.2-fitcheck-USLetter-1to1.pdf` is the cheapest possible catch for a
footprint bug, and footprint bugs are what killed v2. Regenerate it with:

```
"K:\Program Files\KiCad\10.0\bin\python.exe" -u kicad\fitcheck_v3.py
```

> **The A4 trap (hit for real on 2026-07-25).** The board's page setting is A4,
> and `kicad-cli pcb export pdf` has **no** `--page-size-mode` option — the PDF
> inherits the board's page. Printing that A4 sheet on US Letter makes every
> driver silently rescale, and a rescaled sheet fails in the direction of false
> confidence: pin one lines up, and the error accumulates until the last pin is
> a full pitch out. It reads exactly like a wrong-pitch footprint.
> `fitcheck_v3.py` rewrites the page to US Letter so there is nothing to rescale.

1. Print it **at 100% / "Actual size"** on **US Letter**. Turn *off* "Fit to
   page", "Shrink oversized pages", and any scaling.
2. **Measure the two 100 mm calibration bars printed on the sheet.** Both the
   horizontal and the vertical bar must read exactly 100.0 mm — both, because
   "fit to page" can scale the axes differently. If either is off, the sheet is
   void; fix the print settings and reprint. Do not interpret anything else on
   the page until these pass. The board outline is a secondary check: 90.0 × 70.0 mm.
3. Lay each module's pin row on its **pitch ladder** (the bare tick rows near the
   bottom: 12 @ 2.54 mm for the Pro Mini, 9 @ 2.50 mm for the DY-SV17F). These
   are drawn independently of the footprints, which is what makes them
   diagnostic: if a module matches its ladder but not its footprint, the
   footprint is wrong; if it matches neither, the printout is still rescaled.
4. Lay the physical DY-SV17F on its footprint. All 18 pins must drop onto pad
   centres, both rows at once. Pitch is 2.5 mm *metric*, row pitch 20.5 mm — a
   2.54 mm imperial footprint looks almost right and is off by 0.36 mm across
   nine pins, which is exactly the v2 failure.
5. Lay the physical Pro Mini on its footprint. 12 pins per side, 2.54 mm pitch,
   0.6″ (15.24 mm) row pitch.
6. Check nothing else is drawn *underneath* either module outline. The chamfered
   rectangles on the print are the true package bodies, not the header strips.

### Other checks

- `kicad-cli pcb drc` — expect 0 violations, 0 unconnected.
- 3D viewer: confirm U1's right-edge `RAW` and `VCC` silk labels line up over
  the routed pads.
- 3D viewer with a real DY-SV17F STEP model (a community-library one, not the
  DFPlayer Mini stand-in) — confirm it clears C4 and every 0805.

## Fabrication outputs

`kicad/fab/` is regenerated by `kicad-cli`; it is not hand-edited.

| File | What it is |
|---|---|
| `ahmygroin-v3.2-jlcpcb.zip` | Upload this to JLCPCB. Gerbers + drill. |
| `gerbers/` | The unzipped contents — 7 layers, `.drl`, `.gbrjob`. |
| `v3.2-fitcheck-USLetter-1to1.pdf` | The 1:1 paper print described above. US Letter, with self-verifying rulers. Built by `kicad/fitcheck_v3.py`, not by a bare `kicad-cli` call. |
| `v3.2-top.png` | 3D render, top view. |

When re-exporting Gerbers, pass the layer list explicitly — the default sweeps
in Fab, Courtyard, User_\*, Adhesive and Margin layers, which JLCPCB either
ignores or misreads:

```
--layers F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts
```

---

## Known doc debt (deferred 2026-06-07)

**Schematic (`kicad/ahmygroin.kicad_sch`) is out of sync with the v3.1 netlist and PCB.** Specifically:

* J6 and J7 are 8-pin `Conn_01x08` symbols in the schematic, but `build_v3.py` overrides them to 9-pin footprints at netlist-mutation time.
* J6/J7 net labels in the schematic match the original (pre-v3) wrong-pin design.
* `R3` (10 kΩ CON3 pull-down) exists in the netlist + PCB but not in the schematic.
* `/CON3` net label is still in the schematic but no longer exists in the netlist (folded into `/BUSY_IN`).

The PCB is correct (verified via KiCad MCP) and is the artifact that gets fab'd. The schematic redo is documentation work — not blocking fabrication. When eventually addressed: swap J6/J7 to 9-pin symbols, redo all module-side net labels per PINOUTS.md tables, add R3 between `/BUSY_IN` and `/GND`, and drop the `/CON3` label.

## Revision history

* **2026-07-25 — phantom-power fix (v3.2 pending).** Kelly's v2 board drew 14.44 mA at idle — about a week of battery life against a claimed "months". Root cause: the unpowered DY-SV17F was being fed through its input-protection diodes from two always-on sources, `IO0` (firmware idled D6 HIGH) and `CON2` (jumper rail bonded to the Pro Mini's always-on `VCC`). Both closed; idle current is now **0.15 mA**, measured in series on the battery + line. Firmware `v2/firmware/main.cpp` updated: D6 idles LOW, `sleep_bod_disable()` added, `BOOT_MS` 50 → 1000 (a module that is no longer pre-warmed by phantom power needs a real cold-boot delay). — Claude (with Kelly).
* **2026-07-25 — v3.2 PCB, fabrication-ready.** The board Kelly can solder without a single flying wire. Three electrical fixes in `build_v3.py`: the `/V33` split (`/V33_MCU` for the Pro Mini, gated `/V33` for the module + jumper rail) closing the CON2 phantom-power path; Q3 reverse-polarity FET re-oriented (drain→`/VBATT`, source→`/VSYS` — it was backwards in v3.1, i.e. no protection at all); a second Pro Mini ground bonded on `J5.2`. Placement fixed so nothing sits under either module body — R1, C2, C3 and TP1 were all evicted. Full assembly silkscreen added: chamfered body outlines, all 42 module pin names, jumper straps, connector polarity. Board fully autorouted headless (148 tracks, 0 unconnected, 0 DRC violations). New: `kicad/route_v3.py` (routing pipeline) and `kicad/verify_v3.py` (the pre-fab gate — run it, `PASS` or don't fab). — Claude.
* **2026-06-07 — v3.1 mode-select + trigger-pin fix.** Kelly's v2 board (built with flying-wire workaround) was silent. Debug session revealed three doc bugs that were inherited by v3: (a) wrong CON1/CON2/CON3 truth table in this file, (b) `/TRIG_OUT` routed to module RX/IO1 instead of TX/IO0 (in Independent Mode 0, IO0 plays 00001.mp3 and IO1 plays 00002.mp3), (c) firmware D7 `INPUT_PULLUP` silently changed the mode-select at boot. All three corrected here and propagated to `kicad/build_v3.py`. New BOM item: 10 kΩ pull-down R3 on CON3. — Claude (with Kelly).
* **2026-05-20 — v3 re-spin.** All six v2 bugs corrected via `kicad/build_v3.py`. Footprint pitch 2.5 mm metric (was 2.54 mm imperial); row pitch 20.5 mm (was 17.78 mm). User Kelly calipered the physical DY-SV17F: 26.3 × 23.08 mm outer. Routing left for the GUI autorouter. — Claude.
* 2026-05-19 — Initial file. Created after user Kelly identified five Claude-introduced bugs in the v2 PCB during build of the first board. Pinouts verified against physical HiLetgo Pro Mini (B07RS911JD) and DY-SV17F (B0BPSPPW52) modules by Kelly. — Claude (with Kelly).
