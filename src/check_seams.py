"""Check the shiplap seams: pieces never collide, and no straight line of sight passes
through the shield (front to back) anywhere along a seam."""
import numpy as np
import build as B

parts = B.pieces(0)
names = list(parts)
for a, b in zip(names, names[1:]):
    v = (parts[a] ^ parts[b]).volume()
    print(f"overlap {a} / {b}: {v:.4f} mm3")

union = parts[names[0]]
for n in names[1:]:
    union = union + parts[n]
# Line-of-sight test: sample X across each seam band, Z over the fin, cast along Y
tm = B.to_trimesh(union)
from trimesh.ray.ray_triangle import RayMeshIntersector
ri = RayMeshIntersector(tm)
leaks = 0
total = 0
for x0 in B.SEAMS:
    xs = np.arange(x0 - 3, x0 + B.ROW_H + B.LAP + 3, 0.05)
    zs = np.arange(B.WALL + 1, B.HEIGHT - B.FIN_T - 1, 0.5)
    X, Z = np.meshgrid(xs, zs)
    o = np.c_[X.ravel(), np.full(X.size, -50.0), Z.ravel()]
    d = np.tile([0, 1.0, 0], (len(o), 1))
    hit = ri.intersects_any(o, d)
    leaks += int((~hit).sum())
    total += len(o)
print(f"see-through rays across seams: {leaks} of {total}")
