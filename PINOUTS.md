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
| 9 | `6` | D6 | **/TRIG_OUT** | Required. Pulled HIGH at rest; pulses LOW to trigger DY-SV17F IO0. |
| 10 | `7` | D7 | **/BUSY_IN** | Required. Reads DY-SV17F BUSY (LOW during playback). Firmware must set this as plain `INPUT` (no pullup) — see CON3 note in U2 table. |
| 11 | `8` | D8 | — | Unused. |
| 12 | `9` | D9 | — | Unused. |

### Right long edge (top to bottom)

| # | Pad label (silkscreen) | Arduino name | v2/v3 net | Notes |
|---|---|---|---|---|
| 1 | `RAW` | VIN | **/VSYS** | Required. Battery feed after Q3 reverse-polarity FET. |
| 2 | `GND` | GND | /GND (optional) | Can also use this GND instead of left pin 4. |
| 3 | `RST` | RESET | — | Mirror of left pin 3. |
| 4 | `VCC` (sometimes printed `V3.3`, `ACC`, `+3.3`) | VCC | **/V33** | Required. 3.3 V output of the Pro Mini's onboard AMS1117 regulator. Also powers the V33 net for mode-select jumpers. |
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
| 5 | `V33` | 3.3 V output (internal regulator) | **/V33** | Required. Feeds the V33 net (shared with Pro Mini VCC for mode-select reference). |
| 6 | `V5` | 5 V power input | **/VDFP** | Required. Gated by Q1 P-FET from VSYS. |
| 7 | `CON3` / `BUSY` | Mode select pin 3 / BUSY output | **/BUSY_IN** *and* **/CON3** | Required. Dual-purpose: sampled at boot for mode selection (first ~30 ms after power-on), then drives BUSY low during playback. In v3, biased LOW via a **10 kΩ pull-down resistor (R3) to GND** so the chip samples Independent Mode 0 at boot, while the push-pull BUSY output can still drive the line HIGH afterward. **Firmware must keep D7 as `INPUT` (no internal pullup) — a pullup here fights the boot-time pull-down and selects the wrong mode.** |
| 8 | `CON2` | Mode select pin 2 | **/CON2** | Required. Set HIGH or LOW via J9 jumper. |
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

## v3 routing pipeline (verified working 2026-06-08)

`build_v3.py` produces an **unrouted** PCB — footprints, pad-net assignments, board outline, GND zones, and silkscreen are in place but no copper traces yet. The autoroute pipeline:

1. Close KiCad if it has the PCB open.
2. `python build_v3.py` — regenerates footprints, nets, placements, GND zone outlines, and silkscreen.
3. KiCad MCP `export_dsn` → produces `ahmygroin.dsn`.
4. Run **Freerouting v2.0.1** with Java 21 (Temurin LTS):
   ```
   "C:\Program Files\Eclipse Adoptium\jdk-21.0.11.10-hotspot\bin\java.exe" \
     -jar /tmp/freerouting-2.0.1.jar \
     -de kicad/ahmygroin.dsn -do kicad/ahmygroin.ses -mp 30
   ```
   v2.2.x of Freerouting requires Java 25 — avoid it on this machine.
5. KiCad MCP `import_ses` → applies routing back to `.kicad_pcb`.
6. **Fill GND zones** (this step is needed because `build_v3.py` only adds the zone *outlines*, and `import_ses` doesn't fill either):
   ```python
   import pcbnew
   b = pcbnew.LoadBoard("kicad/ahmygroin.kicad_pcb")
   pcbnew.ZONE_FILLER(b).Fill(b.Zones())
   pcbnew.SaveBoard("kicad/ahmygroin.kicad_pcb", b)
   ```
7. `kicad-cli pcb drc kicad/ahmygroin.kicad_pcb` — expect 0 violations, 0 unconnected.
8. Open in KiCad GUI; eyeball R3, J7 routing, and pad alignment.
9. Print at 1:1 scale; lay the physical Pro Mini + DY-SV17F on the paper to confirm pin alignment.
10. Export Gerbers; upload to JLCPCB.

The 14 nets routed: VBATT, VSYS, V33, VDFP, GND, SPK_P, SPK_N, TRIG_OUT, BUSY_IN, GATE_CTRL, BTN_IN, Q1_GATE, Q4_BASE, CON1, CON2.

## Suggested v3 verification before fab

- ERC + DRC pass in KiCad (currently DRC reports 0 violations on the unrouted board; will report unconnected items until routing is done).
- 3D viewer: visually confirm U1 right-edge `RAW` and `VCC` silkscreen labels line up over the routed pads.
- 3D viewer: confirm U2's actual STEP model (download a real DY-SV17F STEP file from a community library, not the DFPlayer Mini stand-in) fits the footprint without overlapping C4 or any 0805.
- Print the board layout at 1:1 scale and physically lay your DY-SV17F and Pro Mini on the paper to confirm pin alignment before sending Gerbers. **This is the cheapest catch for any further footprint bugs.**

---

## Known doc debt (deferred 2026-06-07)

**Schematic (`kicad/ahmygroin.kicad_sch`) is out of sync with the v3.1 netlist and PCB.** Specifically:

* J6 and J7 are 8-pin `Conn_01x08` symbols in the schematic, but `build_v3.py` overrides them to 9-pin footprints at netlist-mutation time.
* J6/J7 net labels in the schematic match the original (pre-v3) wrong-pin design.
* `R3` (10 kΩ CON3 pull-down) exists in the netlist + PCB but not in the schematic.
* `/CON3` net label is still in the schematic but no longer exists in the netlist (folded into `/BUSY_IN`).

The PCB is correct (verified via KiCad MCP) and is the artifact that gets fab'd. The schematic redo is documentation work — not blocking fabrication. When eventually addressed: swap J6/J7 to 9-pin symbols, redo all module-side net labels per PINOUTS.md tables, add R3 between `/BUSY_IN` and `/GND`, and drop the `/CON3` label.

## Revision history

* **2026-06-07 — v3.1 mode-select + trigger-pin fix.** Kelly's v2 board (built with flying-wire workaround) was silent. Debug session revealed three doc bugs that were inherited by v3: (a) wrong CON1/CON2/CON3 truth table in this file, (b) `/TRIG_OUT` routed to module RX/IO1 instead of TX/IO0 (in Independent Mode 0, IO0 plays 00001.mp3 and IO1 plays 00002.mp3), (c) firmware D7 `INPUT_PULLUP` silently changed the mode-select at boot. All three corrected here and propagated to `kicad/build_v3.py`. New BOM item: 10 kΩ pull-down R3 on CON3. — Claude (with Kelly).
* **2026-05-20 — v3 re-spin.** All six v2 bugs corrected via `kicad/build_v3.py`. Footprint pitch 2.5 mm metric (was 2.54 mm imperial); row pitch 20.5 mm (was 17.78 mm). User Kelly calipered the physical DY-SV17F: 26.3 × 23.08 mm outer. Routing left for the GUI autorouter. — Claude.
* 2026-05-19 — Initial file. Created after user Kelly identified five Claude-introduced bugs in the v2 PCB during build of the first board. Pinouts verified against physical HiLetgo Pro Mini (B07RS911JD) and DY-SV17F (B0BPSPPW52) modules by Kelly. — Claude (with Kelly).
