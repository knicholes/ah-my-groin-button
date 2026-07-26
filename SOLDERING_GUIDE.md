# Build the "Ah! My Groin!" device end-to-end from a bare PCB and a bag of parts

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained in accordance with `PLANS.md` at the repository root.

## Purpose / Big Picture

After following this plan you will be holding a finished device: a 120 × 120 × 140 mm 3D-printed box — softly rounded on every corner and edge so it's safe for small hands — with a large red dome button on the top face, a speaker grille and four feet on the bottom, and a small window on one side wall for the battery holder's on/off switch. Three AA batteries inside power it. When you press the button, the device plays a short audio clip ("Ah! My groin!" by default) through the speaker, then returns to deep sleep, drawing under 1 mA so a set of batteries lasts months of casual use.

You are starting from:

* a bare custom PCB fabricated to the design in `kicad/ahmygroin.kicad_pcb` (Gerber zip at `kicad/fab/ahmygroin-v3.2-jlcpcb.zip` — order this from JLCPCB or PCBWay, 5-board minimum, 2.0 mm thickness, HASL finish);
* the kit-form parts listed in `v2/bom.md` (purchased components — Pro Mini, DY-SV17F audio module, AO3401A P-MOSFETs, MMBT3904 NPN, 0805 passives, JST-XH connectors, electrolytics, button, speaker, battery holder);
* a 3D-printed case from `case/v2-120x120x140/` — `body.stl`, `bottom.stl`, and `foot.stl` printed **four times**;
* the firmware source at `v2/firmware/main.cpp`;
* the audio clip prepared as a `00001.mp3` file on your PC.

You will end up with a finished, working unit you can hand to a friend.

This is not a great *first* soldering project. Three of the active components are SOT-23 packages — surface-mount transistors roughly the size of a sesame seed. If you have never soldered anything before, work through a $10 SMD practice kit (search "SMD soldering practice kit" on Amazon) first. The hour you spend on the practice kit will save you several on this build.

## Disciplines Touched

This plan touches: **hand assembly** (SMD + through-hole soldering, wire crimping, mechanical fit), **audio assets** (loading MP3 onto the DY-SV17F via USB), and **firmware** (flashing `v2/firmware/main.cpp` to the Pro Mini via an FTDI cable). It does not modify the schematic, PCB layout, or 3D model — those are inputs, treated as fixed.

## Progress

The novice running this plan should tick each box in the order shown.

- [ ] Step 0 complete — workspace set up, all tools located, parts inventoried against the BOM, 1:1 paper fit check passed.
- [ ] Step 1 complete — seven 0805 SMD passives soldered (R1, R2, R3, C2, C3, C5, C6).
- [ ] Step 2 complete — three SOT-23 transistors soldered (Q1, Q3, Q4) with correct orientation.
- [ ] Step 3 complete — two through-hole electrolytic capacitors soldered (C1, C4) with correct polarity.
- [ ] Step 4 complete — all four module headers soldered to the PCB (J4, J5 for the Pro Mini; J6, J7 for the DY-SV17F).
- [ ] Step 5 complete — mode-select jumper pins soldered (J8, J9, J10) and shunts installed per the silkscreen (J8 1-2, J9 2-3, J10 none). Configures Independent Mode 0.
- [ ] Step 6 complete — three JST-XH connectors soldered (J1, J2, J3).
- [ ] Step 7 complete — Pro Mini plugged into J4 + J5 and soldered; DY-SV17F plugged into J6 + J7 and soldered. **No flying wires anywhere.**
- [ ] Step 8 complete — external wires crimped onto JST-XH housings: battery cable to J1-mate, button cable to J2-mate, speaker cable to J3-mate.
- [ ] Step 9 complete — `00001.mp3` loaded onto DY-SV17F's onboard flash over USB.
- [ ] Step 10 complete — `v2/firmware/main.cpp` flashed to the Pro Mini via FTDI.
- [ ] Step 11 complete — bring-up procedure passed (visual / continuity / powered).
- [ ] Step 12 complete — device installed in 3D-printed case, screwed shut, drop-tested at chest height onto carpet.

Use a real date/time when checking these off, e.g. `- [x] (2026-05-16 14:00Z) Step 0 complete — workspace set up …`.

## Surprises & Discoveries

* `Observation:` (2026-07-25) The DY-SV17F draws ~8.7 mA while it is supposed to be switched off by the Q1 power gate.
  `Evidence:` Board idle current 12.95 mA. Lifting the module's GND flying wire dropped it to 4.3 mA. The module's `V5` pin read 2.56 V with the gate closed — one diode drop below 3.3 V. Cause: the module was being back-fed through its input protection diodes from `CON2` (bonded to the always-on `/V33` rail via the Pro Mini's `VCC`) and from `IO0` (firmware idled D6 HIGH). Both paths closed → 0.15 mA idle. Full write-up in `PINOUTS.md` → *Phantom power*.

* `Observation:` (2026-07-25) Removing phantom power made the device go completely silent, which looked like a regression.
  `Evidence:` D5 measured correctly (0 V idle, ~3 V for the full playback window on a press), so the MCU and gate were fine — the module simply wasn't hearing the trigger. It had never cold-booted before: phantom power kept it pre-warmed at 2.5 V, so a 50 ms `BOOT_MS` was enough. From a genuine 0 V start it needs far longer. `BOOT_MS` 50 → 1000 restored audio immediately.

* `Observation:` (2026-07-25) The Pro Mini's onboard regulator on the HiLetgo clones is **not** an AMS1117.
  `Evidence:` The part is a 5-pin SOT-23-5 (three legs one side, two the other) marked `S2XI`, with an enable pin — a modern low-quiescent-current regulator, not the thirsty SOT-223 AMS1117 the earlier docs assumed. Do not plan an "LDO bypass" around it; it is not the drain. Measured idle after all other fixes was 150 µA total, which bounds its quiescent current well below what a bypass could recover.

## Decision Log

(Empty until you make a deliberate change to the procedure. Examples:)

* `Decision:` …
  `Rationale:` …
  `Date/Author:` …

## Outcomes & Retrospective

(Empty until the build is finished. At completion, summarise: did the device power up first time? Did anything need rework? How many hours did the build take? What would you do differently?)

## Context and Orientation

The repository is a small hardware project that lives on disk like this:

    I:/code/ah-my-groin-button/
        v2/README.md              ← schematic + design rationale (read this once before starting)
        v2/bom.md                 ← actual purchased parts and their ASINs
        v2/firmware/main.cpp      ← 110 lines of AVR C++; what gets flashed to the Pro Mini
        v2/firmware/platformio.ini
        kicad/ahmygroin.kicad_sch ← the schematic (open in KiCad ≥ 10 if you want to look)
        kicad/ahmygroin.kicad_pcb ← the PCB layout
        kicad/fab/ahmygroin-jlcpcb.zip ← Gerber zip — this is what you ordered from JLCPCB
        case/build_case.py        ← Blender script that generates the enclosure model
        case/build_v2.py          ← generates the current box
        case/v2-120x120x140/      ← print-ready 3D models — PRINT THESE
            body.stl, bottom.stl, foot.stl (×4)
        case/build_case.py        ← generates the older wide box
        case/v1-200x130x110/      ← superseded; kept so it still reproduces
        SOLDERING_GUIDE.md        ← this file
        PLANS.md                  ← rules for ExecPlans like this one

The board itself: a 90 × 70 mm rectangle of FR4 fibreglass laminate, 2.0 mm thick (twice the usual hobby-board thickness — for drop resistance), green solder-mask, HASL (hot-air-solder-levelled) silver pads. Four M3 mounting holes at the corners (the silkscreen calls these `H1`–`H4`). One copper layer on top, one on the bottom, with ground pours (large copper fills connected to the `GND` net) on both sides stitched together by vias every ~5 mm.

The silkscreen — the white painted text on the green board — labels every component pad with a reference designator (`R1`, `R2`, `C1`, `C2`, `C3`, `C4`, `C5`, `C6`, `Q1`, `Q3`, `Q4`, `J1` through `J10`, `H1` through `H4`). It also labels each connector with a hint about what plugs in there ("BAT", "BTN", "SPK").

Terms you will see in this guide, defined once:

* **SMD** — Surface-Mount Device. A part that sits flat on the top of the board with no leads going through it. Soldered to pads on the board surface.
* **Through-hole / TH** — A part with wire leads that go through holes in the board and are soldered on the opposite side.
* **0805** — A specific size of SMD passive component, 2.0 × 1.2 mm. The smallest part you will hand-solder in this build.
* **SOT-23** — A specific size of SMD transistor package, about 3 × 1.4 × 1 mm with three legs. You will solder three of these.
* **Pad** — A small flat metallic area on the PCB where a component lead sits. Solder is what bonds the lead to the pad.
* **Flux** — A liquid or paste that cleans metal surfaces during soldering. Cored solder has flux inside; for SMD work, add extra liquid flux.
* **Tinning** — Pre-melting a thin film of solder onto a pad or wire so it's ready to bond. You tin one pad on an SMD footprint, position the part, then reflow.
* **Reflow** — Re-melting solid solder by reheating it. You "reflow" a tinned pad to capture a part lead.
* **Drag-soldering** — A technique for soldering many close-spaced pins (like an IC's legs) by dragging the iron, loaded with solder and flux, across all the pins at once.
* **Reference designator** — The short alphanumeric label (`R1`, `C2`, `Q3`, `J5`) that ties a component on the PCB to its line in the schematic.
* **Polarity** — Which way around a part goes. Resistors and ceramic capacitors have no polarity. Electrolytic capacitors, diodes, LEDs, and transistors have polarity — they only work one way around.
* **DRC / ERC** — Design-Rule Check / Electrical-Rule Check. Automated PCB / schematic validations you run inside KiCad before fabrication. The board you're holding has already passed both.
* **FTDI cable** — A USB-to-serial cable with a 6-pin 0.1″ connector on the end that mates with the Pro Mini's programming header. The "FTDI" name comes from the chip inside; many cables use CH340 or CP2102 chips instead and still work. The signal levels must be 3.3 V (not 5 V) for our Pro Mini.

## Tools, Materials, and Safety

Tools you must have:

* **Temperature-controlled soldering iron** with a fine conical or chisel tip, set to 320–340 °C / 610–650 °F for leaded solder, or 350–370 °C / 660–700 °F for lead-free. A Pinecil V2, a Hakko FX-888D, or a TS100/TS101 are all fine.
* **Spool of solder.** 60/40 leaded rosin-core solder, 0.5 mm or 0.6 mm diameter (sometimes labelled "Sn60Pb40"). If you can't or won't use leaded solder, lead-free SAC305 0.5 mm works but is fussier and needs a slightly hotter iron.
* **Liquid flux.** A flux pen (Kester 951, Chip Quik SMD291) or a small bottle of "no-clean" flux. SMD work without extra flux is miserable.
* **Tweezers.** Curved-tip or straight-tip stainless steel tweezers for placing SMD parts. Anti-magnetic preferred (so you don't fling a 0805 across the room).
* **Solder wick** (a.k.a. desoldering braid). A flat copper braid that sucks up molten solder. Indispensable for fixing bridges. 2 mm width is the most useful size.
* **Multimeter.** Any cheap meter with continuity beep and a DC voltage range to at least 20 V. A Fluke is nice but unnecessary; an AstroAI or Aneng for $20 is fine.
* **Magnification.** A pair of 5×–10× magnifying glasses, a head-mounted loupe ("Optivisor"), or a USB microscope. The 0805 passives are smaller than they look and the SOT-23 markings are unreadable without magnification.
* **Isopropyl alcohol (99 % preferred)** and a clean toothbrush or cotton swabs, to clean flux residue off the board after assembly.
* **Wire stripper / cutter** capable of stripping 22–26 AWG hookup wire.
* **JST-XH crimping tool.** The kit listed in `v2/bom.md` (B0B77CSH85, ALAMSCN JST-XH 2.54 mm) ships with pre-crimped wires, so you don't strictly need a crimper. If you got bare crimps and wire instead, you do — engineer-PA09 or equivalent.
* **Small Philips screwdriver** (PH0 or PH00) for the M3 case screws.
* **FTDI cable, 3.3 V**, for programming. Search "FTDI FT232RL 3.3V USB to TTL". Make sure the cable explicitly says 3.3 V or has a 5 V / 3.3 V selector switch set to 3.3 V — applying 5 V to the Pro Mini's signal pins won't immediately destroy the ATmega328P but will stress it.
* **USB cable** with a male micro-USB connector on one end and male USB-A on the other, to load audio onto the DY-SV17F. Most "phone-charging" cables work, but it must be a *data* cable (not charge-only). A USB-A to USB-C cable is *not* what you want — the DY-SV17F has a USB-A footprint on the board edge by design (or a micro-USB on some variants — check yours).
* **3D printer or print service.** You need the printed case from `case/v2-120x120x140/`: `body.stl` ×1, `bottom.stl` ×1, and `foot.stl` **×4** (one puck per corner — it is a separate part so no support is wasted under the tray). 0.4 mm nozzle, 0.2 mm layer height, 20 % infill, PLA or PETG, four M3 brass heat-set inserts pressed into the corner bosses of the body. That folder's `README.md` has the per-part print orientations. **Check the size your slicer reports when you load them** — `body.stl` must come in at 120 × 120 × 140 mm. If you don't own a printer, services like JLC3DP or Shapeways will print the set for ~$25.

Consumables / single-use materials:

* The PCB itself (you have only the one).
* The 11 SMD parts you'll solder once.
* M3 × 25 mm countersunk screws — 4 pieces. The case stack-up requires longer screws than a typical M3 build because the bottom tray now has feet underneath it.
* M3 brass heat-set inserts — 4 pieces (search "M3 heat-set insert PCB" on Amazon).
* Optional but recommended: a 12 oz can of MG Chemicals 419D acrylic conformal coating to spray on the populated board after bring-up.

Safety notes — read these before plugging in the iron:

* The iron tip is at 340 °C. Touching it produces a burn that goes through three or four layers of skin instantly. Always set the iron in its stand between operations. Treat the iron as if it were always hot, even when off.
* Solder fumes are *flux* fumes — the metal vapour pressure is negligible at our temperatures, but the rosin smoke is a respiratory irritant and a known sensitiser. Work in a ventilated room or, ideally, with a desktop fume extractor pointing the smoke away from your face. Do not lean over your work and inhale directly.
* Lead-bearing solder gets lead on your hands. Wash hands after each session. Do not eat at the bench. Do not lick the solder; this should be obvious but is a real failure mode for kids.
* Tantalum and electrolytic capacitors installed backwards can vent (rupture and spray flammable electrolyte). Always verify polarity before powering anything new for the first time, with a fresh power supply set to a current limit of 100 mA.
* AA cells will sit happily in a holder all day, but a shorted holder lead will heat up and can start a fire on a paper-strewn bench. Do not assemble the battery pack until step 11 and don't carry assembled cells with the leads exposed.
* ESD (electrostatic discharge) — touch a grounded metal object before handling the modules. A static shock you don't feel can still damage CMOS inputs invisibly.

## Bill of Materials

The authoritative BOM is at `v2/bom.md`. The table here is a working subset reproduced for convenience. If anything disagrees with `v2/bom.md`, `v2/bom.md` wins.

* Ref `U1` — Arduino Pro Mini, 3.3 V / 8 MHz, HiLetgo (Amazon B07RS911JD, 3-pack). Verify the crystal can on the board reads `8.000`, not `16.000`. You should already own this.
* Ref `U2` — DY-SV17F audio module (Amazon B0BPSPPW52, 2-pack). Bench-test each before soldering.
* Ref `Q1`, `Q3` — AO3401A SOT-23 P-MOSFET (Amazon B08RHFLH1K, 100-pack from Todiys). Same part for both refs.
* Ref `Q4` — MMBT3904 SOT-23 NPN BJT, marked `1AM` on the package. From the SMD BJT kit (Amazon B0D69KD677), the strip labelled `2N3904 / MMBT3904`.
* Ref `R1` — 10 kΩ 0805 resistor. From the resistor kit (Amazon B09538ZBCR), labelled `10K` or `103` on the strip.
* Ref `R2` — 100 kΩ 0805 resistor. Same kit, labelled `100K` or `104`.
* Ref `R3` — 10 kΩ 0805 resistor (same value and strip as R1). CON3 mode-select pull-down, added in v3.1. On a v3 board this is a normal SMD part on the board — it is *not* the hand-soldered resistor across a jumper that the old v2 instructions described.
* Ref `C2`, `C6` — 10 µF X5R 0805 ceramic. From the ceramic-cap kit (Amazon B0F5QB3S8V), labelled `10uF`. These two values are interchangeable for our purposes; if the kit labels them `106` that is the EIA code for 10 µF.
* Ref `C3`, `C5` — 0.1 µF X7R 0805 ceramic. Same kit, labelled `100nF` or `0.1uF` or `104` (EIA code).
* Ref `C1` — 1000 µF / 10 V or higher radial electrolytic, D = 10 mm, lead pitch = 5 mm. From the electrolytic kit (Amazon B0GMKLB2QM).
* Ref `C4` — 100 µF / 10 V or higher radial electrolytic, D = 6.3 mm, lead pitch = 2.5 mm. Same kit.
* Ref `J1`, `J2`, `J3` — JST-XH 2-pin, 2.50 mm pitch, vertical PCB-mount male header. From the connector kit (Amazon B0B77CSH85). The kit also includes pre-crimped wire-side female housings.
* Ref `J4`, `J5` — the Pro Mini's two long edges, 12 holes each, 2.54 mm pitch, 15.24 mm (0.6″) apart. You do **not** buy a separate part for these: solder two 1 × 12 male pin headers to the *Pro Mini* pointing down, and those pins drop straight through the PCB's J4/J5 holes. Snap the two 12-pin strips from the connector kit (Amazon B0B77CSH85).
* Ref `J6`, `J7` — the DY-SV17F's two long edges, 9 holes each, **2.50 mm metric pitch**, 20.5 mm apart. Same idea: the module's own downward-pointing pins go through the PCB. **Use the header strips that shipped with the DY-SV17F** — they are 2.50 mm by definition. Do not substitute a 2.54 mm imperial strip from the connector kit; over nine pins the error accumulates to 0.36 mm and the last pin will not enter its hole. Your modules from the 2-pack may already have headers soldered on from the v2 build; those are the right ones.
* Ref `U1` FTDI programming header — 1 × 6 male pin header, 2.54 mm, soldered to the Pro Mini's short-edge FTDI pads **pointing up, away from the main PCB.** See the note in Step 7A; getting this backwards is the one remaining way to make the board unprogrammable after assembly.
* No hookup wire. **A v3 build has no flying wires.** If you find yourself reaching for wire, stop and re-read the *v3.2 status* section — you are following v2 instructions.
* Ref `J8`, `J9`, `J10` — 3 × 1 × 3-pin 2.54 mm-pitch single-row male pin headers, for DY-SV17F mode-select. From the connector kit. Plus three 2.54 mm jumper shunts (the small plastic-and-metal caps that bridge two adjacent header pins).
* Ref `H1`, `H2`, `H3`, `H4` — M3 mounting holes; not parts, just plated-through holes on the PCB. The corresponding hardware (4 × M3 × 25 mm countersunk screws, 4 × M3 brass heat-set inserts) is in your fastener bag.
* Off-board: EG STARTS 100 mm Big Dome arcade button (already owned, ASIN B01LZMANZ7); LAMPVPATH 3 × AA battery holder with on/off switch and leads (ASIN B07C6XC3MP); Adafruit ADA1313 3″ / 8 Ω / 1 W speaker (ASIN B00XW2NPTG); fresh 3 × AA alkaline cells.

## Plan of Work

You will work in twelve numbered steps. Steps 1–6 build the populated PCB starting with the smallest, lowest-profile parts and finishing with the connectors — this is the universal ordering principle for hand-assembled boards, because each step's parts are reachable only if the next steps' taller parts aren't in the way yet. Step 7 mounts the two modules onto their headers. Step 8 makes the external cables. Steps 9 and 10 load software onto the two modules. Step 11 is the bring-up procedure — the staged, current-limited first-power test that catches the mistakes everyone makes on their first board. Step 12 closes everything into the case.

You will not solder anything until you have read each step's full text once.

## v3.2 status — read this before anything else (2026-07-25)

**Which board am I holding?** Look at the silkscreen along the bottom edge. A v3.2
board reads:

```
AH! MY GROIN!  v3.2
IDLE 0.15mA - NO WIRE LINKS
```

If you see that, this guide applies as written and **you will not solder a single
piece of wire.** Every connection is a copper trace. Both modules plug into their
headers and that is the whole story.

If your board has no version text on it, it is a v2 board and this guide is wrong
for it. v2 needs the ten-flying-wire workaround; recover those instructions with:

```
git show c28d509:SOLDERING_GUIDE.md
```

### What changed, and why you should trust the v3.2 board

v2 had six layout bugs, all mine (Claude's). v3 (2026-05-20) fixed the geometry;
v3.1 (2026-06-07) fixed the mode-select and trigger pin; v3.2 (2026-07-25) fixed
the power topology and the assembly ergonomics. The v3.2 board:

| Was broken in | What it is now |
|---|---|
| v2 | DY-SV17F footprint is 2 × 9 pads at **2.5 mm metric** pitch, 20.5 mm row pitch — matches the real DIP-18 module. (v2 had 2 × 8 at DFPlayer-Mini geometry.) |
| v2 | J6/J7 pin assignments match the real module pinout, top-to-bottom. |
| v2 | `CON1`/`CON2`/`CON3` are actually routed from the jumpers to the module. |
| v2 | Pro Mini `RAW` and `VCC` land on J5 pads 1 and 4 — the real power pins, not D10/D11. |
| v3 | `/TRIG_OUT` goes to **IO0**, not IO1. In Independent Mode 0 that is the pin that plays `00001.mp3`. |
| v3 | `R3`, a 10 kΩ CON3 pull-down, is a normal SMD part on the board. |
| v3.1 | `/V33` is split: the module's gated V33 output feeds the jumper rail; the Pro Mini's always-on `VCC` goes nowhere near it. This is the 14 mA → 0.15 mA fix. |
| v3.1 | Q3, the reverse-polarity FET, is oriented correctly. It was backwards — meaning v3.1 boards had *no* reverse-polarity protection at all despite the part being fitted. |
| v3 | Nothing is placed under either module body. R1, C2, C3 and TP1 were moved out. |
| v3 | Full assembly silkscreen: module outlines, all 42 module pin names, jumper settings printed next to each jumper. |

The board was verified before fabrication by `kicad/verify_v3.py`, which checks
module-body keep-outs, the electrical assertions above, silkscreen-over-pad, and
routing completeness. It reported `PASS`, 0 DRC violations, 0 unconnected.

### The one thing the board cannot check for you

Footprint pitch. Do the **1:1 paper fit check in Step 0** before you solder
anything. It takes five minutes and it is the only check that would have caught
the bug that killed v2.

### Ignore the strikethrough sections

Anything below labelled *"Errata-revised"* or inside the collapsed *"Legacy v2
hardware erratum"* block describes the v2 flying-wire workaround. It does not
apply to your board. Where a step has been rewritten for v3.2 it says so in its
heading.

---

<details>
<summary>Legacy v2 hardware erratum (kept for reference; v3 does not need it)</summary>

**Mea culpa.** I (Claude) designed this board and wrote the original instructions. While building from the boards, the user found three bugs in the DY-SV17F footprint and routing that I introduced. The original Steps 4, 5, 7, and 11.2 below were written for an *imagined* DY-SV17F pinout that does not match the real module. They are wrong and are superseded by the "Errata-revised" notes inside each affected step.

The bugs:

1. **Pin count (DY-SV17F).** The PCB footprint at J6/J7 is 2 × 8 holes (16 total). The real DY-SV17F is a 2 × 9 DIP-18 module (18 pins). One pin per side will overhang the end of the row.
2. **Row pitch (DY-SV17F).** The PCB has 17.78 mm (0.7″) row spacing — that's DFPlayer Mini geometry, not DY-SV17F. The two rows of pins on a real DY-SV17F won't drop into J6 *and* J7 simultaneously; only one side can engage at a time.
3. **Pin assignment on J7 (DY-SV17F).** Even ignoring (1) and (2), the nets routed to J7's pads (`VDFP`, `GND`, `BUSY_IN`, `SPK_N`, `SPK_P`) do not align with the DY-SV17F's left-side pinout (top-to-bottom: `SPK+`, `SPK-`, `DACL`, `DACR`, `V33`, `V5`, `CON3/BUSY`, `CON2`, `CON1`). The original layout was routed against a fabricated pinout that doesn't match the real datasheet.
4. **CON1/CON2/CON3 are not routed to J6/J7 at all.** The mode-select jumpers J8/J9/J10 carry the `/CON1`, `/CON2`, `/CON3` nets — but no trace runs from those nets back to the module footprint. So even the mode pins need hand-wires.
5. **Pro Mini J5 power-pin assignment is reversed.** I routed `/V33` to J5 pad 11 and `/VSYS` to J5 pad 12 — but on a standard HiLetgo Pro Mini, those positions are `D11` and `D10` (digital pins). The actual `VCC` (3.3 V) and `RAW` (battery feed) pins are at J5 pad 4 and J5 pad 1 respectively. Plugging a Pro Mini into J5 as designed would feed ~4.5 V into D10 and 3.3 V into D11 (damaging the ATmega's pin-protection diodes) while leaving the Pro Mini's actual power pins disconnected (so it never boots). The fix is to install **J4 only** (left-side routing is correct), trim the Pro Mini's right-side header pins flush so they don't engage J5's holes, and hand-wire `RAW` and `VCC` to J5 pad 12 and J5 pad 11 respectively.

DY-SV17F pinout (correct, per user verification 2026-05-19):

```
       LEFT side                  RIGHT side
       (top to bottom)            (top to bottom)
    ┌──────────────┐           ┌──────────────┐
  1 │ SPK+         │         1 │ TX  / IO0    │
  2 │ SPK−         │         2 │ RX  / IO1    │  ← trigger input
  3 │ DACL         │         3 │ IO2          │
  4 │ DACR         │         4 │ IO3          │
  5 │ V33          │         5 │ ONE_LINE/IO4 │
  6 │ V5           │         6 │ IO5          │
  7 │ CON3 / BUSY  │         7 │ IO6          │
  8 │ CON2         │         8 │ IO7          │
  9 │ CON1         │         9 │ GND          │
    └──────────────┘           └──────────────┘
```

What can be salvaged:

| Item | Status | Reason |
|---|---|---|
| Module's pin headers (already soldered to the DY-SV17F) | **Keep both sides.** | They're not used as plug-ins — they serve as wire-anchor terminals for the flying wires. The module sits off-board and the pin tips are convenient solder posts. |
| J4 PCB header (Pro Mini left side) | **Install as designed.** | Left-side routing (GND/D2/D5/D6/D7) is correct. |
| J5 PCB header (Pro Mini right side) | **Do NOT install.** | Bug #5 above — V33 and VSYS land on D10/D11 in natural orientation. Skip the header; trim the Pro Mini's right-side pins flush; hand-wire `RAW` and `VCC` from the Pro Mini's solder pads to J5 pads 12 and 11. |
| J6 PCB header (was for DY-SV17F left side) | **Do NOT install.** | In the natural orientation, J6 pad 2 (the only routed pad, `TRIG_OUT`) lands on the module's LEFT pin 2 (`SPK−`) — a digital pulse on the speaker output. No orientation puts `IO1` on pad 2. Leave the holes empty; use them as solder pads for the flying-wire end carrying `IO1`. |
| J7 PCB header (was for DY-SV17F right side) | **Do NOT install.** | Same problem: J7 pad 2 (`VDFP`, 5 V) lands on the module's RIGHT pin 2 (`RX/IO1`) in natural orientation, which would put 5 V on a 3.3 V digital input and damage the module the moment Q1 turns on. Holes serve as solder pads. |
| J8, J9, J10 PCB headers (mode select) | **Install as designed.** | They still function. The module's `CON1`/`CON2`/`CON3` pins need flying wires from the module's left side to the middle pin of each jumper. |
| Both unused 1 × 8 male pin headers (originally intended for J6 and J7) | **Trash, or save for another project.** | Two headers don't get used in this build. |

Net summary: **two PCB-side headers get thrown out (both 1 × 8 strips for J6 and J7), and ten flying wires are added between the module and the PCB.** Everything else stays. The DY-SV17F is mounted off-PCB — hot-glued to the case wall or to a small piece of perfboard — and every signal it needs runs as a discrete wire from the module's pin-tip to a routed hole on the PCB.

</details>

## Concrete Steps

### Step 0 — Workspace setup, inventory, and read-through

Sit down at a clean, well-lit, ventilated bench. Lay out:

* the PCB, top side facing up (the side with most of the silkscreen text);
* a small dish or piece of double-sided tape to hold loose SMD parts;
* the multimeter, set to continuity-beep mode;
* the iron, plugged in but not yet hot;
* a damp sponge or brass-wool tip cleaner;
* a clean sheet of paper to keep notes on.

Inventory check: take each item from the BOM and physically locate it. The SMD passives in the kits come on strips of paper tape; the kit binder will be labelled. If you can't find a part, stop here and order it before continuing. You won't be able to "improvise" a missing AO3401A halfway through.

Read the rest of this document end-to-end *once* before applying any heat.

#### 0-bis — The 1:1 paper fit check (do not skip this)

Five minutes here is the cheapest insurance in the whole build. A footprint that
is subtly the wrong pitch looks completely normal on screen and completely normal
on the bare board, and you only discover it after you have soldered eleven SMD
parts onto a board that the modules will never seat on. That is exactly how v2
died.

1. Print `kicad/fab/v3.2-fitcheck-1to1.pdf` **at 100 %**. In the print dialog set
   Scale to "Actual size" or "100%". Turn *off* "Fit to page" and "Shrink
   oversized pages". This is the step people get wrong.
2. Take a ruler to the printed board outline — the plain rectangle. It must
   measure **90.0 mm across and 70.0 mm down**. If it doesn't, your printer
   scaled the page. Fix the print settings and print again. Do not proceed on a
   scaled print; it will "prove" a correct footprint is wrong and vice versa.
3. Lay a physical **DY-SV17F** on its printed footprint, pins down. All nine pins
   on each side must sit over pad centres *simultaneously*. Sight down the row:
   if pin 1 is centred and pin 9 is riding the edge of its pad, the pitch is
   wrong — stop and say so before ordering more boards.
4. Lay a physical **Pro Mini** on its printed footprint. Twelve pins per side.
   Same check.
5. Look at what is printed *inside* the two chamfered rectangles that mark the
   module bodies. The answer should be: nothing. No resistor, no capacitor, no
   test point. If there is something in there, it will be permanently buried
   under a module after assembly.

Only when all five pass do you pick up the iron.

### Step 1 — Solder the 0805 SMD passives

The 0805 parts on this board are R1 (10 kΩ), R2 (100 kΩ), R3 (10 kΩ), C2 (10 µF), C3 (0.1 µF), C5 (0.1 µF), and C6 (10 µF). Total: seven parts.

Find each on the silkscreen. Reference designators are printed near each pair of pads. Approximate positions on the v3.2 board, in mm from the top-left corner, if a designator has gone missing under flux:

| Ref | Value | Roughly where |
|---|---|---|
| R1 | 10 kΩ | (38, 34) — right of the Pro Mini, below the jumper row |
| R2 | 100 kΩ | (45, 34) — just right of R1 |
| R3 | 10 kΩ | (62, 41) — below the DY-SV17F, left of jumper J10 |
| C2 | 10 µF | (20, 43) — below the Pro Mini body |
| C3 | 0.1 µF | (24, 43) — right of C2 |
| C5 | 0.1 µF | (57, 33) — below the DY-SV17F |
| C6 | 10 µF | (62, 33) — right of C5 |

R1 and R3 are the same value, so mixing them up is harmless. Mixing up R1/R3 with
R2 is not: R2 is the 100 kΩ gate pull-up for Q1, and a 10 kΩ there fights Q4 hard
enough to keep the module partly on.

Procedure, per part:

1. Identify the correct value. SMD resistor codes — `103` = 10 kΩ, `104` = 100 kΩ. SMD ceramic-cap EIA codes — `104` = 0.1 µF, `106` = 10 µF (yes, resistor `104` and capacitor `104` are different values; trust the part-strip label, not just the printed code).
2. Apply a tiny dab of flux to *one* of the two pads for that footprint.
3. Touch the iron tip to the flux-wetted pad and feed in a small bead of solder — just enough to coat the pad. This is "tinning the pad."
4. Pick up the part with tweezers. Resistors have no polarity — either way is fine. 0805 ceramic caps similarly have no polarity (the body is a sintered ceramic block, you can put it down either way).
5. Slide the part so one of its end-terminations sits on the tinned pad. Hold it down with the tweezers.
6. Touch the iron tip to the tinned pad's edge. The solder reflows; the part settles. Release the tweezers. The part is now tacked in place by one end.
7. Solder the other end normally — touch iron and solder simultaneously to the un-soldered pad and the un-soldered termination.
8. Verify under magnification: both ends shiny, no bridges, no tombstoning (the part standing on edge).

Repeat for all six 0805 parts.

When you're done with this step you should see six tiny black bricks across the board. The board should still be flat — these parts are too small to stick up enough to notice from a foot away.

### Step 2 — Solder the SOT-23 transistors

Three transistors: Q1 (AO3401A P-MOSFET), Q3 (AO3401A P-MOSFET), Q4 (MMBT3904 NPN BJT).

Identification under magnification:

* AO3401A is marked `A1SHB` (Alpha & Omega Semi house style). Some clones mark it `4401` or just `AO`. The cheap Todiys 100-pack from B08RHFLH1K is genuine AO and marked correctly.
* MMBT3904 is marked `1AM`. This is the only place you will see `1AM` in your build — it's how MMBT3904 is identified in SOT-23.

If you see `1AM`, it's a 3904 — for Q4. Any other marking is one of the AO3401As — for Q1 or Q3.

Orientation: SOT-23 has three legs. Two on one side, one on the opposite side. Look closely at the silkscreen footprint on the PCB — the outline shows the same pattern. The single-leg side is the *drain* pin for the P-MOSFETs and the *collector* for the NPN. You cannot install an SOT-23 backwards — the leg pattern only goes one way — but you *can* install it twisted 180°. The silkscreen-drawn outline tells you which way is correct. **Do not skip this check.** Q1 mounted backwards will short VSYS to GND through the body diode and cook itself the moment you apply battery power.

Procedure, per part:

1. Apply flux to one of the two adjacent pads (the side with two legs).
2. Tin that pad with a thin layer of solder.
3. Hold the part with tweezers, single-leg side oriented per the silkscreen.
4. Reflow the tinned pad while sliding the part into position. The single leg should hang in mid-air at this point — that's fine.
5. Once one leg is tacked, solder the opposite single leg. Then solder the remaining adjacent leg.
6. Inspect: each leg has a small shiny fillet, none of the legs are bridged to one another, the body sits flat on the board.

If you bridge two legs, lay a piece of solder wick over them, press with the iron, and the wick will lift the bridge.

### Step 3 — Solder the through-hole electrolytic capacitors

Two parts: C1 (1000 µF / 10 V) and C4 (100 µF / 10 V).

**Electrolytic capacitors are polarised.** Installing one backwards under power will rupture the case and spray hot electrolyte. The marking convention:

* The capacitor body has a white stripe running down one side. The stripe marks the *negative* lead.
* The two leads have different lengths from the factory. The *longer* lead is positive; the shorter (sometimes pre-trimmed) is negative.
* The PCB footprint has one pad marked with a `+` symbol in silkscreen (positive) and the other pad usually has a curved bracket or stripe (negative).

Match: long lead and `+` mark, short lead and stripe.

Procedure, per cap:

1. Verify the white stripe on the cap. Verify the `+` mark on the silkscreen pad.
2. Bend the leads at the cap body so the cap will sit flush against the PCB.
3. Insert the leads through the holes from the top (parts side). The leads protrude on the bottom.
4. Trim the leads to ~2 mm on the bottom side using your wire cutter, so they don't stab anything later.
5. Solder each lead from the bottom. Feed solder while heating both lead and pad — you should see solder wick up around the lead and form a shiny concave fillet.
6. Visually verify: cap body sits flush, stripe matches `+` correctly (i.e. the *stripe* is opposite the `+` pad).

### Step 4 — Fit the headers to the two modules (rewritten for v3.2)

On a v3 board the headers belong to the *modules*, not to the PCB. You solder a
row of male pins onto each long edge of each module, pointing **down**, and in
Step 7 those pins drop straight through the PCB's holes. Nothing is soldered into
J4–J7 in this step.

Four header strips, snapped to length:

| For | Length | Pitch | Source |
|---|---|---|---|
| Pro Mini, left edge (→ J4) | 12 pins | 2.54 mm | connector kit |
| Pro Mini, right edge (→ J5) | 12 pins | 2.54 mm | connector kit |
| DY-SV17F, left edge (→ J6) | 9 pins | **2.50 mm** | shipped with the module |
| DY-SV17F, right edge (→ J7) | 9 pins | **2.50 mm** | shipped with the module |

**The two pitches are different and they are not interchangeable.** A 2.54 mm
strip in a DY-SV17F is off by 0.36 mm end-to-end, which is more than half a hole.
If your DY-SV17F already has headers on it from the v2 build, leave them; they are
the right ones.

Procedure, per module:

1. Push the header strip's long pins down through the module's holes **from the
   top** — from the component side — so the long pins stick out underneath.
   Plastic spacer against the module's underside.
2. Do both edges at once, then stand the module on a flat surface resting on the
   pin tips. Gravity holds everything square while you solder. (A solderless
   breadboard makes a good jig here if you have one.)
3. Solder one corner pin on each strip. Look at the module from the side: it must
   sit parallel to the bench, not tilted. Reheat and nudge if it isn't.
4. Solder the remaining pins, about a second of heat and a touch of solder each.
5. Under magnification, check every pin has a shiny ring of solder and no two
   adjacent pins are bridged.

Do this for both modules. When you're done you have two modules that look like
small IC packages with long legs. Set them aside — they go on in Step 7, after the
connectors.

#### 4-bis — The FTDI header, and which way it points

The Pro Mini has a sixth row of six holes on one short edge, labelled (in some
order) `DTR` `TXO` `RXI` `VCC` `GND` `GND`. That is the programming header. Solder
a 1 × 6 male pin header into it now, while the module is still loose and easy to
jig.

**The pins must point up, away from the main PCB — the same direction the
components face, the opposite direction from the twelve pins you just fitted.**

Why this matters: on the v3.2 layout the Pro Mini sits fully inside the board
outline, with about 5.5 mm of PCB underneath the FTDI edge. A downward-facing FTDI
header would land on solid board. You would have a finished device you cannot
reprogram without desoldering the Pro Mini.

Two acceptable choices:

* **Straight header pointing up (recommended).** Simplest, and there is nothing
  above the Pro Mini to collide with. The FTDI cable plugs down onto it
  vertically. Needs roughly 15 mm of headroom for the cable's plug body — the case
  has far more than that.
* **Right-angle header pointing outward.** Use this if you would rather the cable
  come in sideways. Fit it so the pins exit *away* from the board, over the top
  edge, not back across the Pro Mini.

Do not fit a straight header pointing down, and do not leave the FTDI pads bare
intending to hold wires in the holes while it flashes — that works once, badly,
and you will want it again the first time you change the audio timing.

#### 4-ter — Remove the Pro Mini's LEDs (optional, but it is worth 1.7 mA)

The finished device idles at 0.15 mA. A lit power LED on the Pro Mini draws about
**1.7 mA** on its own — more than ten times the entire rest of the board — and it
turns two years of battery life into about six weeks.

Now, with the module loose and before anything is soldered to the main PCB, is the
easiest time to remove it:

1. Find the power LED — a tiny SMD LED near the regulator that lights whenever the
   module has power. On HiLetgo clones there is often a **second** LED near the
   `D13` pad; check for that one too and take both.
2. Grip the LED body with tweezers. Heat one end pad, then the other, alternating
   every second or so until the part releases, then lift it away. Do not pry —
   the pads tear.
3. Wick the leftover solder off both pads so nothing shorts later.

This is genuinely optional. The device works fine with the LEDs fitted, it just
runs the batteries down faster. If you want the visual feedback while debugging,
leave them on and remove them after bring-up.

### Step 5 — Solder the mode-select jumper pins and install shunts

Three 3-pin headers: J8, J9, J10. These set the DY-SV17F into IO-trigger mode.
On v3 the `CON1`/`CON2`/`CON3` nets are routed from these jumpers to the module
footprint in copper, so there is nothing to hand-wire.

**The v3.2 silkscreen tells you the answer.** Printed next to each jumper is the
setting it wants:

```
CON1  SHUNT 1-2
CON2  SHUNT 2-3
CON3  NO SHUNT
```

If the board and this document ever disagree, trust the board — it was generated
from the same source that produced the netlist.

Solder each 3-pin header exactly like the module headers in step 4 — one pin at a time, verify vertical, finish the remaining pins.

Per pad data from the PCB (confirmed via the KiCad MCP), each jumper is wired:

| Header | Pad 1 (left) | Pad 2 (middle) | Pad 3 (right) |
|---|---|---|---|
| J8  | GND | /CON1 | /V33 |
| J9  | GND | /CON2 | /V33 |
| J10 | GND | /CON3 | /V33 |

So a shunt across pads 1–2 ties that `CON` pin to GND; a shunt across pads 2–3 ties it to V33.

DY-SV17F mode configuration: set the jumpers so the module enters **I/O Independent Mode 0** — in that mode, grounding the module's IO0 pin plays `00001.mp3` once, then the module idles. The real datasheet truth table is in `PINOUTS.md`. We need `CON1 = GND`, `CON2 = V33`, `CON3 = GND`.

`CON3` is dual-purpose — sampled for mode-select during the first ~30 ms after power-on, then it switches to driving the BUSY output. Hard-shorting it to GND would fight the BUSY output. That is why J10 gets **no shunt**: on a v3 board, `R3` (the 10 kΩ 0805 you soldered in Step 1) biases the line LOW, so the chip's boot-time mode-detect reads LOW while the push-pull BUSY output can still drive the line HIGH afterwards. The resistor is on the board; there is nothing to fit across the jumper.

* J8 → shunt across pads 1–2 (CON1 ↔ GND).
* J9 → shunt across pads 2–3 (CON2 ↔ V33).
* J10 → **no shunt.** R3 does the job. Leave the header bare; it stays available as an override during bring-up if you ever need to force CON3 high or low by hand.

If you can't find shunts, you can hand-solder a wire bridge between the two pins instead. Less convenient to reconfigure but works fine.

The V33 rail on J8/J9/J10 pad 3 is fed by copper from the DY-SV17F's own `V33`
output pin (module left-edge pin 5). That is deliberate and it is the single most
important electrical decision on this board:

> **Why the jumper rail must be fed by the *module's* V33 and nothing else.**
>
> On the v2 and v3.1 boards the Pro Mini's `VCC` pad landed on the same `/V33` net.
> That rail is live whenever the batteries are switched on, even with the module
> gated off — so `CON2`, shunted to it, sat at 3.3 V forever. Current flowed
> backwards into the powered-down module through its input protection diodes and
> half-woke the chip. On Kelly's board this alone cost about **8.7 mA of permanent
> idle draw** — the difference between a week and two years of battery life.
>
> **On a v3.2 board this is already fixed in copper.** The net is split: `/V33_MCU`
> is the Pro Mini's always-on `VCC` and goes nowhere; `/V33` is the module's gated
> output and feeds only the jumper rail. It collapses to 0 V the instant Q1 closes,
> which is exactly what you want. You don't have to do anything — just don't
> "helpfully" bridge the Pro Mini's `VCC` to a jumper pad.
>
> Full explanation and diagnostic fingerprints: `PINOUTS.md` → *Phantom power*.
>
> The same rule governs every other line into the module, which is why the firmware
> idles D6 (`TRIG_OUT`) **LOW** rather than HIGH.

### Step 6 — Solder the JST-XH 2-pin connectors

Three connectors: J1 (battery), J2 (button), J3 (speaker).

JST-XH 2-pin male headers have two pins on 2.50 mm pitch (slightly narrower than the 2.54 mm of the 0.1″ pin headers — make sure you're using the right ones from the kit). The plastic body has a tall keyed side that the mating female housing can only enter one way, so they're polarity-safe to plug in.

Place each connector so the *open keyed face* points toward the edge of the PCB. That way the mating cable enters from outside the board's bounding rectangle, not back across the PCB.

Procedure, per connector:

1. Insert from the top, long pins down through the bottom.
2. Solder one pin from the bottom side.
3. Verify the connector is flush and the keyed face points outward. If not, reheat and adjust.
4. Solder the other pin.

### Step 7 — Plug in the two modules (rewritten for v3.2 — no wires)

This is the step that used to take twelve flying wires and an hour of squinting.
On a v3.2 board it is two modules, forty-two pins, and no wire at all.

Both modules mount **component-side up**, on the top of the PCB, with their pins
going down through the board and soldered on the bottom.

#### 7A — Orientation: read the silkscreen, not this document

The v3.2 board prints the *name of every module pin* next to its hole. The
DY-SV17F's own silkscreen prints the same names next to the same pins. So the
orientation rule is simply:

> **Turn each module until its printed pin names line up with the board's printed
> pin names. There is exactly one rotation where they all match.**

That is the whole check, and it is self-verifying — if you have it backwards,
`SPK+` will be sitting over the hole labelled `CON1` and you will see it
immediately.

For reference, what the board expects:

**Pro Mini** — `TXO` at the top of the left column (J4 pad 1), `RAW` at the top of
the right column (J5 pad 1). The FTDI header ends up pointing at the **top edge of
the PCB**.

| J4 (left column, top → bottom) | Net | | J5 (right column, top → bottom) | Net |
|---|---|---|---|---|
| `TXO` | — | | `RAW` | /VSYS |
| `RXI` | — | | `GND` | /GND |
| `RST` | — | | `RST` | — |
| `GND` | /GND | | `VCC` | — (deliberately unconnected) |
| `D2` | /BTN_IN | | `A3` | — |
| `D3` | — | | `A2` | — |
| `D4` | — | | `A1` | — |
| `D5` | /GATE_CTRL | | `A0` | — |
| `D6` | /TRIG_OUT | | `D13` | — |
| `D7` | /BUSY_IN | | `D12` | — |
| `D8` | — | | `D11` | — |
| `D9` | — | | `D10` | — |

`VCC` having no net is correct and intentional — see the phantom-power note in
Step 5. Nothing on this board consumes the Pro Mini's regulator output.

**DY-SV17F** — `SPK+` at the top of the left column (J6 pad 1), `IO0` at the top
of the right column (J7 pad 1).

| J6 (left column, top → bottom) | Net | | J7 (right column, top → bottom) | Net |
|---|---|---|---|---|
| `SPK+` | /SPK_P | | `IO0` | /TRIG_OUT |
| `SPK-` | /SPK_N | | `IO1` | — |
| `DACL` | — | | `IO2` | — |
| `DACR` | — | | `IO3` | — |
| `V33` | /V33 | | `IO4` | — |
| `V5` | /VDFP | | `IO5` | — |
| `BUSY` | /BUSY_IN | | `IO6` | — |
| `CON2` | /CON2 | | `IO7` | — |
| `CON1` | /CON1 | | `GND` | /GND |

Note the trigger is on **IO0**, the first pin of the right column. In Independent
Mode 0 that is the pin that plays `00001.mp3`. (v3.0 had it on IO1, which plays
`00002.mp3` — a file that does not exist, so the board was silent.)

#### 7B — Seat and solder the DY-SV17F

Do the DY-SV17F first; it is the fussier of the two because of the 2.5 mm pitch.

1. Hold the module over its footprint and lower it straight down. All eighteen
   pins should enter their holes together with no persuasion. **If you have to
   push, twist, or splay pins to get it in, stop.** Lift it off and go back to the
   1:1 paper fit check — a pitch mismatch is the one failure you cannot solder
   your way out of.
2. With the module seated, look at it edge-on from two directions. The plastic
   spacers should be flat against the PCB and the module parallel to it.
3. Flip the whole board over onto a flat surface, module hanging down through the
   bench... or, easier, prop the board on two blocks so the module hangs free and
   the bottom of the PCB faces up.
4. Solder **one pin at each diagonal corner** — J6 pad 1 and J7 pad 9. Then turn
   the board back over and check the module is still flat and square. This is your
   last easy chance to fix it; reheat one corner and nudge if needed.
5. Solder the remaining sixteen pins. About a second of heat and a touch of solder
   each. Solder should wick up into the hole and form a small shiny cone around
   the pin.
6. Inspect under magnification: eighteen cones, no bridges between adjacent pins.
   At 2.5 mm pitch bridges are unlikely but check anyway.

#### 7C — Seat and solder the Pro Mini

Same procedure, twenty-four pins.

1. Lower the Pro Mini onto J4 and J5. `TXO` over J4 pad 1, `RAW` over J5 pad 1,
   FTDI header pointing at the top edge of the board.
2. Check the FTDI header is pointing **up**, away from the PCB. If it is pointing
   down you will find out right now, because it will hold the module off the
   board. Go back to Step 4-bis.
3. Solder the two diagonal corners — J4 pad 1 and J5 pad 12. Check flat and
   square.
4. Solder the remaining twenty-two pins.
5. Inspect.

Unlike the v2 build, the Pro Mini is now supported on both edges by twenty-four
soldered pins. **No hot glue is needed** — there is no cantilever to brace.

#### 7D — What you should have

Look at the board. You should see:

* Two modules sitting flat and parallel to the PCB, on the top side.
* Forty-two solder cones on the bottom side, in four neat rows.
* Two jumper shunts (J8 and J9) and one bare jumper (J10).
* Three JST-XH connectors along the bottom edge.
* **Zero wires.** If there is a wire on this board, something has gone wrong —
  re-read the *v3.2 status* section at the top of this guide.

Trim any pin that protrudes more than ~2 mm on the bottom side so it can't reach
anything in the case.

### Step 8 — Build the external cables

Three cables, all using the pre-crimped JST-XH wires from the connector kit:

* **Battery cable.** Cut the battery holder's red and black flying leads to ~10 cm length. Strip 5 mm from each. Crimp the female JST-XH terminals onto the stripped ends (if the kit shipped pre-crimped wires instead, just splice them with a small soldered joint and heatshrink). Insert into a JST-XH 2-position female housing: red wire into pin 1 (this becomes `VBATT` when plugged into J1), black wire into pin 2 (`GND`). Press the latches in until they click.

* **Button cable.** The EG STARTS dome button has four spade terminals on the back. Two 4.8 mm spades go to the microswitch (the click-switch behind the dome — the actual button function). Two 6.3 mm spades go to the LED (12 V, intentionally unused). Wire two ~15 cm lengths of 22 AWG hookup wire onto the *microswitch* spades only — one to `COM`, one to `NO` ("normally-open"). Most EG STARTS units label these on the metal housing of the microswitch. The other ends of the two wires get JST-XH female crimps and go into a 2-pin housing. `NO` → pin 1 (becomes `BTN_IN`), `COM` → pin 2 (`GND`).

* **Speaker cable.** Two ~10 cm wires from the Adafruit speaker terminals to a JST-XH 2-pin female housing. The speaker has no polarity for our purpose (mono playback). However, *do not* swap or cross the wires from one position into another between assembly attempts; if you eventually pair the device with another for stereo you want a consistent convention.

Tug-test each crimp before plugging anything in. A bad crimp will look fine and fail intermittently after a drop.

### Step 9 — Load the audio file onto the DY-SV17F

The DY-SV17F has 4 MB of onboard flash that the module exposes as a USB mass-storage device when you plug it in.

Procedure:

1. Prepare the audio file on your PC. Source the "Ah! My groin!" clip (or whatever you want to play) and export it as `00001.mp3` (**five digits, per the DY-SV17F datasheet**), mono, 48 kHz, 128 kbps. Audacity (Effect → Resample → 48000; Tracks → Mix → Mix Stereo Down to Mono; File → Export → MP3) does this fine. In Independent Mode 0, IO0 plays `00001.mp3`, IO1 plays `00002.mp3`, etc.
2. Plug a USB cable from your PC into the DY-SV17F. Some module revisions have an on-board USB-A connector you plug directly into a USB-A port via a short cable; others have a 4-pad area marked `D+` `D−` `5V` `GND` that you connect with bare wires to a hacked-up USB cable. Check yours.
3. The module will enumerate as a removable USB drive on your PC.
4. Copy `00001.mp3` to the root of the drive.
5. Right-click the drive and choose "Eject" before unplugging — this matters; on most operating systems an un-ejected USB drive can leave the file system half-written.
6. Unplug the USB cable.

The audio is now on the DY-SV17F's flash and will play whenever IO0 is pulsed LOW (the firmware will do this in step 10).

### Step 10 — Flash the firmware onto the Pro Mini

Procedure:

1. Plug the FTDI cable's 6-pin connector onto the Pro Mini's programming header, with the cable's `GND` wire on the same side as the Pro Mini's silkscreen `GND` label. FTDI cables follow a convention with black = GND, red = VCC; if your cable is wired backwards from the Pro Mini's header silkscreen you will see no power LED. The cable's `DTR` (sometimes labelled `RTS` on cheaper cables) pin goes to the Pro Mini's `DTR` pad, which is required for auto-reset.
2. Plug the FTDI cable's USB end into your PC. The Pro Mini's onboard power LED should light. If it doesn't, suspect the cable orientation or that the cable is set to 5 V instead of 3.3 V.
3. Open a terminal in the repo at `v2/firmware/`:

        cd I:/code/ah-my-groin-button/v2/firmware
        pio run -t upload

4. PlatformIO will compile and flash. Expect output along the lines of:

        Building .pio/build/pro8MHzatmega328/firmware.hex
        avrdude: 1 bytes of efuse verified
        avrdude: writing flash (3128 bytes)
        Writing | ################################################## | 100% 0.65s
        avrdude done.  Thank you.

5. After the flash, the Pro Mini's power LED stays lit. The board is now running the v2 firmware. It will immediately drop into deep sleep. Idle current at this point should be < 1 mA — measure this in step 11 if you want to verify.
6. Optional: open a serial monitor to read the firmware's `Serial.println` output:

        pio device monitor

   The current firmware build has `-DDEBUG` set so it does print status lines. Press the button on the breadboard or short the `D2` pin to GND with a wire to simulate a press, and you should see `Button press confirmed!` followed by audio playback output.

You can keep the FTDI cable plugged in throughout the bring-up in step 11 — it provides 3.3 V cleanly and you can monitor what the firmware is doing.

### Step 11 — Bring-up procedure

Do *not* skip ahead and just slap in a battery. This is the staged, current-limited first power-on that catches one mistake per build on average and prevents the smoke-out failure modes.

#### 11.1 Visual inspection

Under magnification, sweep across the board top:

* every 0805 pad has a small shiny fillet on both ends — no missed pads, no tombstoned (vertical) parts;
* every SOT-23 transistor has three small fillets, no leg-to-leg bridges, the body sits flat;
* the two electrolytic caps' bodies sit flush, with their stripes on the correct side (opposite the `+` mark);
* the three JST-XH connectors are vertical (not leaning), with each pin showing a clean fillet on both top and bottom;
* both modules sit flat and parallel to the PCB, with a solder cone on every one of the forty-two pins on the underside;
* the jumper shunts are on J8 (pads 1–2) and J9 (pads 2–3), and J10 is bare.

If you see a bridge (a glob of solder spanning two adjacent pads or legs), fix it now: flux, press solder wick onto the bridge, lift wick when it absorbs the solder.

#### 11.2 Continuity check, unpowered (rewritten for v3.2)

**Nothing is plugged in for this section. No battery, no bench supply, no FTDI
cable.** Continuity mode puts its own tiny test current through the circuit; an
external supply on top of that can damage the meter and will give you nonsense
readings.

Set the multimeter to continuity-beep mode. Touch the two probe tips together
once to confirm it beeps — that is how you know the mode and the leads are good.

Where to probe: every net below is reachable at a **module pin** on the top of the
board. Touch the probe to the exposed metal of the pin just above the module's
plastic spacer, or to the solder cone on the underside. The board's silkscreen
prints the pin name right next to each hole, so you can find any of these without
counting.

Take the checks in order and stop at the first failure.

**Group 1 — shorts. None of these may beep.**

1. `J1` pin 1 ↔ `J1` pin 2 (battery + to battery −). A beep here means a short on
   the battery rail. Find it before you connect anything.
2. `RAW` (Pro Mini right column, pin 1) ↔ `J1` pin 2. Should not beep.
3. `V5` (DY-SV17F left column, pin 6) ↔ `J1` pin 2. Should not beep.
4. `VCC` (Pro Mini right column, pin 4) ↔ `J8` pin 3. **Must not beep.** This is
   the phantom-power check. A beep means the always-on 3.3 V rail has been bonded
   to the mode-select jumper rail, which is the 8.7 mA bug from v2. On a correct
   v3.2 board these are separate nets and there is no way to bridge them short of
   a solder blob.

If any of the first three beep, you have a solder bridge. Work back over the SMD
parts with magnification.

**Group 2 — connections. All of these must beep.**

5. `J1` pin 1 ↔ the **single leg** of `Q3` (the side of the SOT-23 with one leg,
   not two). That leg is the drain, and it faces the battery. Battery feed into
   the reverse-polarity FET.
6. `RAW` (Pro Mini right column, pin 1) ↔ the `+` leg of `C1`. Both are on the
   `/VSYS` rail, downstream of Q3.
7. `GND` (Pro Mini right column, pin 2) ↔ `J1` pin 2.
8. `GND` (DY-SV17F right column, pin 9) ↔ `J1` pin 2.
9. `D6` (Pro Mini left column, pin 9) ↔ `IO0` (DY-SV17F right column, pin 1).
   This is the trigger. If it doesn't beep the device will be silent.
10. `D7` (Pro Mini left column, pin 10) ↔ `BUSY` (DY-SV17F left column, pin 7).
11. `D5` (Pro Mini left column, pin 8) ↔ one end of `R1`.
12. `V33` (DY-SV17F left column, pin 5) ↔ `J8` pin 3, `J9` pin 3, and `J10` pin 3.
    All three jumper rails come off the module's own regulator output.
13. `V33` (DY-SV17F left column, pin 5) ↔ `TP1` (the lone test point at roughly
    (44, 44), labelled `V33` on the silkscreen).
14. `SPK+` (DY-SV17F left column, pin 1) ↔ `J3` pin 1.
15. `SPK-` (DY-SV17F left column, pin 2) ↔ `J3` pin 2.
16. `D2` (Pro Mini left column, pin 5) ↔ `J2` pin 1.
17. `CON1` (DY-SV17F left column, pin 9) ↔ `J8` pin 2.
18. `CON2` (DY-SV17F left column, pin 8) ↔ `J9` pin 2.
19. `BUSY` (DY-SV17F left column, pin 7) ↔ one end of `R3`, and the other end of
    `R3` ↔ `J1` pin 2. That is the CON3 pull-down.

**Group 3 — the mode-select states.** With the shunts fitted:

20. `CON1` (DY-SV17F left pin 9) ↔ `J1` pin 2 — must beep. J8's shunt ties CON1 to
    ground.
21. `CON2` (DY-SV17F left pin 8) ↔ `V33` (DY-SV17F left pin 5) — must beep. J9's
    shunt ties CON2 to the module's V33.
22. `CON2` ↔ `J1` pin 2 — must **not** beep.

If anything in Group 2 or 3 fails to beep, you have an open joint on that net.
Reflow the pins at both ends of the failing pair and re-test. If it still fails
after reflowing both ends, tell me which check number failed — that narrows it to
a specific trace.

#### 11.3 First power, current-limited

If you own a bench supply: set it to 4.5 V, current limit 100 mA, and connect across J1 (red lead to J1.1, black to J1.2). Power on. Watch the current — it should jump briefly (charging C1) and then settle below 10 mA. If it hits the 100 mA limit, kill the supply immediately and re-inspect — you have a short somewhere.

If you don't own a bench supply: use the FTDI cable from step 10 as your power source. The cable provides 3.3 V at the Pro Mini's `VCC` pad; this bypasses Q3 and the battery, but it does test the Pro Mini and (via D5 gate control + Q1) the DY-SV17F. Skip the reverse-polarity test (11.4) since the FTDI doesn't go through Q3.

#### 11.4 Reverse-polarity test (bench supply only)

Reverse the bench supply leads on J1. Confirm current stays at zero and `VSYS` stays at 0 V (Q3 is doing its job). Restore correct polarity.

**Actually run this one on a v3.2 board.** Q3 was wired backwards on v2 and v3.1 —
drain and source swapped — which meant those boards had a reverse-polarity FET
fitted and no reverse-polarity protection. It is fixed in v3.2 and this is the
test that proves it. If current flows with the leads reversed, kill the supply
immediately: Q3 is in backwards.

Do this with the bench supply only, never with batteries. A reversed battery pack
into an unprotected board is how you release the smoke.

#### 11.5 Per-rail voltage check

With the supply on at 4.5 V, probe with the multimeter (DC volts, 20 V range):

* `VSYS` (Pro Mini `RAW` pin, right column pin 1): should read ~4.5 V minus a few millivolts.
* `VDFP` (DY-SV17F `V5` pin, left column pin 6): should read **0 V** at rest. The firmware holds D5 LOW until the button is pressed, so Q1 is off and the DY-SV17F is unpowered.
* `V33` (`TP1`, the test point at roughly (44, 44)): should read **0 V** at rest. This is the module's own regulator output and it is dead while the module is gated off. If it reads 3.3 V with the device idle, the phantom-power split has been defeated somehow — go back to check 4 in section 11.2.
* Pro Mini onboard power LED: lit — unless you removed it in Step 4-ter, in which case there is nothing to see and that is fine.

If `VDFP` reads ~`VSYS` while the firmware should be holding D5 LOW, suspect Q4 (NPN level shifter) is installed backwards or R1 is the wrong value.

Note that `VDFP` reading exactly 0 V, rather than the ~2.5 V a v2 board showed, is the whole point of the v3.2 respin. See `PINOUTS.md` → *Phantom power*.

#### 11.6 First end-to-end action

Plug in the speaker, button, and battery cables (or keep the bench supply if you're not on batteries yet). Press the button.

Expected: ~1 s after the press (`BOOT_MS`, the module's cold-boot delay), the DY-SV17F gets its trigger pulse and starts playing `00001.mp3` through the speaker, then the firmware powers the module down and returns to deep sleep.

**The one-second gap is normal and is not a fault.** A v3.2 board genuinely
cold-boots the DY-SV17F from 0 V on every press — that is what the phantom-power
fix means — and the module needs about a second to bring up its regulator and read
flash before it will listen to a trigger. If you shorten `BOOT_MS`, the trigger
pulse lands before the module is awake and the device goes silent with no other
symptom. That failure mode cost an afternoon; don't rediscover it.

If it is silent, work through these in order and stop at the first one that's wrong:

1. Is `00001.mp3` on the module's flash, with exactly five digits in the name?
   (Step 9.) `1.mp3` and `001.mp3` do not work.
2. Does `V5` on the module rise to ~4.5 V for a few seconds after the press? If
   not, the power gate isn't opening — suspect Q4 or R1.
3. Is J9's shunt on pads 2–3 and J8's on pads 1–2? Wrong mode means the trigger
   pin does something else entirely.
4. Is the trigger reaching `IO0` and not `IO1`? Check 9 in section 11.2.

#### 11.7 Sleep current

To measure current the meter goes **in series**, not across anything: switch the
battery holder off, disconnect the red battery wire from J1, and bridge that gap
with the meter — red probe to the battery wire, black probe to J1 pin 1. Then
switch the holder on. Probing in *parallel* across the battery with the meter in
current mode is a dead short through the meter; it blows the fuse at best.

With the device idle (audio finished), the current should be **around 150 µA** —
the figure measured on Kelly's finished v2 board on 2026-07-25 with both fixes in
— which works out to roughly 18–24 months on 3 × AA alkaline at 2–3 presses a day.
Use the meter's 2 mA range for a stable reading; the 20 mA range can barely
resolve it. **Do not press the button while the meter is on a low range** —
playback pulls ~150 mA and will blow the meter's fuse.

Anything much above that means something is still drawing current it shouldn't. In order of likelihood:

| Reading | Cause | Fix |
|---|---|---|
| +1.7 mA | Pro Mini onboard power LED still fitted | Step 4-ter. There is often a second LED near the D13 pad on clones — check for that one too. |
| ~4 mA | ATmega not actually in power-down | Confirm the firmware calls `sleep_bod_disable()` and that unused pins are `INPUT_PULLUP` rather than floating. |
| ~10–15 mA | Phantom power into the gated DY-SV17F via `CON2` and/or `IO0` | **Should be impossible on a v3.2 board** — the `/V33` split is in copper and the firmware idles D6 LOW. If you see this, check that you flashed the current `v2/firmware/main.cpp` and not an older build, then re-run check 4 in section 11.2. Background: `PINOUTS.md` → *Phantom power*. |

To isolate a suspected phantom-power path without desoldering: measure the DY-SV17F's `V5` pin with the device idle. It should read **0 V**. If it reads ~2.5 V, something is feeding the module through an input pin.

#### 11.8 Conformal coating (optional)

If you want the unit to survive a glass of water spilled near it, spray the populated board with MG Chemicals 419D acrylic coating per the can's directions. Mask the JST-XH housings, the Pro Mini's FTDI header, and the DY-SV17F's USB pads with painter's tape first — these are the ports you might want to access again. One light coat, dry 30 minutes, then a second light coat.

### Step 12 — Final assembly into the case

The printed case is three parts, all in `case/v2-120x120x140/`: `body.stl` (the top + four sides), `bottom.stl` (the removable tray, which carries everything), and `foot.stl` — a small puck you print **four** times, one per corner. The feet are separate so they can be printed countersink-up with no support, and so the tray's underside stays flat.

**How this box is arranged.** Unlike the old wide case, v2 stacks vertically: speaker on the bottom firing down through the grille, PCB and battery side by side in a middle layer, button on top with its microswitch bolted underneath. Everything except the button and its heat-set inserts mounts to the tray, so you build the whole device on the tray in your hand and then lift it into the shell as one piece.

Two consequences worth knowing before you start:

* The PCB does **not** sit on posts rising straight from the tray floor. Its mounting holes span 80 mm and the speaker is 77.8 mm wide, so posts can't straddle it. Instead four posts rise beside the speaker and reach inward with short arms that pass over the speaker's top face. The four bosses you screw the PCB to are on the ends of those arms, 42 mm up.
* The PCB goes in **rotated 90° from the old case** — its long axis runs front-to-back now, not side to side. That's what makes room for the battery beside it.

1. Press M3 brass heat-set inserts into the four corner bosses inside the case body. Use the soldering iron with a smooth conical tip at 250 °C, pressing each insert in vertically until its top is flush with the boss top. Let cool.
2. Mount the EG STARTS button through the 88 mm hole in the case top, securing it with the supplied threaded ring on the inside.

   The hole has two semicircular notches cut into its rim, directly opposite each other. Those clear the button's two 5.88 mm anti-rotation nubs — line the nubs up with the notches or the flange will not sit down flat on the panel. The 99 mm flange overhangs the notches by 1.5 mm, so once it's down they're hidden, and it leaves 4.5 mm of flat panel outside the flange before the rounded top rim begins.
3. **Bolt the microswitch onto the bottom of the button barrel** using the button's own switch mount. This is different from the old case, which left it dangling on its wires — here it stays captive, which is what you want in something that gets hit repeatedly. It adds 24.62 mm below the barrel, and the case height was set around that; there is 5.8 mm of air between the bottom of the switch and the tallest part on the PCB.
4. Set the Adafruit speaker on the four mounting bosses around the speaker grille on the tray, secured with the small M3 hardware that came with the speaker. Do this **first** — once the PCB is on its arms you can't reach the speaker screws.
5. Screw the populated PCB to the four bosses on the ends of the support arms. The PCB's M3 corner holes (H1–H4) line up with them. Remember the 90° rotation: the board's long edge runs front-to-back.
6. Stand the 3 × AA battery holder **on edge** in the cradle against the left wall, switch face pointing **outward at that wall**. It drops into a channel with a floor 42 mm up, a retaining wall each side and a stop at each end.

   The cradle is a plain channel, so the holder will happily go in rotated 180° with the switch in the far corner. The check comes in step 8.

   Route the leads over the cradle wall and across to J1 on the PCB.
7. Plug each cable:
   * Battery cable from holder → J1 on the PCB.
   * Button cable from dome (now via the bolted-on microswitch) → J2.
   * Speaker cable → J3.
8. **Check the switch before closing anything up.** Look at the left wall of the tray assembly from outside. You should see the holder's on/off switch sitting square in the window, recessed 11.5 mm, with a shallow scallop around the outside so a fingertip can reach in. If you see blank holder, lift it out, spin it end-for-end and drop it back. Nothing else about the fit changes.
9. Lift the populated tray up into the case body from below. The four corner blocks inside the body should align with the four holes in the tray.

   It goes in as one column and the clearances are real but small — the top of the battery passes 4.2 mm below the bottom of the button barrel. If it fouls, something is not seated: most likely the battery has not dropped fully onto its cradle floor, or the PCB is standing proud of its bosses.
10. Stack a printed foot under each corner of the tray, **countersink facing the floor**. The feet printed with the countersink facing up on the build plate, so this is the flipped orientation — the wide cone should be visible from below, ready to swallow the screw head. They lift the case 8 mm so the downward-firing speaker isn't muffled.
11. Drive the four M3 × 25 mm countersunk screws up through foot → tray → the heat-set insert in the body's corner block. The countersink is in the *foot*, not the tray; the tray has plain clearance holes. The screw length is set by that stack: 8 mm foot + 3.5 mm tray + 12 mm block = 23.5 mm. Tighten just until firm — over-torquing splits the plastic.

Done.

## Validation and Acceptance

The device is acceptable when:

* No wire was soldered anywhere on the board. Every connection is a PCB trace.
* Pressing the dome button once produces audible playback of `00001.mp3` through the speaker, about 1 s after the press (the module's genuine cold-boot time).
* The audio plays cleanly to the end without stutter or repeat-trigger.
* Pressing the button again during playback does not crash, double-trigger, or queue a second play (the firmware ignores presses while BUSY).
* The battery holder's on/off switch can be worked with a fingertip through the window in the side wall, with the case fully assembled and no tools.
* Every outside corner and edge is rounded — no sharp arris anywhere a child would grab it. Vertical corners 12 mm radius, top rim 6 mm, bottom rim 2 mm.
* The microswitch is bolted to the button, not floating on its wires. Shake the assembled unit next to your ear: nothing rattles.
* With the device sitting idle, the on/off switch on the battery holder cuts all current draw (you can verify by removing one battery — the device should be undamaged when reinserted regardless of orientation, courtesy of Q3 reverse-polarity protection).
* The unit survives a 1 m drop onto carpet without losing function. Check after drop with another button press.
* With the device idle, the DY-SV17F's `V5` pin reads **0.00 V** — not 2.5 V. This is the single measurement that proves the phantom-power path is closed.
* The unit's idle current with the holder switch on is around 150 µA (measured: 0.15 mA on Kelly's v2 board, 2026-07-25, with both Pro Mini LEDs removed and both phantom-power paths closed).
* With a bench supply connected backwards across J1, current stays at zero (Q3 protection actually works — it did not on v2 or v3.1).

Expected on the FTDI serial monitor at 9600 baud when DEBUG is built:

    Button press confirmed! Playing audio...
    DFPlayer initialized successfully!     ← legacy log line; ignore — leftover from v1 firmware in `ah-my-groin/`
    Playback completed successfully!
    Returning to sleep...
    Woke from sleep

(Note: the v2 firmware in `v2/firmware/main.cpp` does *not* print the "DFPlayer" lines — those are from the old v1 firmware. If you see them, you flashed the wrong tree. Re-flash from `v2/firmware/` per step 10.)

## Idempotence and Recovery

Steps that are *not* idempotent (consume material or are physically irreversible):

* Step 1–7: soldering. Re-soldering with the part already in place works fine for fixing cold joints, but desoldering an SMD part risks pad lift if the iron sits too long. Use solder wick to remove excess solder before lifting a part.
* Step 8: cable crimps. A bad crimp must be cut off and re-crimped.
* Step 11.3: applying battery voltage with a hidden short *will* let smoke out of one or more components. The current-limited bench supply is the safe alternative; use it if available.
* Step 12: heat-set inserts. Once a hot insert melts into the plastic, you can't move it. Press straight, press slowly.

Steps that *are* idempotent (run as many times as you want):

* Step 9: re-loading the MP3. You can change the audio file by repeating step 9 with a different `00001.mp3` later.
* Step 10: re-flashing the firmware. You can iterate on `v2/firmware/main.cpp` and reflash any number of times.
* Step 11: bring-up. Power up, measure, power down. Repeat as needed.

If you damage the PCB beyond rework — e.g. a torn-off pad — you have four other boards from the 5-board JLCPCB batch. Start over on a fresh one; the BOM has spare parts.

## Artifacts and Notes

Reference files in the repo, with their purpose:

* `kicad/ahmygroin.kicad_sch` — open in KiCad 10's Eeschema to look at the schematic. The connection tables in `v2/README.md` §4 are derived from this and are accurate.
* `kicad/ahmygroin.kicad_pcb` — open in KiCad 10's Pcbnew to look at the layout. `View → 3D Viewer` shows the populated board.
* `kicad/fab/v3.2-fitcheck-1to1.pdf` — the 1:1 print for Step 0-bis. Print at 100 %.
* `kicad/fab/ahmygroin-v3.2-jlcpcb.zip` — the Gerber package that was sent for fabrication.
* `kicad/fab/v3.2-top.png` — 3D render of the bare board, top view.
* `kicad/verify_v3.py` — the pre-fab gate. If you ever change the layout, run this and get `PASS` before ordering.
* `case/render-perspective.png`, `case/render-front.png`, `case/render-bottom.png`, `case/render-exploded.png`, `case/render-tray_top.png` — Blender Workbench renders of the finished case from various angles. The exploded view shows how the tray drops into the body.
* `v2/README.md` — the original design rationale and net list. Read once before starting in case you want context for *why* a part exists.
* `v2/bom.md` — the canonical BOM with Amazon ASINs.

Useful photos to take during your build (and paste references here in `Surprises & Discoveries` if anything goes sideways):

* Before-and-after of each SMD-soldering step.
* The board top once all SMD parts are populated but before the modules go on.
* The cable-end of each JST-XH crimp, to confirm wire colours match net assignments.
* The fully assembled board sitting in the printed tray with cables plugged in.

## Interfaces and Dependencies

For firmware: at the end of step 10, the Pro Mini must be running the build produced from `v2/firmware/main.cpp` (commit hash of your repo at the time of build). The firmware exposes the following pin behavior — these are the contract that the rest of the build depends on:

    D2  INPUT_PULLUP  Button input. LOW-level interrupt wakes from sleep.
    D5  OUTPUT        DY-SV17F power-gate via Q4 → Q1 high-side P-MOSFET.
                      HIGH = DY-SV17F powered; LOW = DY-SV17F off.
    D6  OUTPUT        DY-SV17F IO0 trigger. Held **LOW** at rest — driven
                      HIGH only in the window between the power gate
                      opening and the trigger pulse, then returned LOW
                      after the gate closes. Idling it HIGH back-feeds the
                      unpowered module through its input protection diode
                      and costs several mA. See PINOUTS.md → Phantom power.
    D7  INPUT         DY-SV17F CON3/BUSY line. NO internal pullup — a
                      pullup here pulls CON3 HIGH during the chip's boot
                      mode-sample and breaks mode-select. On a v3 board R3
                      (10 kΩ) holds the line low for mode-detect, so BUSY
                      readout is available; playback timing may still use
                      a fixed PLAY_DURATION_MS.

For electronics: at the end of step 7, the following nets must be electrically continuous and otherwise isolated:

    VBATT  — J1.1 → Q3.D  (drain faces the battery; source faces the load)
    VSYS   — Q3.S → U1.RAW (J5.1), Q1.S, C1+, C2, C3
    VDFP   — Q1.D → U2.V5 (J6.6), C4+, C5, C6
    V33    — U2.V33 (J6.5) → J8.3, J9.3, J10.3, TP1
             GATED. Dies when Q1 closes. Must never touch U1.VCC.
    GND    — J1.2 → ground pour on F.Cu and B.Cu (everything else),
             including U1.GND on both header rows (J4.4 and J5.2)
    BTN_IN — J2.1 → U1.D2 (J4.5)
    TRIG_OUT  — U1.D6 (J4.9) → U2.IO0 (J7.1)
    BUSY_IN   — U2.CON3/BUSY (J6.7) → U1.D7 (J4.10) → R3 → GND
    Q1_GATE   — Q1.G → Q4.C → R2 (pull-up to VSYS)
    GATE_CTRL — U1.D5 (J4.8) → R1 → Q4.B
    CON1   — U2.CON1 (J6.9) → J8.2        (shunt to GND)
    CON2   — U2.CON2 (J6.8) → J9.2        (shunt to V33)

    U1.VCC (J5.4) — intentionally connected to NOTHING. The Pro Mini's
    always-on 3.3 V output must not reach the gated module by any path.

Continuity-check these in step 11.2.

For 3D / mechanical: at the end of step 12, the assembled device must conform to:

    Outer dimensions:    120 × 120 × 140 mm, corners r=12, top rim r=6,
                         bottom rim r=2
    Speaker position:    centred on the tray, on 4 × M3 bosses on a 58.9 mm
                         square pattern, firing down through the grille.
                         Occupies z 9.5 → 35.0
    PCB position:        middle layer, z 42.0, on 4 bosses carried on arms
                         that reach in over the speaker. Long axis
                         front-to-back (rotated 90° from v1)
    Battery position:    on edge in the cradle against the −X wall,
                         z 42.0 → 90.2, switch facing out through the
                         window in that wall, recessed 11.5 mm
    Button position:     top centre, 88 mm dia. hole with two 4 mm
                         anti-rotation notches 180° apart. Barrel reaches
                         to z 94.4, microswitch bolted under it to z 69.8
    Foot clearance:      8 mm of air under the speaker grille

If any of those dimensions are wrong, re-run `case/build_case.py` after editing the constants at the top of the file and re-print the affected STL.

## Revision history

* **2026-07-26 — retargeted onto the v2 case (`case/v2-120x120x140`).** The case went from 200 × 130 × 110 to 120 × 120 × 140: narrower footprint, taller, and stacked rather than spread — speaker on the bottom, PCB and battery side by side in a middle layer, button on top. Every outside corner and edge is now rounded (12 / 6 / 2 mm) because the device is going to small children. Step 12 rewritten: 11 steps instead of 9, the speaker now goes in *before* the PCB (its screws become unreachable afterwards), the PCB mounts rotated 90° onto bosses carried on arms that reach over the speaker, the battery stands on edge in a cradle with its switch facing out through a side wall rather than lying flat over a floor window, and the microswitch is bolted to the button instead of dangling on its wires. Also fixed: the intro, deliverables list, file tree, printer section, and the mechanical acceptance block, all of which still described the wide box; the acceptance list gained the rounding and rattle checks; and the print section now tells you to check the size your slicer reports, because until this date the STL exporter wrote metres and `body.stl` loaded as a 0.2 mm speck. Two structural facts are now recorded rather than rediscovered: the PCB's 80 mm mount span cannot straddle the 77.8 mm speaker on tray posts at any box size, and everything tray-mounted must pass up through the 103 mm bottom opening. — Claude.
* **2026-07-25 — rewritten for the v3.2 board. No flying wires.** The whole point of the v3.2 respin was that this guide should stop asking Kelly to solder wire. Rewritten: the *v3.2 status* section (which board am I holding, what changed, what to ignore); Step 0-bis (the 1:1 paper fit check, promoted to a mandatory gate); Step 1 (R3 added, position table); Step 4 (headers now belong to the modules, not the PCB — plus 4-bis on the FTDI header direction and 4-ter on removing the Pro Mini LEDs); Step 5 (silkscreen now states the jumper settings; R3 replaces the hand-soldered pull-down; the phantom-power warning becomes "already fixed in copper"); Step 7 (completely replaced — twelve flying wires became "plug both modules in", with per-column pin/net tables and a self-verifying silkscreen orientation rule); Step 11.1/11.2 (continuity checks rewritten against module pins, grouped into shorts / connections / mode-select, with the meter-safety note); 11.4 (reverse-polarity test now matters, because Q3 was backwards until v3.2); 11.5 (added the `V33` = 0 V check); 11.6 (the 1 s cold-boot delay is normal — troubleshooting ladder added); 11.7 (how to put the meter in series without shorting the pack; phantom power demoted to "should be impossible"); the firmware contract (D6 idles LOW) and the net list (V33 split, Q3 orientation, `U1.VCC` connected to nothing). — Claude.
* 2026-05-16 — Initial ExecPlan, derived from the design in `v2/README.md`, the BOM in `v2/bom.md`, the firmware in `v2/firmware/main.cpp`, and the case in `case/build_case.py`. Twelve steps covering full assembly from bare PCB to finished unit. Written to the format defined in `PLANS.md`. — Claude (with user Kelly).
* 2026-05-19 — Added the *Hardware erratum* section after user (Kelly) identified three bugs in the DY-SV17F footprint I designed: wrong pin count (2 × 8 instead of 2 × 9), wrong row pitch (0.7″ DFPlayer-Mini geometry, not DY-SV17F), and J7's nets misaligned with the real DY-SV17F left-side pinout (`SPK+`, `SPK-`, `DACL`, `DACR`, `V33`, `V5`, `CON3/BUSY`, `CON2`, `CON1` top-to-bottom). Also discovered `CON1/CON2/CON3` aren't routed to the module footprint at all. Errata-revised Steps 4, 5, 7, and 11.2. PCB-side header J7 is no longer populated. — Claude (with user Kelly).
* 2026-05-19 (later, after Kelly caught a follow-on error) — Corrected my earlier claim that J6 was salvageable for the trigger signal. I had asserted "module right side plugs into J6, so `RX/IO1` lands on pad 2 (`TRIG_OUT`)" — but the module's right side is physically on the right of the natural mounting orientation, over J7, not J6. No rotation puts `IO1` on J6 pad 2. In the natural orientation, J6 pad 2 lands on the module's left pin 2 (`SPK−`) and J7 pad 2 lands on right pin 2 (`RX/IO1`) — putting 5 V on a digital input, which would damage the module. Re-revised: J6 is also not populated. All ten signals (including `IO1` to J6 pad 2) are flying wires; the DY-SV17F is mounted off-PCB. — Claude (with user Kelly).
* 2026-05-19 (still later — fifth Claude-introduced bug) — Kelly identified that the Pro Mini's J5 power pins are also reversed. The PCB routes `/V33` to J5 pad 11 and `/VSYS` to J5 pad 12 — those are `D11` and `D10` positions on a standard HiLetgo Pro Mini. The actual `VCC` and `RAW` pins are at pad 4 and pad 1 (top of the right side). Plugging in the Pro Mini as designed would short ~4.5 V into `D10` and 3.3 V into `D11` while leaving the Pro Mini's actual power inputs disconnected. Re-revised: J5 is also not populated. The Pro Mini's right-side header pins are trimmed flush so they don't engage J5's holes; two flying wires (P1 = `RAW` → J5 pad 12, P2 = `VCC` → J5 pad 11) carry power. Pro Mini's right side is supported by hot glue under the cantilevered edge. — Claude (with user Kelly).
