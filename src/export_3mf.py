"""Write one 3MF per print plate, for each joint size, with every part already placed
on a 256 x 256 mm bed exactly as export_plates.py lays them out (and checks them).
Each part stays its own object, so it can still be selected in Bambu Studio."""
import os
import sys

import numpy as np
import trimesh

import export_plates as EP

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "plates")
NAMES = {"A": "plate-A_outer-and-middle", "B": "plate-B_inner-and-webcam-shelf",
         "C": "plate-C_left-side-extension", "D": "plate-D_right-side-extension",
         "T": "test-plate"}


def check(placed):
    on_bed = all(m.bounds[0][0] >= 0 and m.bounds[0][1] >= 0 and m.bounds[1][0] <= EP.BED
                 and m.bounds[1][1] <= EP.BED and m.bounds[1][2] <= EP.BED
                 and abs(m.bounds[0][2]) < 1e-6 for _, m in placed)
    hits = 0
    for i in range(len(placed)):
        for j in range(i + 1, len(placed)):
            A, B = placed[i][1].bounds, placed[j][1].bounds
            if np.all(A[0][:2] < B[1][:2]) and np.all(B[0][:2] < A[1][:2]):
                hits += 1
    return on_bed, hits


def write(placed, path):
    scene = trimesh.Scene()
    for n, m in placed:
        scene.add_geometry(m, geom_name=n, node_name=n)
    scene.export(path, file_type="3mf")


def main():
    ok = True
    sets = sorted(d for d in os.listdir(os.path.join(HERE, "out", "sets")))
    for s in sets:
        EP.SET = os.path.join(HERE, "out", "sets", s)
        d = os.path.join(OUT, s)
        os.makedirs(d, exist_ok=True)
        for tag, rows in EP.PLATES.items():
            if tag == "T":
                continue
            placed, _ = EP.layout(rows)
            on_bed, hits = check(placed)
            ok &= on_bed and hits == 0
            p = os.path.join(d, NAMES[tag] + ".3mf")
            write(placed, p)
            print(f"{s:16s} {NAMES[tag]:34s} {len(placed)} parts  "
                  f"{'on bed' if on_bed else 'OFF BED'}  {hits} overlaps")
    placed, _ = EP.layout(EP.PLATES["T"])
    on_bed, hits = check(placed)
    ok &= on_bed and hits == 0
    write(placed, os.path.join(OUT, NAMES["T"] + ".3mf"))
    print(f"{'(all sizes)':16s} {NAMES['T']:34s} {len(placed)} parts  "
          f"{'on bed' if on_bed else 'OFF BED'}  {hits} overlaps")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
