"""For a few heights in a print file, find the area that appears with nothing directly
under it and how far its farthest point is from the material below. Short distances are
ordinary bridges or tiny overhangs a printer handles; long ones need support."""
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


f = sys.argv[1]
m = trimesh.load(f)
for z in map(float, sys.argv[2:]):
    above, below = layer(m, z + 0.2), layer(m, z - 0.2)
    new = above.difference(below.buffer(0.01))
    geoms = [g for g in getattr(new, "geoms", [new]) if g.area > 0.5]
    if not geoms:
        print(f"z={z:6.1f}  nothing unsupported")
        continue
    worst = max(max(below.distance(Point(c)) for c in g.exterior.coords) for g in geoms)
    print(f"z={z:6.1f}  unsupported {sum(g.area for g in geoms):6.1f} mm2 in {len(geoms)} patches, "
          f"farthest point {worst:4.1f} mm from support")
