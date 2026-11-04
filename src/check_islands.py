"""Slice each print file bottom-up like a printer would and report 'islands': any region of
a layer that doesn't touch the layer below and isn't on the bed. Each island would start
printing in mid-air, so it needs support or a different orientation."""
import glob
import sys

import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union

STEP = 0.4
MIN_AREA = 0.5      # mm2, ignore slicing noise


def layer(m, z):
    s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if s is None:
        return None
    p, _ = s.to_planar(to_2D=np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, -z], [0, 0, 0, 1]]))
    polys = [Polygon(x) for x in p.polygons_full if x.area > MIN_AREA]
    return unary_union(polys).buffer(0) if polys else None


def islands(m):
    out = []
    zs = np.arange(m.bounds[0][2] + STEP / 2, m.bounds[1][2], STEP)
    prev = None
    for z in zs:
        cur = layer(m, z)
        if cur is None:
            prev = None
            continue
        if prev is not None and z > m.bounds[0][2] + 1.0:
            grown = prev.buffer(0.6)       # a 0.6 mm step per layer is a printable overhang
            parts = getattr(cur, "geoms", [cur])
            for g in parts:
                if g.area > MIN_AREA and not g.intersects(grown):
                    out.append((round(z, 1), round(g.area, 1)))
        prev = cur
    return out


if __name__ == "__main__":
    files = sorted(sum((glob.glob(f"{d}/*.stl") for d in sys.argv[1:]), []))
    bad = 0
    for f in files:
        isl = islands(trimesh.load(f))
        bad += bool(isl)
        print(f"{f.split('/')[-1]:44s} {'OK' if not isl else f'{len(isl)} islands, first at z={isl[0][0]} mm'}")
    print("files that start in mid-air:", bad)
