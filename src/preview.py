"""Assembly previews and a fit check of the knuckle spine (z-buffer renders)."""
import math
import os
import sys

import numpy as np
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
import build as B
from raster import render

OUT = B.OUT
TOE = B.TOE_DEG


# Rear shell from the LG manual drawings, scaled to the 625.6 x 375.1 x 53.8 mm spec:
# 25 mm at every edge, sloping out on all four sides to a flat back plate
# 305 mm wide x 178 mm tall whose top sits 94 mm below the panel's top edge.
REAR_PLATE_W, REAR_PLATE_H, REAR_PLATE_TOP = 305.0, 178.0, 94.0
MONITOR_D = 53.8


def monitor_shell():
    W, H = B.MONITOR_W, 375.1
    x0, x1 = (W - REAR_PLATE_W) / 2, (W + REAR_PLATE_W) / 2
    z1, z0 = -REAR_PLATE_TOP, -REAR_PLATE_TOP - REAR_PLATE_H
    pts = [(x, y, z) for x in (0, W) for y in (0, B.EDGE_T) for z in (0, -H)]
    pts += [(x, MONITOR_D, z) for x in (x0, x1) for z in (z0, z1)]
    return trimesh.convex.convex_hull(np.array(pts, float))


def monitor_mesh():
    W, H = B.MONITOR_W, 375.1
    panel = monitor_shell()
    back = trimesh.creation.box([1, 1, 1]); back.apply_translation([W / 2, 1, -H / 2])
    screen = trimesh.creation.box([596.7, 1, 335.7]); screen.apply_translation([W / 2, -0.6, -21 - 335.7 / 2])
    neck = trimesh.creation.box([49, 70, 300]); neck.apply_translation([W / 2, MONITOR_D + 34, -H / 2 - 120])
    return [(panel, "#d9d9db"), (back, "#cfcfd2"), (screen, "#1b1f27"), (neck, "#c8c8cc")]


def place(tm, side):
    """Inner front corners of the two monitors touch at the origin."""
    t = tm.copy()
    if side < 0:
        t.apply_translation([-B.MONITOR_W, 0, 0])
        ang = math.radians(TOE)
    else:
        ang = math.radians(-TOE)
    t.apply_transform(trimesh.transformations.rotation_matrix(ang, [0, 0, 1], [0, 0, 0]))
    return t


def use_frame_pieces(parity):
    parts = B.pieces(parity)
    if parity == 1:
        parts = {n: B.mirror_right(m) for n, m in parts.items()}
    return {n: B.to_trimesh(m) for n, m in parts.items()}


def rgb(c):
    return np.array(matplotlib.colors.to_rgb(c))


def save(img, path, title):
    fig = plt.figure(figsize=(img.shape[1] / 160, img.shape[0] / 160), dpi=160)
    ax = fig.add_axes([0, 0, 1, 1]); ax.imshow(img); ax.set_axis_off()
    ax.text(20, 40, title, fontsize=11, color="#333")
    fig.savefig(path, facecolor="white"); plt.close(fig)


def main():
    tones = {"extension": "#6b7684", "extension-lower": "#707b89", "outer": "#707b89",
             "middle-camera": "#6b7684", "inner": "#707b89"}
    items, placed = [], {}
    for side, parity in ((-1, 0), (1, 1)):
        for m, col in monitor_mesh():
            items.append((place(m, side), rgb(col)))
        for n, tm in use_frame_pieces(parity).items():
            p = place(tm, side)
            placed[(side, n)] = p
            items.append((p, rgb(tones[n])))

    # spine fit check at the nominal angle
    a = B.to_manifold(placed[(-1, "inner")])
    b = B.to_manifold(placed[(1, "inner")])
    print(f"spine overlap at {TOE:.0f} deg: {(a ^ b).volume():.3f} mm3")

    save(render(items, eye=(250, -1900, 520), target=(0, 120, -40)),
         os.path.join(OUT, "preview_assembly.png"), f"Both monitors, each turned {TOE:.0f} deg toward you")
    save(render(items, eye=(-500, 1700, 700), target=(0, 0, -20)),
         os.path.join(OUT, "preview_rear.png"), "From behind (sun side): stiffening ribs on the extensions")
    save(render(items, eye=(-140, -420, 260), target=(0, 30, 110), size=(1400, 1100), fov_deg=34),
         os.path.join(OUT, "preview_spine.png"), "Knuckle spine where the monitors meet")
    save(render(items, eye=(-260, -700, 160), target=(-200, 20, 100), size=(1400, 1100), fov_deg=34),
         os.path.join(OUT, "preview_seam.png"), "Dovetail seam between segments, cut along facet edges")


if __name__ == "__main__":
    main()
