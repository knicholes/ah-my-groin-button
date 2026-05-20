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
| 9 | `6` | D6 | **/TRIG_OUT** | Required. Pulled HIGH at rest; pulses LOW to trigger DY-SV17F IO1. |
| 10 | `7` | D7 | **/BUSY_IN** | Required. Reads DY-SV17F BUSY (LOW during playback). |
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

**Form factor:** Two parallel 1 × 9 long-edge solder pads on 0.1″ (2.54 mm) pitch. DIP-18 outline. Long-edge row spacing **needs measurement on the physical module — it is NOT 0.7″ / 17.78 mm (that's DFPlayer Mini geometry). Likely 0.6″ / 15.24 mm.** Re-verify with calipers before laying out v3.

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
| 7 | `CON3` / `BUSY` | Mode select pin 3 / BUSY output | **/BUSY_IN** *and* **/CON3** | Required. Dual-purpose: sampled at boot for mode selection, then drives BUSY low during playback. May need a 10 kΩ pull-up or pull-down to set the mode; the BUSY output is push-pull and overrides during playback. |
| 8 | `CON2` | Mode select pin 2 | **/CON2** | Required. Set HIGH or LOW via J9 jumper. |
| 9 | `CON1` | Mode select pin 1 | **/CON1** | Required. Set HIGH or LOW via J8 jumper. |

### Right long edge (top to bottom)

| # | Pad label (silkscreen) | Function | v2/v3 net | Notes |
|---|---|---|---|---|
| 1 | `TX` / `IO0` | UART TX / IO trigger 0 | — | Unused (no UART in this build). |
| 2 | `RX` / `IO1` | UART RX / IO trigger 1 | **/TRIG_OUT** | Required. **Trigger input.** Firmware pulses this LOW for 20 ms to start playback. |
| 3 | `IO2` | IO trigger 2 | — | Unused. |
| 4 | `IO3` | IO trigger 3 | — | Unused. |
| 5 | `ONE_LINE` / `IO4` | One-line serial / IO trigger 4 | — | Unused. |
| 6 | `IO5` | IO trigger 5 | — | Unused. |
| 7 | `IO6` | IO trigger 6 | — | Unused. |
| 8 | `IO7` | IO trigger 7 | — | Unused. |
| 9 | `GND` | Ground | **/GND** | Required. |

### Mode configuration for "pulse IO1 LOW → play track 001 once, then idle"

Per the DY-SV17F datasheet for one-shot IO-trigger mode (verify against the silkscreen table on the back of your specific module rev — clones reorder these occasionally):

| Pin | State at boot |
|---|---|
| CON1 | GND (via J8 1↔2 shunt) |
| CON2 | V33 (via J9 2↔3 shunt) |
| CON3 | floating, or via 10 kΩ to GND/V33 per datasheet sub-mode |

The on-board J8/J9/J10 jumpers (3-pin selectors, layout `GND / CON_x / V33`) must connect via the v3 PCB traces to the corresponding DY-SV17F CON pins. **In v2 these traces are missing — the CON nets exist only at the jumpers, not at the U2 footprint.**

### USB / file loading

The DY-SV17F has on-board 4 MB SPI flash that enumerates as a USB mass-storage device when the module is connected to a PC. Load `0001.mp3` to the root of the drive. No microSD card.

USB-side pads on the module: separate from the long-edge pins, on the short edge near the USB connector cutout. Not routed through the carrier PCB in v2 or planned for v3.

---

## v2 PCB errata (what the re-spin must fix)

For full context see `SOLDERING_GUIDE.md` → *Hardware erratum* section. Summary of what v3 must change:

1. **DY-SV17F footprint:** change from 2 × 8 / 0.7″ to **2 × 9 / 0.6″** (or whatever calipers reveal as the actual DY-SV17F row pitch). Pad assignments per the table above. Place the silkscreen pin-1 marker at the `SPK+` corner.
2. **DY-SV17F net routing:** route `/SPK_P`, `/SPK_N`, `/V33`, `/VDFP`, `/BUSY_IN`, `/CON1`, `/CON2`, `/CON3`, `/GND`, and `/TRIG_OUT` per the U2 tables above. The current v2 J7 routing is fabricated against a fictitious pinout and must be discarded entirely.
3. **CON1/CON2/CON3 traces:** in v2, the CON nets exist only at the J8/J9/J10 jumper middle pins. In v3, run those traces all the way to U2 pins 9, 8, 7 respectively.
4. **Pro Mini J5 power pins (bug #5):** route `/VSYS` to U1 right-edge **pin 1** (`RAW`) and `/V33` to U1 right-edge **pin 4** (`VCC`). In v2, I put them at the *bottom* of the right edge (pins 11 and 12 — the `D11` and `D10` positions), which both fails to power the Pro Mini and damages two digital pins.
5. **C4 placement:** in v2, C4 is at (60, 14) — directly under the DY-SV17F module footprint. Move it to a free area of the board so the 7 mm-tall electrolytic doesn't collide with the module body.
6. **Test points:** keep the named test points (`VSYS`, `VDFP`, `PFET_GATE`, `BUSY_IN`, `GND`) per `v2/README.md` §5. Add a `V33` test point too — the v33 rail is now consequential after the mode-jumper redesign.

## Suggested v3 verification before fab

- ERC + DRC pass in KiCad.
- 3D viewer: visually confirm U1 right-edge `RAW` and `VCC` silkscreen labels line up over the routed pads. (This would have caught bug #5.)
- 3D viewer: confirm U2's actual STEP model (download a real DY-SV17F STEP file from a community library, not the DFPlayer Mini stand-in) fits the footprint without overlapping C4 or any 0805.
- Print the board layout at 1:1 scale and physically lay your DY-SV17F and Pro Mini on the paper to confirm pin alignment before sending Gerbers. **This is the cheapest catch for any further footprint bugs.**

---

## Revision history

* 2026-05-19 — Initial file. Created after user Kelly identified five Claude-introduced bugs in the v2 PCB during build of the first board. Pinouts verified against physical HiLetgo Pro Mini (B07RS911JD) and DY-SV17F (B0BPSPPW52) modules by Kelly. — Claude (with Kelly).
