"""Report each exported print file's bed footprint and which way its faces point,
to confirm the files are flat with the faceted front face up."""
import glob
import sys
import trimesh

d = sys.argv[1] if len(sys.argv) > 1 else "out/sets/2-notch_0.15mm"
for f in sorted(glob.glob(f"{d}/*.stl")):
    m = trimesh.load(f)
    s = m.extents
    n, a = m.face_normals, m.area_faces
    up = a[n[:, 2] > 0.3].sum() / 100
    dn = a[n[:, 2] < -0.3].sum() / 100
    fits = "fits" if max(s[0], s[1]) <= 256 and s[2] <= 256 else "TOO BIG"
    print(f"{f.split('/')[-1]:44s} {s[0]:4.0f} x {s[1]:4.0f} x {s[2]:3.0f} mm  {fits}  "
          f"faces up {up:5.0f} cm2, down {dn:5.0f} cm2")
