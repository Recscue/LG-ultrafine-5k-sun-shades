"""Print every patch of new, poorly supported material between two heights of one file,
with its bounds on the bed, to pin down where an overhang the scanner flagged sits."""
import sys
import warnings

import numpy as np
import trimesh
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

warnings.filterwarnings("ignore")
m = trimesh.load(sys.argv[1])
z0, z1 = float(sys.argv[2]), float(sys.argv[3])


def layer(z):
    s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    p, _ = s.to_planar(to_2D=np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, -z], [0, 0, 0, 1]]))
    return unary_union([Polygon(x) for x in p.polygons_full if x.area > 0.05]).buffer(0)


for z in np.arange(z0, z1 + 0.01, 0.2):
    a, b = layer(z), layer(z - 0.2)
    new = a.difference(b.buffer(0.01))
    for g in getattr(new, "geoms", [new]):
        if g.area > 1:
            far = max(b.distance(Point(c)) for c in g.exterior.coords)
            if far > 1.0:
                print(round(z, 1), "area", round(g.area, 1), "reach", round(far, 1),
                      "bounds", [round(v, 1) for v in g.bounds])
