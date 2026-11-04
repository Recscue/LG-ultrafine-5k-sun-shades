"""Group each file's steeper-than-45-degree downward faces into connected patches and
report where each patch is, its area, its height above the bed and how wide it is, so a
patch can be told apart: a short bridge (prints) from a real overhang (needs support)."""
import sys

import numpy as np
import trimesh

for f in sys.argv[1:]:
    m = trimesh.load(f)
    n, c = m.face_normals, m.triangles_center
    down = np.where((n[:, 2] < -0.71) & (c[:, 2] > m.bounds[0][2] + 0.3))[0]
    sub = m.submesh([down], append=True) if len(down) else None
    print(f.split('/')[-1])
    if sub is None:
        continue
    for p in sorted(sub.split(only_watertight=False), key=lambda p: -p.area)[:8]:
        if p.area < 20:
            continue
        lo, hi = p.bounds
        ext = hi - lo
        steep = np.degrees(np.arccos(np.clip(-p.face_normals[:, 2], -1, 1))).min()
        print(f"   {p.area/100:5.1f} cm2 at z {lo[2]:5.1f}-{hi[2]:5.1f}  span {ext[0]:5.1f} x {ext[1]:5.1f} mm  "
              f"flattest {90 - steep:4.0f} deg from horizontal")
