"""Write the assembled shield and monitors as one GLB for the browser viewer."""
import os
import sys

import numpy as np
import trimesh

sys.path.insert(0, os.path.dirname(__file__))
import build as B
import preview as P

VIEW = os.path.join(os.path.dirname(__file__), "viewer")
COLORS = {"extension": (92, 102, 116), "outer": (98, 108, 122), "middle-camera": (92, 102, 116),
          "inner": (98, 108, 122)}


def colored(tm, rgb, name):
    t = tm.copy()
    t.visual = trimesh.visual.ColorVisuals(t, face_colors=np.tile([*rgb, 255], (len(t.faces), 1)))
    t.metadata["name"] = name
    return t


CAM_W, CAM_D, CAM_H = 98.0, 33.0, 38.0   # MX Brio, approximate (not verified)


def webcam_local():
    """Stand-in MX Brio on the shelf, in the left panel's frame, centred on the hole."""
    z0 = B.WALL + B.SHELF_LIFT + B.SHELF_T + 0.05
    cx, cy = B.MONITOR_W + B.CAM_U, B.CAM_V
    body = trimesh.creation.box([CAM_W, CAM_D, CAM_H - 6])
    body.apply_translation([cx, cy, z0 + 6 + (CAM_H - 6) / 2])
    foot = trimesh.creation.box([40, 26, 6])
    foot.apply_translation([cx, cy + 1, z0 + 3])
    lens = trimesh.creation.cylinder(radius=9, height=2, sections=48)
    lens.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
    lens.apply_translation([cx, cy - CAM_D / 2 - 0.9, z0 + 6 + (CAM_H - 6) / 2])
    yaw = trimesh.transformations.rotation_matrix(B.SHELF_YAW, [0, 0, 1], [cx, cy, 0])
    T = np.vstack([B.tilt_matrix(B.WALL + B.SHELF_LIFT), [0, 0, 0, 1]])
    for m in (body, foot, lens):
        m.apply_transform(yaw)
        m.apply_transform(T)
    return [(body, (40, 42, 46)), (foot, (55, 58, 62)), (lens, (10, 10, 12))]


def webcam():
    return [(P.place(m, -1), c) for m, c in webcam_local()]


def main():
    os.makedirs(VIEW, exist_ok=True)
    # clearance check: webcam vs every shield piece
    worst = 0.0
    for side, parity in ((-1, 0), (1, 1)):
        for n, tm in P.use_frame_pieces(parity).items():
            sm = B.to_manifold(P.place(tm, side))
            for m, _ in webcam():
                worst = max(worst, (sm ^ B.to_manifold(m)).volume())
    print(f"webcam / shield overlap: {worst:.3f} mm3")
    scene = trimesh.Scene()
    for side, parity, tag in ((-1, 0, "left"), (1, 1, "right")):
        for i, (m, col) in enumerate(P.monitor_mesh()):
            rgb = tuple(int(c * 255) for c in P.rgb(col))
            scene.add_geometry(colored(P.place(m, side), rgb, f"monitor_{tag}_{i}"),
                               node_name=f"monitor_{tag}_{i}")
        for n, tm in P.use_frame_pieces(parity).items():
            name = f"shield_{tag}_{n}"
            scene.add_geometry(colored(P.place(tm, side), COLORS[n], name), node_name=name)
    for i, (m, rgb) in enumerate(webcam()):
        scene.add_geometry(colored(m, rgb, f"monitor_cam_{i}"), node_name=f"monitor_cam_{i}")
    # three.js is Y-up: our Z-up -> rotate -90 about X
    scene.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]))
    scene.export(os.path.join(VIEW, "assembly.glb"))
    print("wrote", os.path.join(VIEW, "assembly.glb"))


if __name__ == "__main__":
    main()
