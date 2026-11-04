"""Lay the real print files out on build plates, as Bambu Studio would get them, and
write viewer/plates.glb. Each plate is a 256 x 256 mm bed with its parts arranged in rows,
standing exactly as the STL files open. Checks every part stays on the bed and that no
two parts on a plate touch."""
import os
import sys

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
SET = os.path.join(HERE, "out", "sets", "2-notch_0.15mm")
COUP = os.path.join(HERE, "out", "coupons")
BED = 256.0
GAP = 8.0          # between parts; Bambu brims can merge, that's fine
PITCH = 400.0      # plates sit side by side along X in the viewer

PLATES = {
    "A": ["left_2_outer", "right_2_outer",
          "left_3_middle_monitor-camera-notch", "right_3_middle_monitor-camera-notch"],
    "B": ["left_4_inner_spine", "right_4_inner_spine", "left_5_webcam-shelf"],
    # 330 mm long: only fits diagonally, standing on its flat outer edge
    "C": [("left_1_side-extension", 45)],
    "D": [("right_1_side-extension", 45)],
    "T": [["fixed_seam", "fit_seam_0.10mm_1-notch"],
          ["fit_seam_0.15mm_2-notch", "fit_seam_0.20mm_3-notch"]],
}
PART_RGB = [(92, 102, 116), (112, 122, 136)]
BED_RGB = (46, 50, 56)


def load(name):
    name, ang = name if isinstance(name, tuple) else (name, 0)
    d = COUP if name.startswith(("fit_", "fixed_")) else SET
    m = trimesh.load(os.path.join(d, name + ".stl"))
    if ang:
        m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(ang), [0, 0, 1]))
    m.apply_translation(-m.bounds[0])          # sit on the bed at the origin corner
    return m


def colored(m, rgb, name):
    m = m.copy()
    m.visual = trimesh.visual.ColorVisuals(m, face_colors=np.tile([*rgb, 255], (len(m.faces), 1)))
    m.metadata["name"] = name
    return m


def layout(rows):
    """Rows along Y; a row is one part or a list placed side by side along X.
    Returns placed meshes and the used footprint."""
    placed, y = [], 0.0
    for row in rows:
        names = row if isinstance(row, list) else [row]
        ms = [load(n) for n in names]
        x, depth = 0.0, 0.0
        for n, m in zip([x[0] if isinstance(x, tuple) else x for x in names], ms):
            m.apply_translation([x, y, 0])
            placed.append((n, m))
            x += m.extents[0] + GAP
            depth = max(depth, m.extents[1])
        y += depth + GAP
    lo = np.min([m.bounds[0] for _, m in placed], axis=0)
    hi = np.max([m.bounds[1] for _, m in placed], axis=0)
    shift = np.array([BED / 2, BED / 2, 0]) - (lo + hi) / 2 * [1, 1, 0]
    for _, m in placed:
        m.apply_translation(shift)
    return placed, hi - lo


def main():
    scene = trimesh.Scene()
    ok = True
    for i, (tag, rows) in enumerate(PLATES.items()):
        placed, size = layout(rows)
        on_bed = all(m.bounds[0][0] >= 0 and m.bounds[0][1] >= 0 and
                     m.bounds[1][0] <= BED and m.bounds[1][1] <= BED and m.bounds[1][2] <= BED
                     for _, m in placed)
        touching = 0
        for a in range(len(placed)):
            for b in range(a + 1, len(placed)):
                A, Bm = placed[a][1].bounds, placed[b][1].bounds
                if np.all(A[0][:2] < Bm[1][:2]) and np.all(Bm[0][:2] < A[1][:2]):
                    touching += 1
        ok &= on_bed and touching == 0
        print(f"plate {tag}: {len(placed)} parts, footprint {size[0]:.0f} x {size[1]:.0f} mm, "
              f"tallest {size[2]:.0f} mm, {'on the bed' if on_bed else 'OFF THE BED'}, "
              f"{touching} overlapping footprints")
        ox = i * PITCH
        bed = trimesh.creation.box([BED, BED, 2.0])
        bed.apply_translation([BED / 2 + ox, BED / 2, -1.0])
        scene.add_geometry(colored(bed, BED_RGB, f"bed_{tag}"), node_name=f"bed_{tag}")
        for k, (n, m) in enumerate(placed):
            m.apply_translation([ox, 0, 0])
            scene.add_geometry(colored(m, PART_RGB[k % 2], f"part_{tag}_{n}"),
                               node_name=f"part_{tag}_{n}")
    scene.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]))
    out = os.path.join(HERE, "viewer", "plates.glb")
    scene.export(out)
    print("wrote", out)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
