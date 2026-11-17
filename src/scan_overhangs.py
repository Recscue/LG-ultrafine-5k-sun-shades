"""Slice a print file every 0.2 mm and report every layer where new material appears more
than LIMIT mm from the layer below (a bridge or ledge a printer can't hold up), with its
position on the bed. This is the check that catches what an island check misses."""
import sys
import warnings

import numpy as np
import trimesh
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

warnings.filterwarnings("ignore")
LIMIT = 3.0


def layer(m, z):
    s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if s is None:
        return None
    p, _ = s.to_planar(to_2D=np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, -z], [0, 0, 0, 1]]))
    polys = [Polygon(x) for x in p.polygons_full if x.area > 0.05]
    return unary_union(polys).buffer(0) if polys else None


bad_files = 0
for f in sys.argv[1:]:
    m = trimesh.load(f)
    # the first two layers sit on the bed (squished onto it), so start comparing above them
    zs = np.arange(0.5, m.bounds[1][2], 0.2)
    prev, hits = layer(m, 0.3), []
    for z in zs:
        cur = layer(m, z)
        if cur is None:
            continue
        if prev is not None:
            new = cur.difference(prev.buffer(0.01))
            for g in getattr(new, "geoms", [new]):
                if g.area < 1.0:
                    continue
                far = max(prev.distance(Point(c)) for c in g.exterior.coords)
                if far > LIMIT:
                    x0, y0, x1, y1 = g.bounds
                    hits.append((round(z, 1), round(far, 1), round(g.area, 1),
                                 f"x {x0:.0f}..{x1:.0f} y {y0:.0f}..{y1:.0f}"))
        prev = cur
    bad_files += bool(hits)
    print(f.split("/")[-1], "OK" if not hits else f"{len(hits)} bad layers")
    for h in hits[:6]:
        print("   z", h[0], "reaches", h[1], "mm out, area", h[2], "mm2,", h[3])
print("files with unprintable overhangs:", bad_files)
