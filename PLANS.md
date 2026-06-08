# Execution Plans (ExecPlans) — Hardware Edition

This document describes the requirements for an execution plan ("ExecPlan"), a design document that a contributor — human or coding agent — can follow to deliver a working feature or system change. This repository is a *hardware* project: the artifacts include not just source code (firmware on an AVR microcontroller) but also schematics, fabricated PCBs, soldered modules, wired connectors, 3D-printed enclosures, and audio assets. ExecPlans here therefore have to speak to all four worlds — firmware, electronics, mechanical/3D, and assembly — without assuming the reader has prior exposure to any of them.

Treat the reader as a complete beginner to this repository: they have only the current working tree and the single ExecPlan file you provide. There is no memory of prior plans and no external context. They may also have **no prior soldering, KiCad, or 3D-printing experience** — say so, or assume nothing.

## How to use ExecPlans and PLANS.md

When authoring an executable specification (ExecPlan), follow PLANS.md *to the letter*. If it is not in your context, refresh your memory by reading the entire PLANS.md file. Be thorough in reading (and re-reading) source material — schematics, BOMs, datasheets, mechanical drawings, the actual PCB file, the firmware — to produce an accurate specification. When creating a spec, start from the skeleton in this document and flesh it out as you do your research.

When implementing an executable specification (ExecPlan), do not prompt the user for "next steps"; simply proceed to the next milestone. Keep all sections up to date, add or split entries in the list at every stopping point to affirmatively state the progress made and next steps. Resolve ambiguities autonomously, and commit frequently. For hardware ExecPlans the "commit" cadence also means: take a photo of the in-progress board, save updated render PNGs of the case, archive the Gerber zip — because git can't replay a physical step the way it can replay a code change.

When discussing an executable specification (ExecPlan), record decisions in a log in the spec for posterity; it should be unambiguously clear why any change to the specification was made. ExecPlans are living documents, and it should always be possible to restart from *only* the ExecPlan and no other work.

When researching a design with challenging requirements or significant unknowns, use milestones to implement proof of concepts, "toy implementations", breadboard mock-ups, or print-and-fit prototypes that allow validating whether the user's proposal is feasible. Read the source of libraries, search datasheets in full, measure existing parts with calipers, and include prototypes to guide a fuller implementation.

## Requirements

NON-NEGOTIABLE REQUIREMENTS:

* Every ExecPlan must be fully self-contained. Self-contained means that in its current form it contains all knowledge and instructions needed for a novice to succeed — including any soldering technique, any pinout, any orientation, any tool, and any unit/measurement they need to recognize.
* Every ExecPlan is a living document. Contributors are required to revise it as progress is made, as discoveries occur, and as design decisions are finalized. Each revision must remain fully self-contained.
* Every ExecPlan must enable a complete novice to implement the feature end-to-end without prior knowledge of this repo *or* of the discipline the plan touches (firmware, electronics, mechanical CAD, or hand assembly).
* Every ExecPlan must produce a demonstrably working behavior, not merely code changes or sub-assemblies that "meet a definition". For hardware, "working" means the user can apply power, take the specified action (e.g. press the button), and observe the specified result (e.g. audio plays).
* Every ExecPlan must define every term of art in plain language or do not use it. This applies double for hardware jargon: "decoupling capacitor", "tinning", "reflow", "RDS(on)", "BUSY pin", "FAT32", "SOT-23 footprint" — none of these are common knowledge.

Purpose and intent come first. Begin by explaining, in a few sentences, why the work matters from a user's perspective: what someone can do after this change that they could not do before, and how to see it working. Then guide the reader through the exact steps to achieve that outcome, including what to edit, what to run, what to solder, what to print, what to wire, and what they should observe.

The agent or human executing your plan can list files, read files, search, run the project, run tests, run KiCad / kicad-cli, run Blender headless, flash firmware with PlatformIO, and operate physical tools. They do not know any prior context and cannot infer what you meant from earlier milestones. Repeat any assumption you rely on. Do not point to external blogs or docs; if knowledge is required, embed it in the plan itself in your own words. If an ExecPlan builds upon a prior ExecPlan and that file is checked in, incorporate it by reference. If it is not, you must include all relevant context from that plan.

## Disciplines in this project

A hardware ExecPlan in this repo will typically span one or more of the following disciplines. Identify which apply at the top of the plan so the reader knows what skills they will exercise.

* **Firmware.** AVR C++ in PlatformIO. Lives in `v2/firmware/`. Built with `pio run`, flashed to a Pro Mini via an FTDI cable on the 6-pin programming header. Define what the firmware does in terms of pin-level behavior (`D2 = button input, internal pull-up, FALLING-edge interrupt`), not in terms of class names alone.
* **Electronics — schematic.** A `.kicad_sch` file plus a netlist export. Source of truth for what is connected to what. When an ExecPlan touches the schematic, name the net (e.g. `VSYS`, `BUSY_IN`) and the affected reference designators (e.g. `J6.12`, `U1.D7`).
* **Electronics — PCB layout and Gerbers.** A `.kicad_pcb` file plus an exported Gerber zip in `kicad/fab/`. When an ExecPlan touches the PCB, name the footprint, the layer (F.Cu, B.Cu, F.SilkS), and the placement coordinate or relative location. Always re-run DRC and re-export Gerbers after any layout change.
* **Hand assembly.** Soldering of SMD passives (0805 resistors and ceramic caps), SOT-23 transistors, through-hole connectors and electrolytic capacitors, through-hole module headers, and wires to JST-XH connectors. ExecPlans that touch assembly must specify *order* (SMD before TH before connectors before wires), *technique* (drag-soldering, tinning a pad first, reflow with hot air), and *verification* (visual under magnification, continuity beep with a multimeter).
* **3D modelling and printing.** Blender Python scripts in `case/build_case.py`, headless-rendered for verification, and exported as STL for slicing. When an ExecPlan touches the case, give dimensions in millimetres, identify which features mate with which physical part (`BTN_HOLE_D = 88.0 mm` mates with the EG STARTS 100 mm Big Dome arcade button), and specify FDM-print tolerances (typically 0.4 mm slip-fit clearance, 0.15 mm interference for press-fits).
* **Audio assets.** WAV → MP3 conversion for loading onto the DY-SV17F over USB. Format: mono, 48 kHz, 128 kbps, filename `00001.mp3` (five-digit name, per datasheet) in the module's flash root.

When a plan touches more than one discipline, dedicate a sub-section to each so a contributor specializing in only one can scope their work cleanly.

## Formatting

Format and envelope are simple and strict. Each ExecPlan must be one single fenced code block labeled as `md` that begins and ends with triple backticks. Do not nest additional triple-backtick code fences inside; when you need to show commands, transcripts, diffs, or code, present them as indented blocks within that single fence. Use indentation for clarity rather than code fences inside an ExecPlan to avoid prematurely closing the ExecPlan's code fence. Use two newlines after every heading, use `#` and `##` and so on, and correct syntax for ordered and unordered lists.

When writing an ExecPlan to a Markdown (.md) file where the content of the file *is only* the single ExecPlan, you should omit the triple backticks.

Write in plain prose. Prefer sentences over lists. Avoid checklists, tables, and long enumerations unless brevity would obscure meaning. Two exceptions where tables and lists are *preferred* in hardware ExecPlans:

1. **Bills of materials.** A table with columns `Ref | Qty | Value | Footprint/Form | Source | Notes` is far more useful than prose.
2. **Connection tables and pin maps.** A table with columns `Pin | Net | Direction | Notes` removes ambiguity that prose cannot.

Checklists are permitted in the `Progress` section, where they are mandatory; they are also permitted in step-by-step assembly walkthroughs ("solder these six 0805 resistors, then check off each one"). Narrative sections must remain prose-first.

## Guidelines

Self-containment and plain language are paramount. If you introduce a phrase that is not ordinary English — "daemon", "filter graph", "decoupling cap", "BJT", "P-MOSFET high-side switch", "FAT32", "reverse-polarity protection" — define it immediately and remind the reader how it manifests in this repository (for example, by naming the files, reference designators, or commands where it appears). Do not say "as defined previously" or "according to the design doc." Include the needed explanation here, even if you repeat yourself.

Avoid common failure modes. Do not rely on undefined jargon. Do not describe "the letter of a feature" so narrowly that the resulting code compiles, board layouts route, or case prints, but does nothing meaningful. Do not outsource key decisions to the reader. When ambiguity exists, resolve it in the plan itself and explain why you chose that path. Err on the side of over-explaining user-visible effects and under-specifying incidental implementation details. For a physical build, "user-visible effect" includes things like *where solder must wick*, *which side of an electrolytic cap is the cathode*, and *which way the FTDI cable plugs in* — all of which a novice will get wrong without explicit guidance.

Anchor the plan with observable outcomes. State what the user can do after implementation, the commands to run, and the outputs they should see. Acceptance should be phrased as behavior a human can verify ("after assembling and powering on, pressing the dome button produces ~2 s of audio through the speaker, then the device returns to <1 mA idle current") rather than internal attributes ("added a `playAudio()` function"). For internal changes, explain how their impact can still be demonstrated (for example, by running tests that fail before and pass after, by measuring battery current with a multimeter, or by observing an oscilloscope trace).

Specify repository context explicitly. Name files with full repository-relative paths, name functions and modules precisely, and describe where new files should be created. If touching multiple areas, include a short orientation paragraph that explains how those parts fit together so a novice can navigate confidently. When running commands, show the working directory and exact command line. When outcomes depend on environment, state the assumptions and provide alternatives when reasonable.

Specify the physical environment when it matters. A hardware ExecPlan must state, when applicable: which tools are required (soldering iron with what tip temperature, multimeter, calipers, hot-glue gun, FTDI USB cable), what consumables (specific solder alloy and diameter, flux, isopropyl alcohol, kapton tape), how the workspace should be set up (ventilation for solder fumes, anti-static mat for sensitive parts, lighting and magnification for fine pitch work), and what reference photos or renders the contributor should have on hand. If a step is hazardous (hot iron, sharp leads, brittle ceramic caps that can shatter, lithium cells), call that out before the step rather than after.

Be idempotent and safe. Write the steps so they can be run multiple times without causing damage or drift. If a step can fail halfway, include how to retry or adapt. If a migration or destructive operation is necessary, spell out backups or safe fallbacks. Prefer additive, testable changes that can be validated as you go. For hardware specifically:

* **Soldering steps are not idempotent** — you can't "undo" a solder joint without desoldering. Make every solder step verify orientation and polarity *before* applying heat.
* **Boolean operations on a 3D model are not idempotent in Blender** — re-running a script can re-cut already-cut holes, leaving non-manifold geometry. Always have the script start from a clean scene (`clear_scene()` in `case/build_case.py`).
* **Gerber files are exported, not edited** — to "fix" a board you re-edit the schematic / PCB and re-export. Don't hand-edit `.gbr` files.
* **Burned components are gone.** A reverse-polarity cell, a shorted rail, or a tantalum cap mounted backwards will let smoke out and destroy the part. The bring-up procedure must inspect every connection at low voltage / current-limited supply before connecting batteries.

Validation is not optional. Include instructions to run tests, to start the system if applicable, and to observe it doing something useful. Describe comprehensive testing for any new features or capabilities. Include expected outputs and error messages so a novice can tell success from failure. Where possible, show how to prove that the change is effective beyond compilation — for firmware via a small end-to-end scenario or an oscilloscope/multimeter measurement; for electronics via an ERC/DRC pass and a current-limited bench-supply bring-up; for mechanical via a render and a print-and-fit; for assembly via the bring-up procedure described in the next section. State the exact commands appropriate to the toolchain (`pio run`, `kicad-cli pcb drc`, `blender --background --python build_case.py`) and how to interpret their results.

Capture evidence. When your steps produce terminal output, short diffs, multimeter readings, or photos, include them inside the single fenced block as indented examples. Keep them concise and focused on what proves success. If you need to include a patch, prefer file-scoped diffs or small excerpts that a reader can recreate by following your instructions rather than pasting large blobs. For physical work, include the *measurement you expect* (e.g. "VSYS should read 4.3–4.5 V with fresh 3×AA cells; if it reads battery voltage minus more than 100 mV, suspect Q3").

## Bring-up: the hardware-specific validation discipline

Bring-up is the staged, multimeter-in-hand process of energising a newly-built board for the first time. Every hardware ExecPlan that produces a fabricated or assembled board MUST include a bring-up section, and it must look like this:

1. **Visual inspection.** Check every solder joint under magnification. Look for bridges (solder spanning two adjacent pads), cold joints (dull, grainy surface), missed pads (no solder at all), tombstoning (a passive lifted vertically by surface tension), and reversed polarised parts (electrolytic caps, diodes, tantalums, ICs).
2. **Continuity check, unpowered.** With a multimeter in continuity mode, verify there is no short between the supply rails and ground. Verify each connector pin connects to the net it should.
3. **First power, current-limited bench supply.** Apply nominal voltage with a current limit set to maybe 100 mA. Watch the supply's current meter as you bring up power — if it hits the limit, kill the supply and re-inspect.
4. **Per-rail voltage check.** Probe each named rail (`VSYS`, `VDFP`, etc.) at its test point. Compare to expected value.
5. **First active operation.** Trigger the simplest end-to-end behavior (button press, LED on, audio on).
6. **Sleep / quiescent current check.** With the device idle, measure current and compare to budget.
7. **Final assembly.** Only after the above passes do you transfer to a real battery and close up the case.

If an ExecPlan skips the bring-up procedure, it is incomplete.

## Milestones

Milestones are narrative, not bureaucracy. If you break the work into milestones, introduce each with a brief paragraph that describes the scope, what will exist at the end of the milestone that did not exist before, the commands to run, and the acceptance you expect to observe. Keep it readable as a story: goal, work, result, proof. Progress and milestones are distinct: milestones tell the story, progress tracks granular work. Both must exist. Never abbreviate a milestone merely for the sake of brevity — do not leave out details that could be crucial to a future implementation.

For a hardware project, useful milestone boundaries often include:

* **Design milestone.** Schematic + BOM + layout-rules finalised; ERC clean; bench-test plan written.
* **Fabrication milestone.** PCB ordered, parts ordered, lead-times tracked.
* **Assembly milestone.** All parts soldered, no shorts on a continuity check.
* **Bring-up milestone.** Per-rail voltages verified, first end-to-end action observed.
* **Enclosure milestone.** Case printed, PCB and components fit, fasteners thread correctly.
* **Field-ready milestone.** Conformal coating applied, drop-test passed, battery life measured.

Each milestone must be independently verifiable and incrementally implement the overall goal of the execution plan.

## Living plans and design decisions

* ExecPlans are living documents. As you make key design decisions, update the plan to record both the decision and the thinking behind it. Record all decisions in the `Decision Log` section.
* ExecPlans must contain and maintain a `Progress` section, a `Surprises & Discoveries` section, a `Decision Log`, and an `Outcomes & Retrospective` section. These are not optional.
* When you discover an unexpected behavior — a manufacturing tolerance that mattered, a clone-module quirk, a Blender boolean that left non-manifold geometry, a solder joint that needed reflow twice, a firmware timing window that was tighter than the datasheet implied — capture it in `Surprises & Discoveries` with short evidence (a screenshot, a measurement, a stack trace, a photo).
* If you change course mid-implementation, document why in the `Decision Log` and reflect the implications in `Progress`. Plans are guides for the next contributor as much as checklists for you.
* At completion of a major task or the full plan, write an `Outcomes & Retrospective` entry summarizing what was achieved, what remains, and lessons learned.

## Prototyping milestones and parallel implementations

It is acceptable — and often encouraged — to include explicit prototyping milestones when they de-risk a larger change. Examples: breadboarding a power-gating circuit before committing it to a PCB layout, printing a single corner of an enclosure to verify wall thickness and fit, scripting a Blender boolean on a stand-in cube to confirm the modifier behaves before applying it to the full case, flashing a "blink-on-button-press" sketch before the full firmware. Keep prototypes additive and testable. Clearly label the scope as "prototyping"; describe how to run and observe results; and state the criteria for promoting or discarding the prototype.

Prefer additive code changes followed by subtractions that keep tests passing. Parallel implementations (e.g. keeping an old PCB revision's bring-up notes alongside the new revision's during migration) are fine when they reduce risk or enable tests to continue passing during a large migration. Describe how to validate both paths and how to retire one safely with tests.

## Skeleton of a Good ExecPlan

    # <Short, action-oriented description>

    This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

    This document is maintained in accordance with `PLANS.md` at the repository root.

    ## Purpose / Big Picture

    Explain in a few sentences what someone gains after this change and how they can see it working. State the user-visible behavior you will enable. For a hardware plan, anchor on the physical end-state: "after following this plan, you will be holding a working device that does X when you do Y."

    ## Disciplines Touched

    List which of {firmware, schematic, PCB, hand assembly, 3D model, audio assets} this plan exercises, so a specialist knows what skills they need.

    ## Progress

    Use a list with checkboxes to summarize granular steps. Every stopping point must be documented here, even if it requires splitting a partially completed task into two ("done" vs. "remaining"). This section must always reflect the actual current state of the work.

    - [x] (2026-05-16 14:00Z) Example completed step.
    - [ ] Example incomplete step.
    - [ ] Example partially completed step (completed: X; remaining: Y).

    Use timestamps to measure rates of progress.

    ## Surprises & Discoveries

    Document unexpected behaviors, bugs, optimizations, mechanical-fit issues, or insights discovered during implementation. Provide concise evidence — a screenshot path, a multimeter reading, a stack trace, a photo filename.

    - Observation: …
      Evidence: …

    ## Decision Log

    Record every decision made while working on the plan in the format:

    - Decision: …
      Rationale: …
      Date/Author: …

    ## Outcomes & Retrospective

    Summarize outcomes, gaps, and lessons learned at major milestones or at completion. Compare the result against the original purpose.

    ## Context and Orientation

    Describe the current state relevant to this task as if the reader knows nothing. Name the key files and modules by full path. Define any non-obvious term you will use. Do not refer to prior plans. For a hardware plan, also describe: what board revision is assumed, what parts are on hand, what tools are needed, and what state the device is in (bare PCB, partially assembled, fully assembled-but-broken, etc.).

    ## Tools, Materials, and Safety

    List the physical tools required (with example models or specs), the consumables (with example part numbers), and the safety notes (ventilation, ESD, hot surfaces, batteries). Omit this section only for plans that touch *only* firmware or *only* the 3D model.

    ## Bill of Materials

    For plans that involve electronics or assembly: table the parts with `Ref | Qty | Value/Form | Footprint/Source | Notes`. Either reproduce the BOM in full or link to a checked-in BOM file (`v2/bom.md`) by exact path — never to an external URL alone.

    ## Plan of Work

    Describe, in prose, the sequence of edits and additions. For each edit, name the file and location (function, module, footprint, mesh object) and what to insert or change. Keep it concrete and minimal.

    ## Concrete Steps

    State the exact commands to run and where to run them (working directory). When a command generates output, show a short expected transcript so the reader can compare. For physical steps, state what the contributor will hold, see, and do. This section must be updated as work proceeds.

    ## Validation and Acceptance

    Describe how to start or exercise the system and what to observe. Phrase acceptance as behavior, with specific inputs and outputs. If tests are involved, say "run `pio test` and expect 12 passed; the new test `<name>` fails before the change and passes after." For hardware, include the bring-up procedure described earlier in this document.

    ## Idempotence and Recovery

    If steps can be repeated safely, say so. If a step is risky, provide a safe retry or rollback path. For hardware: list the consumables you will use up (e.g. one PCB, one set of cells), and which steps are reversible (firmware reflash) vs. irreversible (cutting a wire, drilling a hole, soldering a transistor in the wrong orientation and then desoldering it leaving lifted pads). Keep the environment clean after completion.

    ## Artifacts and Notes

    Include the most important transcripts, diffs, renders, photos, or snippets as indented examples or by reference to paths in the repo. Keep them concise and focused on what proves success.

    ## Interfaces and Dependencies

    Be prescriptive. Name the libraries, modules, services, footprints, mesh-object names, or pin numbers to use and why. Specify the types, traits/interfaces, function signatures, schematic nets, or PCB layers that must exist at the end of the milestone. Prefer stable names and paths such as `v2/firmware/main.cpp:playAudio()`, `kicad/ahmygroin.kicad_sch:VSYS`, or `case/build_case.py:build_tray()`.

    For firmware:

        // In v2/firmware/main.cpp
        void playAudio();   // power up DY-SV17F, pulse IO0, hold for fixed delay, power down

    For electronics:

        Net VSYS — sourced from Q3.D after reverse-polarity protection,
        sinks: U1.RAW (Pro Mini), Q1.S, C1+, C2+, C3+.
        Test point: TP1 on top-left silkscreen.

    For 3D:

        case/build_case.py:build_tray() must return a Blender object named
        "case_tray" with feet at the four corners (centred at
        CORNER_CX × CORNER_CY) projecting downward by FOOT_H mm.

If you follow the guidance above, a single, stateless agent — or a human novice — can read your ExecPlan from top to bottom and produce a working, observable result. That is the bar: SELF-CONTAINED, SELF-SUFFICIENT, NOVICE-GUIDING, OUTCOME-FOCUSED, PHYSICALLY DEMONSTRABLE.

When you revise a plan, you must ensure your changes are comprehensively reflected across all sections, including the living-document sections, and you must write a note at the bottom of the plan describing the change and the reason why. ExecPlans must describe not just the *what* but the *why* for almost everything.

---

## Revision history

* 2026-05-16 — Rewritten for hardware projects. Added discipline taxonomy (firmware / schematic / PCB / assembly / 3D / audio assets), the bring-up section as a non-optional element, tool/material/safety guidance, and concrete examples for each discipline in the Skeleton. Rationale: this repo is not a pure-software project, and an ExecPlan that does not address physical-build concerns will leave a novice stranded after the firmware compiles. — Claude (with user Kelly).
