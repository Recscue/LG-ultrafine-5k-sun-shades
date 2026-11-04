"""For each print file, try all six 'which face is down' orientations and score each the
way a slicer decides supports: the area of downward-facing surface steeper than 45 deg from
vertical that is not resting on the bed. Also report whether it fits the 256 mm bed."""
import glob
import sys

import numpy as np
import trimesh

BED = 256.0
ROT = {
    "as exported": np.eye(4),
    "flip upside down": trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]),
    "lie on +Y face": trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]),
    "lie on -Y face": trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]),
    "lie on +X face": trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]),
    "lie on -X face": trimesh.transformations.rotation_matrix(-np.pi / 2, [0, 1, 0]),
}


def score(m):
    n, a = m.face_normals, m.area_faces
    zc = m.triangles_center[:, 2]
    down = (n[:, 2] < -0.71) & (zc > m.bounds[0][2] + 0.3)    # >45 deg, off the bed
    on_bed = (n[:, 2] < -0.99) & (zc <= m.bounds[0][2] + 0.3)
    s = m.extents
    fits = s[2] <= BED and (max(s[0], s[1]) <= BED)
    return a[down].sum() / 100, a[on_bed].sum() / 100, fits, s


if __name__ == "__main__":
    for f in sorted(sum((glob.glob(f"{d}/*.stl") for d in sys.argv[1:]), [])):
        base = trimesh.load(f)
        print(f.split("/")[-1])
        for k, R in ROT.items():
            m = base.copy(); m.apply_transform(R)
            sup, bed, fits, s = score(m)
            print(f"   {k:17s} needs support {sup:6.1f} cm2   on bed {bed:6.1f} cm2   "
                  f"{s[0]:4.0f}x{s[1]:4.0f}x{s[2]:4.0f}  {'fits' if fits else 'too big'}")
