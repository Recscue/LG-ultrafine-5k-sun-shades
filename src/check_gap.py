"""Measure the real gap between neighbouring pieces at each seam type. The smallest
in-plane gap should equal JOINT_CLEAR (the clearance the file name promises)."""
import numpy as np
import trimesh
import build as B

P = {n: B.to_trimesh(m) for n, m in B.pieces(0).items()}
pairs = [("outer", "middle-camera"), ("middle-camera", "inner"),
         ("extension", "extension-lower")]
rng = np.random.default_rng(1)
for a, b in pairs:
    A, Bm = P[a], P[b]
    pts, _ = trimesh.sample.sample_surface(A, 60000, seed=1)
    _, d, _ = trimesh.proximity.closest_point(Bm, pts)
    near = d[d < 1.0]
    print(f"{a:14s}| {b:15s}: smallest gap {near.min():.3f} mm "
          f"(target {B.JOINT_CLEAR}), samples near seam {len(near)}")
