"""Fill GND zones via pcbnew.ZONE_FILLER. Intended to be run in a
subprocess so any SWIG-related segfault on exit doesn't take down the
parent. The actual fill operation works fine on this build; the crashes
documented earlier were in SaveBoard / Python cleanup, not in Fill itself."""
import os, sys
from pathlib import Path
import pcbnew

PCB = Path(r"I:\code\ah-my-groin-button\kicad\ahmygroin.kicad_pcb")

board = pcbnew.LoadBoard(str(PCB))
zones = list(board.Zones())
print(f"loaded {len(list(board.GetFootprints()))} footprints, "
      f"{len(list(board.GetTracks()))} tracks, "
      f"{len(zones)} zones")

# Build a vector<ZONE*> for the filler.
zone_vec = pcbnew.ZONES()
for z in zones:
    zone_vec.append(z)

filler = pcbnew.ZONE_FILLER(board)
ok = filler.Fill(zone_vec, False, None)
print(f"Fill() returned {ok}")

# Save and exit immediately — don't let Python cleanup run.
pcbnew.SaveBoard(str(PCB), board)
print("saved")
os._exit(0)
