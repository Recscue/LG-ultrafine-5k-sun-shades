"""At one print height, list each unsupported patch of a print file: where it is in the
panel's own frame (Z along the panel, Y through it), its size, and how far its farthest
point is from material below. Print frame: piece X (along the monitor) is up."""
import sys
import warnings

import numpy as np
import trimesh
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

warnings.filterwarnings("ignore")


def layer(m, z):
    s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    p, _ = s.to_planar(to_2D=np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, -z], [0, 0, 0, 1]]))
    return unary_union([Polygon(x) for x in p.polygons_full]).buffer(0)


m = trimesh.load(sys.argv[1])
z = float(sys.argv[2])
above, below = layer(m, z + 0.2), layer(m, z - 0.2)
new = above.difference(below.buffer(0.01))
for g in [g for g in getattr(new, "geoms", [new]) if g.area > 0.5]:
    far = max(below.distance(Point(c)) for c in g.exterior.coords)
    x0, y0, x1, y1 = g.bounds
    print(f"area {g.area:6.1f} mm2  print-x {x0:6.1f}..{x1:6.1f}  print-y {y0:6.1f}..{y1:6.1f}  farthest {far:4.1f} mm")
