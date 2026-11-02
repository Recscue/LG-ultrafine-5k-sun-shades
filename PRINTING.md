# Sun shield for two LG UltraFine 5K monitors

Each monitor gets one continuous faceted panel. It rises 8 in above the top edge, continues 7 in past the monitor's outer side and reaches 5 in below the top edge there. It's split into printable pieces only along edges of its own triangle facets, and every split is a dovetail, so the seams read as more facet lines and the pieces lock together like a puzzle. Each seam is also a shiplap. The faceted front layer is cut on the dovetail, and the plain 1.2 mm back layer is cut straight, past the end of the dovetail band, so a back layer always covers the gap in the front layer behind it. `check_seams.py` casts about 775,000 rays through the seam bands and found no line of sight through any of them. The two panels meet at a knuckle spine pinned with a length of filament, which follows whatever angle the monitors sit at.

## File names

The print files were renamed so each name says what the part is. The geometry is unchanged (byte-identical copies). Numbers run from the monitor's outer edge toward the middle where the two monitors meet.

| New name | Old name | What it is |
|---|---|---|
| `0_fit-test-clip_print-first.stl` | `p2s_fit_test_clip.stl` | 20 mm slice of the clip, to check the fit first |
| `left_1a_side-extension-top.stl` | `p2s_left_extension.stl` (top half) | Left monitor, part past its outer side, above the horizontal seam |
| `left_1b_side-extension-bottom.stl` | `p2s_left_extension.stl` (bottom half) | Left monitor, part past its outer side, below the horizontal seam |
| `left_2_outer.stl` | `p2s_left_outer.stl` | Left monitor, outer third |
| `left_3_middle_monitor-camera-notch.stl` | `p2s_left_middle-camera.stl` | Left monitor, middle third, notch over the LG's built-in camera |
| `left_4_inner_webcam-shelf_spine.stl` | `p2s_left_inner.stl` | Left monitor, inner third, Logitech webcam shelf and knuckles |
| `right_1a_side-extension-top.stl` | `p2s_right_extension.stl` (top half) | Right monitor, part past its outer side, above the horizontal seam |
| `right_1b_side-extension-bottom.stl` | `p2s_right_extension.stl` (bottom half) | Right monitor, part past its outer side, below the horizontal seam |
| `right_2_outer.stl` | `p2s_right_outer.stl` | Right monitor, outer third |
| `right_3_middle_monitor-camera-notch.stl` | `p2s_right_middle-camera.stl` | Right monitor, middle third, notch over the LG's built-in camera |
| `right_4_inner_spine.stl` | `p2s_right_inner.stl` | Right monitor, inner third, knuckles |

## Test the joints first

Print `stl/test-coupons/` before the full set, in the same filament and process profile you'll use for the real parts. That's 12 small pieces, about 100 g of PETG. They're slices of the real seams, cut straight from the full model, at three clearances. The number of notches on each piece's edge marks its clearance:

| Notches | Clearance per side |
|---|---|
| 1 | 0.10 mm |
| 2 | 0.15 mm (the default the full set is built with) |
| 3 | 0.20 mm |

Each clearance has a horizontal-seam pair (`horiz-top`, `horiz-bottom`) and a vertical-seam pair (`vert-left`, `vert-right`). Press each pair together the way the real pieces go together, sliding the panel face on from the back. Pick the tightest clearance that goes together by hand without a mallet and has no visible gap at the front face. If that isn't 2 notches, rebuild the set with `FIT=0.10` or `FIT=0.20` in front of `python src/build.py`.

Printing notes for the fit:
- **Elephant foot compensation:** keep it on in Bambu Studio. Several pieces have a seam starting on the bed, and first-layer squish otherwise flares those tails.
- **XY contour compensation:** if the coupons all come out tight or all loose, Bambu's [XY Hole / Contour compensation guide](https://wiki.bambulab.com/en/software/bambu-studio/xy-hole-contour-compensation) shows how to calibrate it per filament. Calibrate first, then re-print the coupons.
- **Dry filament:** wet PETG extrudes unevenly and changes the fit.

## Parts

| File | Print | Notes |
|---|---|---|
| `out/fit_test_clip.stl` | 1, first | 20 mm slice of the clip. Push it onto the monitor's top edge before printing anything else |
| `out/left_extension.stl`, `out/right_extension.stl` | 1 each | The part past the monitor's side. 330 mm long, so place it diagonally on the bed (it fits with about 7 mm to spare) |
| `out/left_outer.stl`, `out/right_outer.stl` | 1 each | |
| `out/left_middle-camera.stl`, `out/right_middle-camera.stl` | 1 each | Notch in the front lip over the camera |
| `out/left_inner.stl`, `out/right_inner.stl` | 1 each | Carry the knuckles. Left and right knuckles alternate |

Every STL is already in print orientation, with no supports needed. The dovetail tails print with 60° sides, and the ceiling over each socket is a short bridge.

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
