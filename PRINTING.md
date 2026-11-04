# Sun shield for two LG UltraFine 5K monitors

Each monitor gets one continuous faceted panel. It rises 8 in above the top edge, continues 7 in past the monitor's outer side and reaches 5 in below the top edge there. It's split into printable pieces only along edges of its own triangle facets, and every split is a dovetail, so the seams read as more facet lines and the pieces lock together like a puzzle. Each seam is also a shiplap. The faceted front layer is cut on the dovetail, and the plain 1.2 mm back layer is cut straight, past the end of the dovetail band, so a back layer always covers the gap in the front layer behind it. `check_seams.py` casts about 775,000 rays through the seam bands and found no line of sight through any of them. The two panels meet at a knuckle spine pinned with a length of filament, which follows whatever angle the monitors sit at.

## Test the joints first

Print everything in `print-files/step-1_test-prints/` on one plate before the shield, in the same filament and profile you'll use for the real parts. That's 9 small pieces: the fit-test clip, two fixed pieces and six fit pieces.

At every seam, one piece is exactly nominal and the other carries the whole clearance. So each seam type gets one `fixed_` piece and three `fit_` pieces to try in it, and the clearance in the file name is the real gap at each dovetail face. The notches on each fit piece's edge also mark it:

| Fit piece | Gap at each face | Full shield to print |
|---|---|---|
| 1 notch | 0.10 mm | `print-files/step-2_full-shield/0.10mm_1-notch/` |
| 2 notches | 0.15 mm | `print-files/step-2_full-shield/0.15mm_2-notch/` |
| 3 notches | 0.20 mm | `print-files/step-2_full-shield/0.20mm_3-notch/` |

Press each fit piece into its fixed piece the way the real pieces go together. Pick the tightest that goes together by hand without a mallet and has no visible gap at the front face, then print the whole shield from the matching folder. If the vertical and horizontal results disagree, go with the vertical one, since there are six vertical seams and two horizontal. Never mix folders. If even 0.20 mm is tight, or 0.10 mm is loose, calibrate as below and re-print the test pieces rather than forcing a set.

`src/build_sets.sh` rebuilds all three sets and runs the seam and assembly checks on each.

Printing notes for the fit:
- **Elephant foot compensation:** keep it on in Bambu Studio. Several pieces have a seam starting on the bed, and first-layer squish otherwise flares those tails.
- **XY contour compensation:** if the test pieces all come out tight or all loose, Bambu's [XY Hole / Contour compensation guide](https://wiki.bambulab.com/en/software/bambu-studio/xy-hole-contour-compensation) shows how to calibrate it per filament. Calibrate first, then re-print the test pieces.
- **Dry filament:** wet PETG extrudes unevenly and changes the fit.

## Parts

Each folder in `print-files/step-2_full-shield/` holds a `left-monitor/` and a `right-monitor/` folder with these five parts, numbered from the monitor's outer edge toward the middle:

| Part | What it is |
|---|---|
| `1a_side-extension-top` | Past the monitor's outer side, above the horizontal seam |
| `1b_side-extension-bottom` | Past the monitor's outer side, below the horizontal seam |
| `2_outer` | Outer third |
| `3_middle_monitor-camera-notch` | Middle third, notch over the LG's built-in camera |
| `4_inner` | Inner third with the hinge knuckles. The left one also carries the webcam shelf |

The files are exported standing up. Printing them flat, faceted side up, is also fine and stronger: support marks then land on the back, which faces the sun. Keep supports off the dovetail faces.

## Webcam shelf

The left inner piece carries a 3 mm triangular shelf that reaches 25 mm past the corner where the monitors meet and 45 mm in front of the screens. It tilts down toward you by 18.5°, the angle that points the lens at your eyes when they're level with the screen's center and about 680 mm away. That distance assumes a 30 in deep desk with the stand bases at its back edge. Under the shelf, a criss-cross grid of 2 mm ribs on 13 mm centers carries the camera's weight. The grid's back wall is fused into the saddle's front lip, and its bottom is flush with that lip's bottom edge. The shelf floats above the right shield, and `check_angles.py` confirms nothing collides, spine included, at every angle between the monitors from 0° to 50°. The webcam screws down through a 6.6 mm hole with a standard 1/4"-20 screw from underneath, Use a 1/4" to 3/8" long screw with a head no wider than 14 mm (a button head, or a small thumbscrew). The head sits in a 16 mm pocket in the grid. The camera sits about 25 mm left of the center line. To re-aim it, change `EYE_DIST` or `SCREEN_CENTRE_DROP` in `build.py` and rebuild: the tilt and the shelf height are computed from them.

## Print settings

- **Filament:** PETG or ASA, not PLA. PLA softens around 55 °C in direct sun.
- **Shells and infill:** 0.2 mm layers, 4 walls, 15% infill.
- **Bed adhesion:** a 5–8 mm brim on the tall pieces.
- **Extension corner support:** the extensions stand on their outer edge, so the bottom ~9 mm of the 30 mm corner round overhangs. In Bambu Studio, paint support under just that corner, or use tree supports set to build plate only. Every other part needs no supports.
- **Weight:** about 820 cm³, roughly 1 kg of PETG, per monitor. That's heavy for the monitor's tilt hinge. If the monitor starts tipping forward, set `FIN_T` to 1.8 and `TEX_MAX` to 2.6 and rebuild.

## Assembly

1. For each monitor, lay its four pieces face down on a table and press the dovetails together. The fit is 0.1 mm per side. Add a drop of CA glue per seam if you want it permanent.
2. Lift each panel onto its monitor. The clips slide along the top edge, so slide the panels until the left and right knuckles interleave.
3. Drop a length of 1.75 mm filament, about 200 mm, down through the knuckles from the top. That's the pin.

## Before printing the set

- **Edge thickness:** `EDGE_T` (25 mm) is estimated from the manual drawings. Print the fit test and adjust `EDGE_T` or `CLEAR` until it seats snugly.
- **Monitor angle:** `TOE_DEG` (15°) sets where the spine sits. Measure the straight-line distance between the two monitors' outer front corners, D, and set `TOE_DEG = degrees(acos(D / 1251.2))`. At 15°, D is about 1208 mm (47.6 in). Rebuild with your value before printing the inner pieces. Only the 15° fit has been checked.

## Rebuild

```
.venv/bin/python build.py      # STLs to out/, checks every piece fits the bed
.venv/bin/python preview.py    # preview PNGs, and checks the two spines don't collide
```
