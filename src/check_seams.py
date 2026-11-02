"""Check the shiplap seams: no two pieces collide, and no straight line of sight passes
through the shield (front to back) anywhere along a seam, vertical or horizontal."""
import itertools
import numpy as np
import build as B
from trimesh.ray.ray_triangle import RayMeshIntersector

parts = B.pieces(0)
names = list(parts)
for a, b in itertools.combinations(names, 2):
    v = (parts[a] ^ parts[b]).volume()
    if v > 1e-4:
        print(f"overlap {a} / {b}: {v:.4f} mm3")
print("overlaps checked:", len(names) * (len(names) - 1) // 2, "pairs")

union = parts[names[0]]
for n in names[1:]:
    union = union + parts[n]
ri = RayMeshIntersector(B.to_trimesh(union))


def leaks(xs, zs):
    X, Z = np.meshgrid(xs, zs)
    o = np.c_[X.ravel(), np.full(X.size, -50.0), Z.ravel()]
    d = np.tile([0, 1.0, 0], (len(o), 1))
    return int((~ri.intersects_any(o, d)).sum()), len(o)


bad = tot = 0
for x0 in B.SEAMS:
    l, t = leaks(np.arange(x0 - 3, x0 + B.ROW_H + B.LAP + 3, 0.05),
                 np.arange(B.WALL + 1, B.HEIGHT - B.FIN_T - 1, 0.5))
    bad += l; tot += t
l, t = leaks(np.arange(-B.EXT_OVER + 4, -2, 0.5),
             np.arange(B.HSEAM_Z - 3, B.HSEAM_Z + B.HSEAM_TAIL + B.LAP + 3, 0.05))
print(f"see-through rays across seams: {bad + l} of {tot + t}")
