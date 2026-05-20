# Build the "Ah! My Groin!" device end-to-end from a bare PCB and a bag of parts

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained in accordance with `PLANS.md` at the repository root.

## Purpose / Big Picture

After following this plan you will be holding a finished device: a 200 × 130 × 90 mm 3D-printed box with a large red dome button on the top face and a speaker grille and four feet on the bottom. Three AA batteries inside power it. When you press the button, the device plays a short audio clip ("Ah! My groin!" by default) through the speaker, then returns to deep sleep, drawing under 1 mA so a set of batteries lasts months of casual use.

You are starting from:

* a bare custom PCB fabricated to the design in `kicad/ahmygroin.kicad_pcb` (Gerber zip at `kicad/fab/ahmygroin-jlcpcb.zip` — order this from JLCPCB or PCBWay, 5-board minimum, 2.0 mm thickness, HASL finish);
* the kit-form parts listed in `v2/bom.md` (purchased components — Pro Mini, DY-SV17F audio module, AO3401A P-MOSFETs, MMBT3904 NPN, 0805 passives, JST-XH connectors, electrolytics, button, speaker, battery holder);
* a 3D-printed case from `case/body.stl` and `case/bottom.stl`;
* the firmware source at `v2/firmware/main.cpp`;
* the audio clip prepared as a `0001.mp3` file on your PC.

You will end up with a finished, working unit you can hand to a friend.

This is not a great *first* soldering project. Three of the active components are SOT-23 packages — surface-mount transistors roughly the size of a sesame seed. If you have never soldered anything before, work through a $10 SMD practice kit (search "SMD soldering practice kit" on Amazon) first. The hour you spend on the practice kit will save you several on this build.

## Disciplines Touched

This plan touches: **hand assembly** (SMD + through-hole soldering, wire crimping, mechanical fit), **audio assets** (loading MP3 onto the DY-SV17F via USB), and **firmware** (flashing `v2/firmware/main.cpp` to the Pro Mini via an FTDI cable). It does not modify the schematic, PCB layout, or 3D model — those are inputs, treated as fixed.

## Progress

The novice running this plan should tick each box in the order shown.

- [ ] Step 0 complete — workspace set up, all tools located, parts inventoried against the BOM.
- [ ] Step 1 complete — six 0805 SMD passives soldered (R1, R2, C2, C3, C5, C6).
- [ ] Step 2 complete — three SOT-23 transistors soldered (Q1, Q3, Q4) with correct orientation.
- [ ] Step 3 complete — two through-hole electrolytic capacitors soldered (C1, C4) with correct polarity.
- [ ] Step 4 complete — module header pins soldered to the PCB (J4 only for the Pro Mini left side — J5, J6, J7 all left empty per the *Hardware erratum*).
- [ ] Step 5 complete — mode-select jumper pins soldered (J8, J9, J10) and shunts installed per the errata-revised table (J8 1-2 GND, J9 2-3 V33, J10 unshunted).
- [ ] Step 6 complete — three JST-XH connectors soldered (J1, J2, J3).
- [ ] Step 7 complete — Pro Mini soldered onto J4 with right-side pins trimmed and 2 power flying wires (`RAW`/`VCC` → J5 pads 12/11); DY-SV17F hot-glued to the case off-PCB; 10 flying wires from module pin tips to PCB nets per the errata-revised wire table.
- [ ] Step 8 complete — external wires crimped onto JST-XH housings: battery cable to J1-mate, button cable to J2-mate, speaker cable to J3-mate.
- [ ] Step 9 complete — `0001.mp3` loaded onto DY-SV17F's onboard flash over USB.
- [ ] Step 10 complete — `v2/firmware/main.cpp` flashed to the Pro Mini via FTDI.
- [ ] Step 11 complete — bring-up procedure passed (visual / continuity / powered).
- [ ] Step 12 complete — device installed in 3D-printed case, screwed shut, drop-tested at chest height onto carpet.

Use a real date/time when checking these off, e.g. `- [x] (2026-05-16 14:00Z) Step 0 complete — workspace set up …`.

## Surprises & Discoveries

(Empty until something surprises you. Examples of what to record here:)

* `Observation:` …
  `Evidence:` …

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
        case/body.stl, bottom.stl ← print-ready 3D models
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
* **3D printer or print service.** You need the printed case (`case/body.stl` and `case/bottom.stl`). 0.4 mm nozzle, 0.2 mm layer height, 20 % infill, PLA or PETG, four M3 brass heat-set inserts pressed into the corner bosses of the body. If you don't own a printer, services like JLC3DP or Shapeways will print both parts for ~$25.

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
* Ref `C2`, `C6` — 10 µF X5R 0805 ceramic. From the ceramic-cap kit (Amazon B0F5QB3S8V), labelled `10uF`. These two values are interchangeable for our purposes; if the kit labels them `106` that is the EIA code for 10 µF.
* Ref `C3`, `C5` — 0.1 µF X7R 0805 ceramic. Same kit, labelled `100nF` or `0.1uF` or `104` (EIA code).
* Ref `C1` — 1000 µF / 10 V or higher radial electrolytic, D = 10 mm, lead pitch = 5 mm. From the electrolytic kit (Amazon B0GMKLB2QM).
* Ref `C4` — 100 µF / 10 V or higher radial electrolytic, D = 6.3 mm, lead pitch = 2.5 mm. Same kit.
* Ref `J1`, `J2`, `J3` — JST-XH 2-pin, 2.50 mm pitch, vertical PCB-mount male header. From the connector kit (Amazon B0B77CSH85). The kit also includes pre-crimped wire-side female housings.
* Ref `J4` — 1 × 1 × 12-pin 2.54 mm-pitch single-row male pin header, to mate the Pro Mini's *left side* to the PCB. From the connector kit. (J5 is not populated — see *Hardware erratum* bug #5. The second 1 × 12 strip is unused for this build.)
* Ref `J6`, `J7` — **not populated.** See the *Hardware erratum* section. Both 1 × 8 pin-header strips from the connector kit are unused for this build.
* ~12 × 60 mm lengths of 28 AWG stranded silicone-insulated hookup wire — 10 for the DY-SV17F flying wires (Step 7C) and 2 for the Pro Mini `RAW`/`VCC` flying wires (Step 7A-bis). Any colour; one bundle.
* Ref `J8`, `J9`, `J10` — 3 × 1 × 3-pin 2.54 mm-pitch single-row male pin headers, for DY-SV17F mode-select. From the connector kit. Plus three 2.54 mm jumper shunts (the small plastic-and-metal caps that bridge two adjacent header pins).
* Ref `H1`, `H2`, `H3`, `H4` — M3 mounting holes; not parts, just plated-through holes on the PCB. The corresponding hardware (4 × M3 × 25 mm countersunk screws, 4 × M3 brass heat-set inserts) is in your fastener bag.
* Off-board: EG STARTS 100 mm Big Dome arcade button (already owned, ASIN B01LZMANZ7); LAMPVPATH 3 × AA battery holder with on/off switch and leads (ASIN B07C6XC3MP); Adafruit ADA1313 3″ / 8 Ω / 1 W speaker (ASIN B00XW2NPTG); fresh 3 × AA alkaline cells.

## Plan of Work

You will work in twelve numbered steps. Steps 1–6 build the populated PCB starting with the smallest, lowest-profile parts and finishing with the connectors — this is the universal ordering principle for hand-assembled boards, because each step's parts are reachable only if the next steps' taller parts aren't in the way yet. Step 7 mounts the two modules onto their headers. Step 8 makes the external cables. Steps 9 and 10 load software onto the two modules. Step 11 is the bring-up procedure — the staged, current-limited first-power test that catches the mistakes everyone makes on their first board. Step 12 closes everything into the case.

You will not solder anything until you have read each step's full text once.

## Hardware erratum — DY-SV17F mounting bugs (added 2026-05-19)

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

### Step 1 — Solder the 0805 SMD passives

The 0805 parts on this board are R1 (10 kΩ), R2 (100 kΩ), C2 (10 µF), C3 (0.1 µF), C5 (0.1 µF), and C6 (10 µF). Total: six parts.

Find each on the silkscreen. Reference designators are printed near each pair of pads:

* R1, R2 are near the Pro Mini headers and the BJT Q4. R1 is the 10 kΩ; R2 is the 100 kΩ.
* C2, C3 are near the Pro Mini's RAW pin (left side of the Pro Mini footprint).
* C5, C6 are near the DY-SV17F's V5 pin (left side of the DY-SV17F footprint).

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

### Step 4 — Solder the module pin headers

**Errata-revised (2026-05-19, corrected twice): only J4 is installed.** See the *Hardware erratum* section above for context. One header, not four: J4 only (Pro Mini left side, 1 × 12 pins). J5 is omitted because the right-side power-pin routing is reversed (bug #5). Both 1 × 8 strips for J6 and J7 are also discarded — the DY-SV17F is mounted off-PCB in Step 7 and every signal is a flying wire.

These are simple straight 0.1″ (2.54 mm) male pin headers. The kit ships them as long strips that you snap to length. Snap one 12-pin piece for J4.

Procedure, per header:

1. Insert the long pins of the header through the PCB *from the bottom*, so the long pins point up through the top of the PCB. The short ends and the plastic spacer remain on the bottom.
2. Place the PCB flat on the bench with the bottom side facing up. The headers should stand vertically through the board.
3. Solder one corner pin only. Check from the side that the header is square and vertical, not leaning. If it leans, reheat the corner pin and gently push the header straight before the solder freezes.
4. Solder the diagonally opposite corner pin. Re-check vertical.
5. Solder the remaining pins one by one. Each takes about a second of heat plus a touch of solder.
6. Flip the board over and check from the top side that each pin has a clean fillet (a small ring of solder around the pin) on the top side as well as the bottom.

You should end up with a single row of pins for the Pro Mini's left side (J4). The J5, J6, and J7 holes remain empty — Step 7 will solder flying-wire ends directly into them.

### Step 5 — Solder the mode-select jumper pins and install shunts

**Errata-revised (2026-05-19): the J8/J9/J10 hardware install is unchanged, but the `CON1`/`CON2`/`CON3` nets are not routed to the module footprint. You'll wire each `CON` pin from the module to the middle pin of its jumper in Step 7.**

Three 3-pin headers: J8, J9, J10. These set the DY-SV17F into IO-trigger mode.

Solder each 3-pin header exactly like the module headers in step 4 — one pin at a time, verify vertical, finish the remaining pins.

Per pad data from the PCB (confirmed via the KiCad MCP), each jumper is wired:

| Header | Pad 1 (left) | Pad 2 (middle) | Pad 3 (right) |
|---|---|---|---|
| J8  | GND | /CON1 | /V33 |
| J9  | GND | /CON2 | /V33 |
| J10 | GND | /CON3 | /V33 |

So a shunt across pads 1–2 ties that `CON` pin to GND; a shunt across pads 2–3 ties it to V33.

DY-SV17F mode configuration (see `v2/README.md` §3 if you want the rationale): set the jumpers so the module interprets a falling pulse on its IO1 pin as "play track 001 once, then stop and wait." For the common DY-SV17F revision, that's `CON1 = GND`, `CON2 = V33`. `CON3` doubles as the BUSY output, so do **not** shunt J10 to either rail — leave J10 unshunted (the BUSY output drives it directly). The flying wire from the module's left-side pin 7 (CON3/BUSY) handles both the mode-pin sample at boot (high impedance ≈ floating, which selects one of the IO-trigger sub-modes per datasheet) and the BUSY readout.

* J8 → shunt pads 1–2 (CON1 ↔ GND).
* J9 → shunt pads 2–3 (CON2 ↔ V33).
* J10 → no shunt. The module's CON3/BUSY pin floats during boot-sampling and then drives the line as a BUSY output during playback.

If `CON3` floating gives the wrong mode on your specific module revision (check the silkscreen table on the back of the DY-SV17F), the fallback is a 10 kΩ pull-up or pull-down resistor across J10 pads 2–3 or pads 1–2 respectively, rather than a hard shunt — the resistor lets the module's BUSY output still pull the line during playback.

If you can't find shunts, you can hand-solder a wire bridge between the two pins instead. Less convenient to reconfigure but works fine.

The V33 rail on J8/J9/J10 pad 3 needs a feed too: it comes from the DY-SV17F's left-side pin 5 (V33 output) via a flying wire installed in Step 7.

### Step 6 — Solder the JST-XH 2-pin connectors

Three connectors: J1 (battery), J2 (button), J3 (speaker).

JST-XH 2-pin male headers have two pins on 2.50 mm pitch (slightly narrower than the 2.54 mm of the 0.1″ pin headers — make sure you're using the right ones from the kit). The plastic body has a tall keyed side that the mating female housing can only enter one way, so they're polarity-safe to plug in.

Place each connector so the *open keyed face* points toward the edge of the PCB. That way the mating cable enters from outside the board's bounding rectangle, not back across the PCB.

Procedure, per connector:

1. Insert from the top, long pins down through the bottom.
2. Solder one pin from the bottom side.
3. Verify the connector is flush and the keyed face points outward. If not, reheat and adjust.
4. Solder the other pin.

### Step 7 — Mount the Pro Mini, then hand-wire the DY-SV17F

**Errata-revised (2026-05-19).** The Pro Mini half of this step is unchanged. The DY-SV17F half is rewritten: the module is plugged in on its right side only (into J6) and every left-side signal is run as a flying wire.

#### 7A — Pro Mini (left side via J4, right side hand-wired)

**Errata-revised (2026-05-19, corrected).** The Pro Mini's left side plugs into J4 normally. The right side does not engage J5 — it's trimmed and hand-wired for power.

Pin orientation on J4 (verified via the KiCad MCP — pad nets confirmed):

| J4 pad | Pro Mini pin | Net |
|---|---|---|
| 1 (square pad, top) | `TXO` / `TX1` / `D1` | unrouted |
| 2 | `RXI` / `RX0` / `D0` | unrouted |
| 3 | `RST` | unrouted |
| 4 | `GND` | /GND |
| 5 | `D2` | /BTN_IN |
| 6 | `D3` | unrouted |
| 7 | `D4` | unrouted |
| 8 | `D5` | /GATE_CTRL |
| 9 | `D6` | /TRIG_OUT |
| 10 | `D7` | /BUSY_IN |
| 11 | `D8` | unrouted |
| 12 (bottom) | `D9` | unrouted |

So the Pro Mini's `TXO` pin sits on J4 pad 1 (the square pad). The FTDI 6-pin header overhangs the *top* edge of the PCB (so an FTDI cable plugs in without removing the module).

Procedure:

1. **Before placing the Pro Mini on the board**: trim the Pro Mini's right-side pin header flush with the Pro Mini's PCB. The cleanest way is to snap or cut off the right-side male pin strip entirely *before* soldering it to the Pro Mini, if it isn't already on. If it's already soldered on, clip each pin flush with diagonal cutters so nothing protrudes below the Pro Mini's PCB on the right edge. The Pro Mini's right-side solder pads (with the `RAW`, `GND`, `RST`, `VCC`, `A3`–`A0`, `D13`–`D10` silkscreen labels) remain accessible from the *top* — those are the wire-anchor pads for sub-step 7A-bis below.
2. Position the Pro Mini above J4's upward-pointing pins, with the left-side solder pads of the Pro Mini aligned over J4's twelve pins. The `TXO` pad of the Pro Mini must be over J4 pad 1 (the square pad at the top). The FTDI 6-pin programming header overhangs the top edge of the PCB.
3. Press the module down so J4's pins protrude through the Pro Mini's left-side pads. The Pro Mini's *right-side* edge hangs out unsupported (because J5 has no pins). That's expected.
4. Solder J4 pad 1 (the `TXO` pin) from the top of the Pro Mini. Verify flush against J4's plastic spacer.
5. Solder J4 pad 12 (the `D9` pin) — the diagonal corner. Verify flush.
6. Solder the remaining ten J4 pins from the top of the Pro Mini.
7. **Then flip the assembly over and solder each of those twelve pins from the bottom of the main PCB as well.** This is the "soldered on both sides" requirement — it doubles the mechanical attachment for J4.
8. Right back-up the cantilevered right side of the Pro Mini with a hot-glue blob between the Pro Mini's bottom-right edge and the PCB top. The glue is structural — J4 alone can't take a drop without the right side levering off.

#### 7A-bis — Pro Mini power flying wires (2 wires)

Two more flying wires, one for `RAW` and one for `VCC`:

| # | Pro Mini solder pad | PCB landing point | PCB net | Purpose |
|---|---|---|---|---|
| P1 | **`RAW`** (top of right edge — first pad from the FTDI end) | **J5 pad 12** at (30.24, 35.94) | /VSYS | Battery feed to the Pro Mini |
| P2 | **`VCC`** (4th from top on right edge) | **J5 pad 11** at (30.24, 33.4) | /V33 | Pro Mini's 3.3 V regulator output going to the V33 rail |

Procedure per wire — same as the DY-SV17F flying wires in Step 7C:

1. Pre-tin the Pro Mini's `RAW` (or `VCC`) solder pad with a small bead of solder.
2. Pre-tin the wire end. Touch it to the Pro Mini pad; reflow the bead. The wire fuses onto the pad.
3. Route the wire across the PCB top to the J5 destination hole.
4. Insert the other wire end into the J5 hole from the top; solder from the bottom; trim flush.
5. Hot-glue the wire bundle at the Pro Mini end and at the PCB end for strain relief.

After Steps 7A and 7A-bis, the Pro Mini is mechanically anchored to J4 + hot glue, electrically connected to the board via J4's twelve pins + two power flying wires, and the right-side digital pins (`D10`–`D13`, `A0`–`A3`, `RST`, `GND`) hang in the air un-soldered (which is correct — none of them are used by the v2 firmware).

#### 7B — Mount the DY-SV17F off-PCB

The module does not plug into either J6 or J7. The bottom of the case (or the side of the case if there's space) is the new home:

1. Pick a flat spot inside the case that's clear of the PCB outline and the speaker. Roughly 30 × 25 mm of clearance is enough.
2. Hot-glue the DY-SV17F to that spot, component side facing up so the USB pads are accessible for re-loading the audio file. Orient with the pin-headers projecting toward the PCB — you want short flying wires, not long ones snaking across the case.
3. Confirm the unit can still close — the DY-SV17F is ~5 mm tall plus another ~3 mm of pin headers below it, so the chosen spot needs ~10 mm of vertical clearance below the case lid.

The module's two 9-pin headers (already soldered on, projecting downward) are now wire-anchor terminals. They don't go into PCB holes; they hang in the air below the module and you'll solder flying wires to the sides of the pin tips.

#### 7C — DY-SV17F flying wires (the ten hand-wired signals)

Use ~28 AWG silicone-insulated stranded hookup wire. Pre-cut to ~60 mm lengths (long enough to reach the PCB from wherever you hot-glued the module in 7B — adjust to fit your case layout). Strip and tin 2 mm at each end.

Each wire goes from one of the DY-SV17F's pin-header tips (used as a terminal post — tin and solder to the side of the pin) to a routed hole on the PCB. Coordinates below are the (x, y) mm position on the PCB top side, in case the silkscreen reference designator has gotten obscured by flux.

**The ten wires:**

| # | Module pin (location on DY-SV17F) | PCB landing point | PCB net | Purpose |
|---|---|---|---|---|
| 1 | Right side pin 2 (`RX/IO1`) | **J6 pad 2** at (55, 7.54) | /TRIG_OUT | Trigger pulse from Pro Mini D6 |
| 2 | Right side pin 9 (`GND`, bottom of right column) | Any GND hole — **J7 pad 3** at (72.78, 10.08) is closest | /GND | Module ground reference |
| 3 | Left side pin 1 (`SPK+`, top) | **J7 pad 8** at (72.78, 22.78) | /SPK_P | Speaker output + |
| 4 | Left side pin 2 (`SPK-`) | **J7 pad 7** at (72.78, 20.24) | /SPK_N | Speaker output − |
| 5 | Left side pin 5 (`V33`) | **J8/J9/J10 pad 3** (any of them — all are the same /V33 net; J10 pad 3 at (70.08, 50) is closest) | /V33 | Feeds the V33 rail to the mode-select jumpers |
| 6 | Left side pin 6 (`V5`) | **J7 pad 2** at (72.78, 7.54) | /VDFP | Module power input (gated by Q1) |
| 7 | Left side pin 7 (`CON3/BUSY`) | **J7 pad 5** at (72.78, 15.16) | /BUSY_IN | BUSY readout to Pro Mini D7 (this pin also samples its mode-select state at boot from being un-shunted on J10) |
| 8 | Left side pin 8 (`CON2`) | **J9 pad 2** at (57.54, 50) | /CON2 | Mode-select CON2 to its jumper |
| 9 | Left side pin 9 (`CON1`, bottom) | **J8 pad 2** at (47.54, 50) | /CON1 | Mode-select CON1 to its jumper |

Optional tenth wire — only if you want the BUSY-readout path *and* CON3 mode-select to be tied together:

| 10 | Left side pin 7 (`CON3/BUSY`) also runs to | **J10 pad 2** at (67.54, 50) | /CON3 | Bonds the BUSY line to the CON3 jumper net (the two PCB holes carrying `/BUSY_IN` and `/CON3` are not on the same net by default; you're creating that bond with this wire) |

Wire #10 is only needed if your DY-SV17F revision boots into the wrong mode with CON3 floating. If wire #7 already gets you "press button → play once → stop" behavior at bring-up, omit wire #10. If you see continuous looping or no playback, add wire #10 and try the J10 shunts described in Step 5.

Right-side pins 1 (`TX/IO0`) and 3–8 (`IO2`–`IO7`) and left-side pins 3 (`DACL`) and 4 (`DACR`) are intentionally left disconnected.

**Procedure per wire:**

1. Pre-tin the module pin tip with a tiny bead of solder. Pre-tin the wire end.
2. Touch the wire end to the side of the pin tip; reflow the bead. The wire should fuse onto the side of the pin without sliding off.
3. Route the wire across the case toward the destination PCB hole. Keep the bundle reasonably tight; ten loose wires that flop around will fatigue at the solder joints under drops.
4. Insert the other wire end into the destination PCB hole from the top. Solder from the bottom. Trim flush.
5. After all wires are in place, dab a bead of hot glue along the bundle at the module end and at the PCB end. The glue is structural strain relief — it stops a wire from peeling off its module-pin tip when the unit is dropped.

After Step 7C, the DY-SV17F is mechanically anchored to the case via the hot-glue blob from 7B, and the flying wires are all in shear (not tension) at both ends. That is correct.

### Step 8 — Build the external cables

Three cables, all using the pre-crimped JST-XH wires from the connector kit:

* **Battery cable.** Cut the battery holder's red and black flying leads to ~10 cm length. Strip 5 mm from each. Crimp the female JST-XH terminals onto the stripped ends (if the kit shipped pre-crimped wires instead, just splice them with a small soldered joint and heatshrink). Insert into a JST-XH 2-position female housing: red wire into pin 1 (this becomes `VBATT` when plugged into J1), black wire into pin 2 (`GND`). Press the latches in until they click.

* **Button cable.** The EG STARTS dome button has four spade terminals on the back. Two 4.8 mm spades go to the microswitch (the click-switch behind the dome — the actual button function). Two 6.3 mm spades go to the LED (12 V, intentionally unused). Wire two ~15 cm lengths of 22 AWG hookup wire onto the *microswitch* spades only — one to `COM`, one to `NO` ("normally-open"). Most EG STARTS units label these on the metal housing of the microswitch. The other ends of the two wires get JST-XH female crimps and go into a 2-pin housing. `NO` → pin 1 (becomes `BTN_IN`), `COM` → pin 2 (`GND`).

* **Speaker cable.** Two ~10 cm wires from the Adafruit speaker terminals to a JST-XH 2-pin female housing. The speaker has no polarity for our purpose (mono playback). However, *do not* swap or cross the wires from one position into another between assembly attempts; if you eventually pair the device with another for stereo you want a consistent convention.

Tug-test each crimp before plugging anything in. A bad crimp will look fine and fail intermittently after a drop.

### Step 9 — Load the audio file onto the DY-SV17F

The DY-SV17F has 4 MB of onboard flash that the module exposes as a USB mass-storage device when you plug it in.

Procedure:

1. Prepare the audio file on your PC. Source the "Ah! My groin!" clip (or whatever you want to play) and export it as `0001.mp3`, mono, 48 kHz, 128 kbps. Audacity (Effect → Resample → 48000; Tracks → Mix → Mix Stereo Down to Mono; File → Export → MP3) does this fine. The filename matters — DY-SV17F plays the lowest-numbered file in its directory listing when triggered.
2. Plug a USB cable from your PC into the DY-SV17F. Some module revisions have an on-board USB-A connector you plug directly into a USB-A port via a short cable; others have a 4-pad area marked `D+` `D−` `5V` `GND` that you connect with bare wires to a hacked-up USB cable. Check yours.
3. The module will enumerate as a removable USB drive on your PC.
4. Copy `0001.mp3` to the root of the drive.
5. Right-click the drive and choose "Eject" before unplugging — this matters; on most operating systems an un-ejected USB drive can leave the file system half-written.
6. Unplug the USB cable.

The audio is now on the DY-SV17F's flash and will play whenever IO1 is pulsed LOW (the firmware will do this in step 10).

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
* the four module headers and the three connectors are vertical (not leaning), with each pin showing a clean fillet on both top and bottom;
* the two modules are seated flush against their bottom headers with both top and bottom solder joints visible.

If you see a bridge (a glob of solder spanning two adjacent pads or legs), fix it now: flux, press solder wick onto the bridge, lift wick when it absorbs the solder.

#### 11.2 Continuity check, unpowered

Multimeter in continuity-beep mode. Probe between each pair below; a beep means a short.

**Errata-revised (2026-05-19):** DY-SV17F pin numbers below now reference the *real* pinout (right side: `TX/IO0`, `RX/IO1`, `IO2`, `IO3`, `IO4`, `IO5`, `IO6`, `IO7`, `GND`; left side: `SPK+`, `SPK-`, `DACL`, `DACR`, `V33`, `V5`, `CON3/BUSY`, `CON2`, `CON1`). For each "DY-SV17F X" probe below, touch the tinned tip of the corresponding module pin.

* `VBATT` (J1.1) ↔ `GND` (J1.2) — should *not* beep. If it does, you have a short on the battery rail — find and fix it before applying power.
* `VSYS` (Q3 drain pad) ↔ `GND` — should not beep. May read tens of kΩ on the resistance scale from the R2 pull-up and various module input pins; that's fine.
* `VDFP` (J7 pad 2) ↔ `GND` — should not beep.
* J1.1 ↔ Q3 source — should beep (this is the battery feed through the reverse-polarity FET).
* Pro Mini `RAW` solder pad ↔ Q3 drain — should beep (the `VSYS` net is reached via flying wire P1 to J5 pad 12).
* Pro Mini `VCC` solder pad ↔ J8 pad 3 — should beep (the V33 rail via flying wire P2 to J5 pad 11; J8 pad 3 is also on /V33).
* J5 pad 11 ↔ J5 pad 12 — should *not* beep (these are two different nets, V33 and VSYS; they only become electrically distinct because flying wires P1 and P2 are correctly placed).
* DY-SV17F left-side pin 6 (`V5`) ↔ Q1 drain — should beep (the `VDFP` flying wire to J7 pad 2 to Q1, gated).
* DY-SV17F right-side pin 2 (`RX/IO1`) ↔ Pro Mini D6 — should beep (wire #1 lands on J6 pad 2, which carries `TRIG_OUT`).
* DY-SV17F left-side pin 7 (`CON3/BUSY`) ↔ Pro Mini D7 — should beep (the `BUSY_IN` flying wire to J7 pad 5).
* DY-SV17F right-side pin 9 (`GND`, overhanging J6's bottom edge) ↔ J1.2 — should beep (the ground flying wire).
* DY-SV17F left-side pin 5 (`V33`) ↔ J8 pad 3 — should beep (the V33 flying wire feeds the jumper rail).
* DY-SV17F left-side pin 1 (`SPK+`) ↔ J3 pad 1 — should beep (speaker output + via J7 pad 8).
* DY-SV17F left-side pin 2 (`SPK-`) ↔ J3 pad 2 — should beep (speaker output − via J7 pad 7).

If anything that should beep doesn't, you have an open joint somewhere on that net — reflow the joints at both ends.

#### 11.3 First power, current-limited

If you own a bench supply: set it to 4.5 V, current limit 100 mA, and connect across J1 (red lead to J1.1, black to J1.2). Power on. Watch the current — it should jump briefly (charging C1) and then settle below 10 mA. If it hits the 100 mA limit, kill the supply immediately and re-inspect — you have a short somewhere.

If you don't own a bench supply: use the FTDI cable from step 10 as your power source. The cable provides 3.3 V at the Pro Mini's `VCC` pad; this bypasses Q3 and the battery, but it does test the Pro Mini and (via D5 gate control + Q1) the DY-SV17F. Skip the reverse-polarity test (11.4) since the FTDI doesn't go through Q3.

#### 11.4 Reverse-polarity test (bench supply only)

Reverse the bench supply leads on J1. Confirm current stays at zero and `VSYS` stays at 0 V (Q3 is doing its job). Restore correct polarity.

#### 11.5 Per-rail voltage check

With the supply on at 4.5 V, probe with the multimeter (DC volts, 20 V range):

* `VSYS` (Q3 drain pad): should read ~4.5 V minus a few millivolts.
* `VDFP` (DY-SV17F V5 pin): should read 0 V at rest. The firmware holds D5 LOW until the button is pressed, so Q1 is off and the DY-SV17F is unpowered.
* Pro Mini onboard power LED: lit.

If `VDFP` reads ~`VSYS` while the firmware should be holding D5 LOW, suspect Q4 (NPN level shifter) is installed backwards or R1 is the wrong value.

#### 11.6 First end-to-end action

Plug in the speaker, button, and battery cables (or keep the bench supply if you're not on batteries yet). Press the button.

Expected: ~50 ms after the press, the DY-SV17F powers up; ~100 ms later it starts playing `0001.mp3` through the speaker. When the clip ends (DY-SV17F BUSY goes HIGH again), the firmware powers down the module and returns to deep sleep.

#### 11.7 Sleep current

With the device idle (audio finished), the current at the battery input should be under 1 mA. With a Fluke-class meter you can resolve it to ~10 µA. If you see anything like 10 mA idle, the Pro Mini's onboard power LED is the culprit — the v1 docs used to call for desoldering it, but on a 3 × AA battery that LED's continuous 3 mA still gives months of life, so you can leave it if you don't care about absolute longevity.

#### 11.8 Conformal coating (optional)

If you want the unit to survive a glass of water spilled near it, spray the populated board with MG Chemicals 419D acrylic coating per the can's directions. Mask the JST-XH housings, the Pro Mini's FTDI header, and the DY-SV17F's USB pads with painter's tape first — these are the ports you might want to access again. One light coat, dry 30 minutes, then a second light coat.

### Step 12 — Final assembly into the case

The printed case is two parts: `body.stl` (the top + four sides) and `bottom.stl` (the removable tray with the speaker grille and four feet).

1. Press M3 brass heat-set inserts into the four corner bosses inside the case body. Use the soldering iron with a smooth conical tip at 250 °C, pressing each insert in vertically until its top is flush with the boss top. Let cool.
2. Mount the EG STARTS button through the 88 mm hole in the case top, securing it with the supplied threaded ring on the inside.
3. Screw the populated PCB to the four PCB-standoffs that project up from the bottom tray (`bottom.stl`). The PCB has its M3 mounting holes at the corners (H1–H4) which align with the tray's standoffs.
4. Set the Adafruit speaker on the four speaker-mounting bosses around the speaker grille on the tray, secured with the small M3 hardware that came with the speaker.
5. Slot the 3 × AA battery holder into the U-shaped rib pocket on the tray. The holder's switch lever should face outward (toward the right end-wall of the tray) so it's reachable through the case.
6. Plug each cable:
   * Battery cable from holder → J1 on the PCB.
   * Button cable from dome → J2.
   * Speaker cable → J3.
7. Lift the populated tray up into the case body from below. The four corner blocks inside the body should align with the four holes in the tray.
8. Drive the four M3 × 25 mm countersunk screws up through the tray's countersunk holes (which now include 8 mm of foot depth) into the heat-set inserts in the body. Tighten just until firm — over-torquing splits the plastic.

Done.

## Validation and Acceptance

The device is acceptable when:

* Pressing the dome button once produces audible playback of `0001.mp3` through the speaker, within ~250 ms.
* The audio plays cleanly to the end without stutter or repeat-trigger.
* Pressing the button again during playback does not crash, double-trigger, or queue a second play (the firmware ignores presses while BUSY).
* With the device sitting idle, the on/off switch on the battery holder cuts all current draw (you can verify by removing one battery — the device should be undamaged when reinserted regardless of orientation, courtesy of Q3 reverse-polarity protection).
* The unit survives a 1 m drop onto carpet without losing function. Check after drop with another button press.
* The unit's idle current with the holder switch on is under 1 mA (under 100 µA if you removed the Pro Mini power LED).

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

* Step 9: re-loading the MP3. You can change the audio file by repeating step 9 with a different `0001.mp3` later.
* Step 10: re-flashing the firmware. You can iterate on `v2/firmware/main.cpp` and reflash any number of times.
* Step 11: bring-up. Power up, measure, power down. Repeat as needed.

If you damage the PCB beyond rework — e.g. a torn-off pad — you have four other boards from the 5-board JLCPCB batch. Start over on a fresh one; the BOM has spare parts.

## Artifacts and Notes

Reference files in the repo, with their purpose:

* `kicad/ahmygroin.kicad_sch` — open in KiCad 10's Eeschema to look at the schematic. The connection tables in `v2/README.md` §4 are derived from this and are accurate.
* `kicad/ahmygroin.kicad_pcb` — open in KiCad 10's Pcbnew to look at the layout. `View → 3D Viewer` shows the populated board.
* `kicad/fab/render-top.png` and `render-bottom.png` — KiCad-generated renders of the bare board.
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

    D2  INPUT_PULLUP  Button input. FALLING-edge interrupt wakes from sleep.
    D5  OUTPUT        DY-SV17F power-gate via Q4 → Q1 high-side P-MOSFET.
                      HIGH = DY-SV17F powered; LOW = DY-SV17F off.
    D6  OUTPUT        DY-SV17F IO1 trigger. Held HIGH at rest; pulsed LOW
                      for 20 ms to trigger track 001.
    D7  INPUT_PULLUP  DY-SV17F BUSY input. LOW = module is playing.

For electronics: at the end of step 7, the following nets must be electrically continuous and otherwise isolated:

    VBATT  — J1.1 → Q3.S
    VSYS   — Q3.D → U1.RAW, Q1.S, C1+, C2+, C3+ (test point on top silkscreen)
    VDFP   — Q1.D → U2.V5(pin 15), C4+, C5+, C6+
    GND    — J1.2 → ground pour on F.Cu and B.Cu (everything else)
    BTN_IN — J2.1 → U1.D2
    TRIG_OUT — U1.D6 → U2.IO1(pin 2)
    BUSY_IN  — U2.BUSY(pin 12) → U1.D7
    PFET_GATE — Q1.G → Q4.C → R2 (pull-up to VSYS)
    GATE_CTRL — U1.D5 → R1 → Q4.B

Continuity-check these in step 11.2.

For 3D / mechanical: at the end of step 12, the assembled device must conform to:

    Outer dimensions:    200 × 130 × 90 mm
    PCB position:        right half of tray, on 4 × M3 standoffs
    Battery position:    right half of tray, retained by U-pocket walls
    Speaker position:    left half of tray, on 4 × M3 mounting bosses,
                         firing down through the grille
    Button position:     top-centre of left half of body, 88 mm dia. hole
    Foot clearance:      8 mm of air under the speaker grille

If any of those dimensions are wrong, re-run `case/build_case.py` after editing the constants at the top of the file and re-print the affected STL.

## Revision history

* 2026-05-16 — Initial ExecPlan, derived from the design in `v2/README.md`, the BOM in `v2/bom.md`, the firmware in `v2/firmware/main.cpp`, and the case in `case/build_case.py`. Twelve steps covering full assembly from bare PCB to finished unit. Written to the format defined in `PLANS.md`. — Claude (with user Kelly).
* 2026-05-19 — Added the *Hardware erratum* section after user (Kelly) identified three bugs in the DY-SV17F footprint I designed: wrong pin count (2 × 8 instead of 2 × 9), wrong row pitch (0.7″ DFPlayer-Mini geometry, not DY-SV17F), and J7's nets misaligned with the real DY-SV17F left-side pinout (`SPK+`, `SPK-`, `DACL`, `DACR`, `V33`, `V5`, `CON3/BUSY`, `CON2`, `CON1` top-to-bottom). Also discovered `CON1/CON2/CON3` aren't routed to the module footprint at all. Errata-revised Steps 4, 5, 7, and 11.2. PCB-side header J7 is no longer populated. — Claude (with user Kelly).
* 2026-05-19 (later, after Kelly caught a follow-on error) — Corrected my earlier claim that J6 was salvageable for the trigger signal. I had asserted "module right side plugs into J6, so `RX/IO1` lands on pad 2 (`TRIG_OUT`)" — but the module's right side is physically on the right of the natural mounting orientation, over J7, not J6. No rotation puts `IO1` on J6 pad 2. In the natural orientation, J6 pad 2 lands on the module's left pin 2 (`SPK−`) and J7 pad 2 lands on right pin 2 (`RX/IO1`) — putting 5 V on a digital input, which would damage the module. Re-revised: J6 is also not populated. All ten signals (including `IO1` to J6 pad 2) are flying wires; the DY-SV17F is mounted off-PCB. — Claude (with user Kelly).
* 2026-05-19 (still later — fifth Claude-introduced bug) — Kelly identified that the Pro Mini's J5 power pins are also reversed. The PCB routes `/V33` to J5 pad 11 and `/VSYS` to J5 pad 12 — those are `D11` and `D10` positions on a standard HiLetgo Pro Mini. The actual `VCC` and `RAW` pins are at pad 4 and pad 1 (top of the right side). Plugging in the Pro Mini as designed would short ~4.5 V into `D10` and 3.3 V into `D11` while leaving the Pro Mini's actual power inputs disconnected. Re-revised: J5 is also not populated. The Pro Mini's right-side header pins are trimmed flush so they don't engage J5's holes; two flying wires (P1 = `RAW` → J5 pad 12, P2 = `VCC` → J5 pad 11) carry power. Pro Mini's right side is supported by hot glue under the cantilevered edge. — Claude (with user Kelly).
