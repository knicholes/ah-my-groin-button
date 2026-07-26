# Ah! My Groin!

A big red arcade button in a 3D-printed box. Hit it, it plays a sound clip,
then it goes back to sleep drawing 150 µA — so a set of AA cells lasts months
rather than days.

This repo is the complete build: PCB design files, firmware, the parametric
case model, a bill of materials with the exact parts used, and a
step-by-step assembly guide written for someone who has not done much
soldering.

---

## What to build

Two things have version numbers and they move independently:

| | Current | Where |
|---|---|---|
| **Board** | v3.2 | `kicad/` |
| **Case** | v2 — 120 × 120 × 140 mm | `case/v2-120x120x140/` |

Everything else in the repo (`ah-my-groin/`, `v2/README.md`'s v1 comparisons,
`case/v1-200x130x110/`) is earlier work kept for reference. You do not need it.

### Honest status

Read this before you spend money.

| Part | State |
|---|---|
| Firmware | **Proven.** Runs on a physically built board. 0.15 mA idle measured 2026-07-25. |
| Power design | **Proven.** The phantom-power drain that made an earlier build useless was found and fixed; idle went 14.44 mA → 0.15 mA. |
| v3.2 PCB | **Designed, not yet fabricated.** Passes `kicad/verify_v3.py`. Nobody has held one of these boards. |
| v2 case | **Designed, not yet printed.** Passes its clearance checks. Nobody has printed one. |

So: the electronics are known to work, but *this specific board revision and
this specific case* are unbuilt. If you build first, you are the pilot. The
verification scripts below exist precisely because earlier revisions shipped
with bugs that KiCad's own DRC passed cleanly.

---

## Specifications

| | |
|---|---|
| Idle current | ~150 µA (0.15 mA measured) |
| Playback current | ~150 mA |
| Power | 3 × AA, 2.4–3.3 V, master switch on the holder |
| Response | ~1 s from press to audio (the audio module's genuine cold-boot time) |
| Audio | DY-SV17F, 4 MB onboard flash, no SD card |
| MCU | Pro Mini 3.3 V / 8 MHz, deep sleep + INT0 wake |
| Board | 90 × 70 mm, 2.0 mm FR4, 2-layer |
| Case | 120 × 120 × 140 mm, all corners and edges rounded |
| Cost | roughly $60–90 depending on what you already own |

---

## Build it

Six stages. Each one points at the document that is authoritative for it —
this README only orients you.

### 1. Order the parts

**[`v2/bom.md`](v2/bom.md)** lists every component with the exact ASIN that
was purchased, plus what each one is for and which ones have gotchas (the Pro
Mini crystal must read 8.000, not 16.000).

### 2. Order the PCB

Gerbers come from `kicad/`. Send to JLCPCB or equivalent: **2 layers,
2.0 mm thickness** (not the default 1.6 — the extra stiffness is deliberate,
an earlier unit failed by flexing on impact).

**Before you order, run the two gates:**

```
"K:\Program Files\KiCad\10.0\bin\python.exe" kicad\verify_v3.py   # must print PASS
"K:\Program Files\KiCad\10.0\bin\python.exe" kicad\fitcheck_v3.py # then print it at 100%
```

`verify_v3.py` checks two classes of bug KiCad's DRC structurally cannot see:
parts buried under a module's overhanging body, and electrical intent
(transistor orientation, pull-downs, the phantom-power split). Every board
revision so far shipped with at least one of these and a clean DRC.

`fitcheck_v3.py` produces a 1:1 sheet. Print it at 100 %, **check the two
100 mm calibration bars with a ruler**, then lay the real DY-SV17F and Pro
Mini on their footprints. This takes five minutes and is the only thing that
catches a wrong footprint pitch. The calibration bars are there because a
printer once silently rescaled the sheet and produced a convincing false
alarm.

### 3. Solder the board

**[`SOLDERING_GUIDE.md`](SOLDERING_GUIDE.md)** — the long one. Twelve steps
from bare PCB to finished unit, written for a beginner: which end of the
resistor, how to hold the iron, how to put a multimeter in series without
shorting the battery pack. It includes the continuity checks to run before
first power-on and the measurements that prove the power design is working.

No wires are soldered anywhere. Every connection is a PCB trace — that was
the entire point of the v3.2 respin.

### 4. Flash the firmware

```
cd v2/firmware
pio run              # build
pio run -t upload    # upload via FTDI cable on the 6-pin header
pio device monitor   # 9600 baud
```

[PlatformIO](https://platformio.org/) handles the toolchain. The firmware is
~60 lines with no libraries — the audio module is driven by one GPIO pulse.
See [`v2/firmware/main.cpp`](v2/firmware/main.cpp); its header comment
documents the pin map and, more usefully, *why* three of the pins are the way
they are. Those three comments are each a bug that cost a debugging session.

### 5. Load the audio

The DY-SV17F appears as a USB mass-storage device. Copy a single MP3 named
`00001.mp3` to it. That is all.

**This repo ships no audio files.** The clip the project is named after is
copyrighted, so supply your own — record something, or use a clip you have
the right to use. Any MP3 works.

### 6. Print and assemble the case

STLs are in **[`case/v2-120x120x140/`](case/v2-120x120x140/)**, and that
folder's `README.md` has per-part print orientations and the constraints that
shaped the design. Three parts: `body.stl` ×1, `bottom.stl` ×1, `foot.stl`
**×4**.

0.4 mm nozzle, 0.2 mm layer, 20 % infill, PLA or PETG. **Check the size your
slicer reports** — `body.stl` must load as 120 × 120 × 140 mm.

Assembly is Step 12 of the soldering guide. Order matters: the speaker's
screws become unreachable once the PCB is mounted.

---

## Repo map

```
README.md              you are here
SOLDERING_GUIDE.md     the build, end to end — the main document
PINOUTS.md             pin and net reference for the board
PLANS.md               the format the guide is written in

kicad/                 v3.2 board — schematic, layout, gerbers
    build_v3.py        generates the board from source
    verify_v3.py       pre-fabrication gate — must PASS before ordering
    fitcheck_v3.py     generates the 1:1 footprint check sheet

v2/
    bom.md             bill of materials — the source of truth for parts
    README.md          why v2's architecture replaced v1's
    firmware/          PlatformIO project; main.cpp is the whole program

case/
    build_v2.py        generates the current case
    render_v2.py       preview renders
    v2-120x120x140/    STLs to print, plus README with print orientations
    build_case.py      generates the older wide case
    v1-200x130x110/    superseded, kept so it still reproduces

ah-my-groin/           v1 firmware (DFPlayer + SD card). Superseded.
```

## Regenerating things

Both the board and the case are generated from scripts, not hand-drawn — so
if you change a dimension, re-run the script rather than editing the output.

```
"K:\Program Files\KiCad\10.0\bin\python.exe" kicad\build_v3.py
"K:\...\blender.exe" --background --python case\build_v2.py
```

The case script refuses to finish if its clearance checks fail, if the button
notches got filled back in by a later boolean, or if the exported STL is not
in millimetres. All three of those are real bugs that happened and shipped
silently.

## Building a different case

Change `W, D, H` and `VERSION` at the top of `case/build_v2.py` and re-run —
outputs land in a new `case/<VERSION>/` folder and the old one is untouched.
The clearance checks will tell you what stopped fitting. Three constraints
are worth knowing before you start, all documented in the v2 case README:
the PCB cannot sit on posts rising straight from the tray, everything
tray-mounted has to pass up through the bottom opening, and the top rim
rounding is what limits the button flange.

## Contributing

Issues and pull requests welcome. If you build one, the most useful thing you
can report is anything in the "not yet fabricated / not yet printed" rows
above turning out wrong.

## License

MIT — see [`LICENSE`](LICENSE). Build it, sell it, modify it, no permission
needed; just keep the copyright notice.

That covers everything in this repo: firmware, the board design, the case
models, and the documentation. It does **not** cover any audio you load onto
the device — no audio ships here, and whatever you add is yours to clear.
