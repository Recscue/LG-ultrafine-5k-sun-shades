"""Compare each print file as exported and flipped end for end: list the downward faces
steeper than 45 deg that aren't on the bed, as (area cm2, span mm, height mm)."""
import sys

import numpy as np
import trimesh


def patches(m):
    n, c = m.face_normals, m.triangles_center
    bad = np.where((n[:, 2] < -0.71) & (c[:, 2] > m.bounds[0][2] + 0.3))[0]
    if not len(bad):
        return []
    sub = m.submesh([bad], append=True)
    out = []
    for p in sub.split(only_watertight=False):
        if p.area > 20:
            e = p.extents
            out.append((round(p.area / 100, 1), round(max(e[0], e[1]), 1), round(p.bounds[0][2], 1)))
    return sorted(out, reverse=True)[:4]


R = trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0])
for f in sys.argv[1:]:
    m = trimesh.load(f)
    f2 = m.copy()
    f2.apply_transform(R)
    print(f.split("/")[-1])
    print("   as exported:", patches(m) or "none")
    print("   flipped:    ", patches(f2) or "none")
