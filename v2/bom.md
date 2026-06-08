# Ah! My Groin! v2 — Bill of Materials

This file is the source of truth. Anything in `pcb/bom.csv` is the v1
reference design and can be ignored — including the Digi-Key part numbers
mentioned there.

---

## Actually purchased (2026-05-06)

These are the specific items in hand. Use them for any 3D-modeling,
enclosure-fit, or replacement-order work.

| ASIN | Item | Role |
| --- | --- | --- |
| [B07RS911JD](https://www.amazon.com/dp/B07RS911JD) | HiLetgo Pro Mini 3.3 V / 8 MHz (3-pack) | U1 — already owned. **Verify crystal reads 8.000, not 16.000.** |
| [B01LZMANZ7](https://www.amazon.com/dp/B01LZMANZ7) | EG STARTS 100mm Big Dome arcade button | BTN — already owned. Microswitch only; LED unused. |
| [B0BPSPPW52](https://www.amazon.com/dp/B0BPSPPW52) | DY-SV17F audio module (2-pack) | U2. Bench-test each before soldering. |
| [B07C6XC3MP](https://www.amazon.com/dp/B07C6XC3MP) | LAMPVPATH 3×AA holder w/ on-off switch (4-pack) | BAT. Built-in switch is the master power switch — no SW1 on PCB. |
| [B00XW2NPTG](https://www.amazon.com/dp/B00XW2NPTG) | Adafruit ADA1313 Speaker, 3″ / 8 Ω / 1 W | SPK. |
| [B08RHFLH1K](https://www.amazon.com/dp/B08RHFLH1K) | Todiys 100 pc AO3401A SOT-23 P-MOSFET | Q1, Q3. Same part for both. |
| [B0D69KD677](https://www.amazon.com/dp/B0D69KD677) | 18-value SOT-23 BJT kit, 180 pcs total | Q4. Use the 2N3904 strip (= MMBT3904, SMD code `1AM`). |
| [B09538ZBCR](https://www.amazon.com/dp/B09538ZBCR) | 60-value 0805 SMD resistor kit, 1500 pcs | R1 (10 kΩ), R2 (100 kΩ). |
| [B0F5QB3S8V](https://www.amazon.com/dp/B0F5QB3S8V) | 30-value 0805 SMD ceramic cap kit, 600 pcs | C2, C3, C5, C6 (0.1 µF + 10 µF values). |
| [B0GMKLB2QM](https://www.amazon.com/dp/B0GMKLB2QM) | 24-value electrolytic capacitor kit, 680 pcs | C1 (1000 µF), C4 (100 µF). |
| [B0B77CSH85](https://www.amazon.com/dp/B0B77CSH85) | ALAMSCN JST-XH 2.54 mm connector kit, 30 pairs, includes pin headers + crimped wires | J1, J2, J3. Both PCB-mount male + wire-side female. |
| [B06XWGCKX5](https://www.amazon.com/dp/B06XWGCKX5) | MG Chemicals 419D Acrylic Conformal Coating, 12 oz | Post-assembly reliability coating. |

**Cancelled (do not order)**: ~~B0DFGZC8YZ~~ (Keszoox JST-PH 2.0 mm female-only kit — wrong pitch and missing PCB headers).

**Total spent on v2-new parts**: ~$110.

---

## Original sourcing guide (for reference / future re-orders)

The sections below are the original "what to search for" guide written
before specific items were chosen. Useful if you need to re-order a part
that's been depleted from the kits.

---

## What you already own (no purchase needed)

| Ref | Item                                       | Source                                                       |
| --- | ------------------------------------------ | ------------------------------------------------------------ |
| U1  | HiLetgo Pro Mini 3.3 V / 8 MHz (3-pack)    | [Amazon B07RS911JD](https://www.amazon.com/dp/B07RS911JD)    |
| BTN | EG STARTS 100mm Big Dome arcade button     | [Amazon B01LZMANZ7](https://www.amazon.com/dp/B01LZMANZ7)    |

**Verify on receipt** — HiLetgo Pro Mini's crystal must read `8.000`, not
`16.000`. Some units ship with the wrong 16 MHz crystal on the 3.3 V
board (out of spec, intermittent failures).

---

## Order from Amazon (single cart)

### Audio module

Look for a 2-pack to give yourself a spare in case one DOAs.

- **Search**: [`DY-SV17F audio module`](https://www.amazon.com/s?k=DY-SV17F+audio+module)
- **Specific listings** (try in order, any will work):
  - [B0BPSPPW52](https://www.amazon.com/dp/B0BPSPPW52) — 2-pack
  - [B0F3DJT4X8](https://www.amazon.com/dp/B0F3DJT4X8) — single
  - [B0BXDN1XHY](https://www.amazon.com/dp/B0BXDN1XHY) — JESSINIE 2-pack

Cost: ~$8–12. Bench-test before soldering down.

### Power and audio output

| Ref | Item                                                | Search link                                                                                              | Specific ASINs                                                                                                  | Price |
| --- | --------------------------------------------------- | -------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ----- |
| BAT | 3×AA battery holder w/ on-off switch                | [Amazon search](https://www.amazon.com/s?k=3+AA+battery+holder+with+switch+leads)                         | [B07C6XC3MP](https://www.amazon.com/dp/B07C6XC3MP) (LAMPVPATH 4-pack), [B07JF3DD9Q](https://www.amazon.com/dp/B07JF3DD9Q) (transparent), [B0C5M9XGGV](https://www.amazon.com/dp/B0C5M9XGGV) (Jstincal 2-pack) | ~$7   |
| SPK | 8 Ω, 2 W speaker (any small enclosure-friendly one) | [Amazon search](https://www.amazon.com/s?k=8+ohm+2W+speaker+arduino)                                      | varies                                                                                                          | ~$5   |

The battery holder's built-in switch is the system's master power switch —
that's why the v2 PCB has no SW1.

### Active discretes

| Ref(s)  | Item                                  | Search link                                                                                | Specific ASINs                                                                                                                                                 |
| ------- | ------------------------------------- | ------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Q1, Q3  | AO3401A P-MOSFET, SOT-23, multipack   | [Amazon search](https://www.amazon.com/s?k=AO3401+SOT-23+multipack)                         | [B08RHFLH1K](https://www.amazon.com/dp/B08RHFLH1K) (Todiys 100-pack), [B08LVLLC1V](https://www.amazon.com/dp/B08LVLLC1V) (Chanzon 100-pack), [B097NHPV3H](https://www.amazon.com/dp/B097NHPV3H) (20-pack) |
| Q4      | MMBT3904 NPN BJT, SOT-23 (in assortment kit or single-value pack) | [Amazon search](https://www.amazon.com/s?k=SMD+transistor+assortment+kit+SOT-23)            | [B0D692FVLW](https://www.amazon.com/dp/B0D692FVLW) — 10-value SOT-23 assortment, 10pcs each (includes MMBT3904 marked "1AM" + 9 other useful BJTs), [B0D8VFQBRT](https://www.amazon.com/dp/B0D8VFQBRT) — 100-pack MMBT3904 only, [B07KNTLBCV](https://www.amazon.com/dp/B07KNTLBCV) — 100-pack MMBT3904 only |

Both AO3401A and MMBT3904 are evergreen parts — multiple manufacturers
still produce them. If a specific listing is unavailable, any AO3401A or
MMBT3904 in SOT-23 from any vendor on Amazon will be electrically
identical.

### Passive component kits

These cover every passive value in the BOM and many more — you'll have
stock for the next 10–20 hobby projects.

| Item                                          | Search link                                                                                          | Notes                                                  |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| 0805 SMD resistor assortment kit              | [Amazon search](https://www.amazon.com/s?k=0805+SMD+resistor+kit+assortment)                          | Look for ≥30 values, ≥50 pcs each. BOJACK and JuForAcc are common brands. Need: 10 kΩ, 100 kΩ. |
| 0805 SMD ceramic capacitor kit                | [Amazon search](https://www.amazon.com/s?k=0805+ceramic+capacitor+kit)                                | Need: 0.1 µF and 10 µF.                                |
| Electrolytic capacitor assortment             | [Amazon search](https://www.amazon.com/s?k=electrolytic+capacitor+assortment+kit)                     | Need: 1000 µF / 10 V or higher, and 100 µF / 10 V or higher. |

### Connectors

Three JST-XH 2-pin connectors needed (J1, J2, J3). One kit covers all
three plus dozens of spares.

- **Search**: [`JST XH 2.54mm connector kit`](https://www.amazon.com/s?k=JST+XH+2.54mm+connector+kit+pre-crimped)
- **Specific listings**:
  - [B0DFGZTGSC](https://www.amazon.com/dp/B0DFGZTGSC) — Keszoox 2-pin specific, pre-crimped
  - [B08G17QHSD](https://www.amazon.com/dp/B08G17QHSD) — multi-pin kit, 90 wires
  - [B0F6C7X5CR](https://www.amazon.com/dp/B0F6C7X5CR) — ribbon cable kit
  - [B0CLDC23ZJ](https://www.amazon.com/dp/B0CLDC23ZJ) — JUZITAO multi-pin

Pick whichever is in stock; any of these will fit the JST-XH B2B-XH-A
footprint specified in `v2/README.md` §3.

### Reliability extras (recommended)

| Item                                | Search link                                                                                            | Notes                                            |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------ |
| Conformal coating acrylic spray     | [Amazon search MG Chemicals 419D](https://www.amazon.com/s?k=MG+Chemicals+419D+conformal+coating)       | Or any acrylic conformal coating spray; ~$15.    |

---

## Off-board (not Amazon)

| Item              | Source                       | Price | Notes |
| ----------------- | ---------------------------- | ----- | ----- |
| Custom v2 PCB     | JLCPCB or PCBWay             | ~$15  | 5-board minimum batch; 2-layer, **2.0 mm thickness**, HASL finish. Send the Gerber zip generated per `v2/README.md` §7. |
| Audio file        | YouTube → ffmpeg / Audacity  | $0    | Hans Moleman "Ah! My Groin!" clip; export as `00001.mp3` (five-digit filename, per DY-SV17F datasheet), mono, 48 kHz, 128 kbps. Drag onto DY-SV17F via USB. |

---

## Cost summary

| Category                                                | Cost      |
| ------------------------------------------------------- | --------- |
| Already owned                                           | $0        |
| New parts from Amazon (kits + module + holder + speaker)| ~$95      |
| PCB fab (5-board batch from JLCPCB)                     | ~$15      |
| **First-build total**                                   | **~$110** |
| **Per additional build** (kits already on hand)         | **~$10**  |

---

## Sourcing notes

- **Why search links over specific ASINs**: Amazon listings cycle in and
  out of stock unpredictably. A search link always shows what's currently
  available; a specific ASIN can break overnight. The ASINs above are
  starting points — if any are unavailable, the search link will surface
  current alternatives.
- **The "obsolete Digi-Key parts" you may have seen** are in
  `pcb/bom.csv` (v1) only. v2 doesn't reference Digi-Key at all. Don't
  cross-reference; just use this file.
- **Why kits over singles for SMD passives**: Amazon doesn't realistically
  stock single-value 0805 reels at hobby quantities. Kits cost the same
  per-unit and stock you for future projects.
- **Why one P-MOSFET part for both Q1 and Q3**: AO3401A handles both
  jobs (DY-SV17F gate + reverse-polarity protection). One 50-pack covers
  hundreds of future projects.
- **What's *not* on this BOM and why**:
  - SW1 (slide switch) — replaced by the battery holder's built-in switch.
  - microSD card — DY-SV17F has onboard flash.
  - 1 kΩ series resistor — v2 has no SoftwareSerial, so no need.
  - DFPlayer Mini, Phoenix screw terminals, EG1218 slide switch — all v1
    parts, not used in v2.
