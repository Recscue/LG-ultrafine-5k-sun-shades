"""Sun shield for two LG UltraFine 5K (27MD5KL-B) monitors, printed on a Bambu P2S.

Design idea: the shield is one continuous faceted panel per monitor. It is cut into
printable pieces only along edges of its own triangle lattice, and those cuts form
dovetails, so every seam reads as one more facet edge and the pieces lock in plane
like a puzzle. The two monitors meet at a pinned knuckle spine, which follows any
angle between them.

Frames
- Use frame (left monitor): X across (monitor's outer edge X=0, inner edge X=MONITOR_W),
  Y depth (screen face Y=0, + toward the back), Z up (monitor top edge Z=0).
- The right monitor's parts are the left's mirrored about X = MONITOR_W / 2.
"""
import math
import os

import numpy as np
import trimesh
from manifold3d import CrossSection, Manifold, Mesh, JoinType

# --------------------------------------------------------------------------------------
# Parameters (mm)
# --------------------------------------------------------------------------------------
EDGE_T = 20.0          # monitor thickness at the top edge, measured with calipers 2026-11-04
                       # (LG's drawing implied 25 mm; the real edge is 20)
# The back slopes out to the drawing's 53.8 mm depth at the back plate, 94 mm down
REAR_TAPER_DEG = math.degrees(math.atan((53.8 - EDGE_T) / 94.0))
CLEAR = 0.3
WALL = 2.4
FRONT_LIP = 6.0        # camera centre is ~9 mm below the top edge
REAR_LIP = 40.0
GRIP_NUB = 0.6
FIN_T = 3.0 if os.environ.get("MJF") == "1" else 2.4   # MJF: each lap layer 1.4 mm
HEIGHT = 203.2         # 8 in above the top edge
RIB = 10.0             # top stiffening rib toward the viewer
GUSSET = 8.0

MONITOR_W = 625.6
SEGMENTS = 3
CAM_NOTCH_W = 50.0
INNER_SADDLE_STOP = 8.0  # saddle ends this far short of the inner edge (front corners touch)

EXT_OVER = 177.8       # shield continues this far past the monitor's outer side (7 in)
EXT_DROP = 127.0       # and this far below the top edge, beside the monitor (5 in)
BACK_RIB = 10.0        # stiffening ribs on the sun-facing back of the extension

TOE_DEG = 14.0         # each monitor's turn toward you: measured 152 deg open angle -> (180-152)/2
KNUCKLE_R = 5.0
KNUCKLE_CLEAR = 0.5
KNUCKLE_GAP = 0.5
KNUCKLES = 7
PIN_HOLE_D = 2.0       # a length of 1.75 mm filament is the pin

MJF = os.environ.get("MJF") == "1"   # JLC3DP MJF nylon: looser fits, walls > 1.2 mm
_FIT = os.environ.get("FIT")          # override for the joint test coupons
# Each side of every dovetail seam. Bambu's own calibration guide shows a hole designed at
# 6.0 mm printing at 5.9 mm, with a snug fit at +0.15 mm, so 0.1 mm per side would print
# close to zero clearance. 0.15 is the P2S default; the coupon set tests 0.10-0.20.
JOINT_CLEAR = float(_FIT) if _FIT else (0.2 if MJF else 0.15)
LAP = 6.0              # back layer is cut straight, this far past the dovetail band
LAP_CLEAR = JOINT_CLEAR                # gap between the overlapping layers, front to back
LAP_SPLIT_FROM_FRONT = None   # where the two layers split, from the fin front

# Facets: triangle lattice with vertical row lines h apart; seams sit on row lines
ROW_H = (MONITOR_W / SEGMENTS) / 10       # 20.85 mm
TRI_S = ROW_H / (math.sqrt(3) / 2)        # 24.1 mm edge
TEX_MIN, TEX_MAX = 0.7, 3.4
TEX_FADE = 10.0
JITTER = 0.22
SEED = 7

MAX_BED = 256.0
SEG = 64
OUT = os.environ.get("OUT_DIR") or os.path.join(
    os.path.dirname(__file__), "out_mjf" if os.environ.get("MJF") == "1" else "out")

# Derived
Y_IN_F, Y_IN_B = -CLEAR, EDGE_T + CLEAR
Y_OUT_F, Y_OUT_B = Y_IN_F - WALL, Y_IN_B + WALL
FIN_B = Y_OUT_B
FIN_F = FIN_B - FIN_T
FIN_MID = (FIN_F + FIN_B) / 2
SEG_W = MONITOR_W / SEGMENTS
Z_LO = WALL + GUSSET + 4.0
Z_HI = HEIGHT - FIN_T - 3.0
AXIS_X = MONITOR_W + FIN_MID * math.tan(math.radians(TOE_DEG))
SEAMS = [0.0, SEG_W, 2 * SEG_W]           # extension|outer, outer|middle, middle|inner


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------
def rect(a0, a1, b0, b1):
    return CrossSection([[(a0, b0), (a1, b0), (a1, b1), (a0, b1)]])


def ccw(pts):
    """CrossSection from points in either winding (clockwise input is silently empty)."""
    a = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))
    return CrossSection([pts if a > 0 else pts[::-1]])


def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def yz_extrude(cs, x0, x1):
    """CrossSection in (Y, Z) extruded along X from x0 to x1, in the use frame."""
    m = cs.extrude(x1 - x0)                      # axes (Y, Z, X')
    P = [[0, 0, 1, x0], [1, 0, 0, 0], [0, 1, 0, 0]]
    return m.transform(P)


def xz_extrude(cs, y0=-300.0, y1=300.0):
    """CrossSection in (X, Z) extruded along Y, in the use frame."""
    return cs.extrude(y1 - y0).rotate([90, 0, 0]).translate([0, y1, 0])


def to_manifold(tm):
    return Manifold(Mesh(vert_properties=np.asarray(tm.vertices, dtype=np.float32),
                         tri_verts=np.asarray(tm.faces, dtype=np.uint32)))


def to_trimesh(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts), process=False)


# --------------------------------------------------------------------------------------
# Saddle (clip onto the monitor's top edge), in (Y, Z)
# --------------------------------------------------------------------------------------
def saddle_profile(fin_height=None):
    t = math.tan(math.radians(REAR_TAPER_DEG))
    parts = [
        rect(Y_OUT_F, Y_OUT_B, 0.0, WALL),
        rect(Y_OUT_F, Y_IN_F, -FRONT_LIP, 0.0),
        ccw([(Y_IN_B, 0.0), (Y_OUT_B, 0.0), (Y_OUT_B + REAR_LIP * t, -REAR_LIP),
                       (Y_IN_B + REAR_LIP * t, -REAR_LIP)]),
        ccw([(Y_IN_B + REAR_LIP * t, -REAR_LIP), (Y_IN_B + (REAR_LIP - 4) * t, -REAR_LIP + 4),
                       (Y_IN_B + (REAR_LIP - 2) * t - GRIP_NUB, -REAR_LIP + 2)]),
        ccw([(FIN_F, WALL), (FIN_F - GUSSET, WALL), (FIN_F, WALL + GUSSET)]),
    ]
    if fin_height is not None:
        parts.append(rect(FIN_F, FIN_B, WALL - 0.01, fin_height))
    out = parts[0]
    for p in parts[1:]:
        out = out + p
    return out


# --------------------------------------------------------------------------------------
# Lattice
# --------------------------------------------------------------------------------------
def _hash(a, b):
    v = math.sin(a * 127.1 + b * 311.7 + SEED * 74.7) * 43758.5453
    return v - math.floor(v)


class Lattice:
    """Row lines at X = k*ROW_H; along each row, points every TRI_S in Z, odd rows
    offset by TRI_S/2. Rows that carry a seam are left unjittered."""

    def __init__(self, x_min, x_max, z_min, z_max):
        self.k0 = math.floor(x_min / ROW_H) - 1
        self.k1 = math.ceil(x_max / ROW_H) + 1
        self.j0 = math.floor(z_min / TRI_S) - 1
        self.j1 = math.ceil(z_max / TRI_S) + 1
        fixed = set()
        for x0 in SEAMS:
            k = round(x0 / ROW_H)
            fixed |= {k, k + 1}
        rng = np.random.default_rng(SEED)
        self.rows = {}
        for k in range(self.k0, self.k1 + 1):
            pts = []
            for j in range(self.j0, self.j1 + 1):
                x = k * ROW_H
                z = j * TRI_S + (TRI_S / 2 if k % 2 else 0.0)
                if k not in fixed:
                    x += rng.uniform(-JITTER, JITTER) * TRI_S
                    z += rng.uniform(-JITTER, JITTER) * TRI_S
                pts.append((x, z, k, j))
            self.rows[k] = pts

    def point(self, k, j):
        return self.rows[k][j - self.j0]

    def triangles(self):
        """Flat list of index triples into self.flat()."""
        flat, index = [], {}
        for k in sorted(self.rows):
            for p in self.rows[k]:
                index[(p[2], p[3])] = len(flat)
                flat.append(p)
        tris = []
        for k in range(self.k0, self.k1):
            A, B = self.rows[k], self.rows[k + 1]
            i = j = 0
            while i < len(A) - 1 or j < len(B) - 1:
                if j == len(B) - 1 or (i < len(A) - 1 and A[i + 1][1] < B[j + 1][1]):
                    tris.append((index[A[i][2:]], index[A[i + 1][2:]], index[B[j][2:]]))
                    i += 1
                else:
                    tris.append((index[A[i][2:]], index[B[j + 1][2:]], index[B[j][2:]]))
                    j += 1
        return flat, tris


def seam_polyline(lat, x0):
    """Dovetail seam on the row lines x0 and x0+ROW_H, made only of lattice edges.
    Left piece owns everything at smaller X. Returns (X, Z) points, bottom to top."""
    k = round(x0 / ROW_H)
    xa, xb = k * ROW_H, (k + 1) * ROW_H
    za = [p[1] for p in lat.rows[k]]
    zb = [p[1] for p in lat.rows[k + 1]]
    start = next(z for z in za if z >= Z_LO + 4)
    pts = [(xa, -2000.0), (xa, start)]
    z = start
    while True:
        b_end = z + 2 * TRI_S                      # right piece's tail tip on xa
        a_lo, a_hi = b_end - TRI_S / 2, b_end + 1.5 * TRI_S
        if a_hi > Z_HI - 6:
            break
        assert min(abs(v - a_lo) for v in zb) < 1e-6 and min(abs(v - b_end) for v in za) < 1e-6
        pts += [(xa, b_end), (xb, a_lo), (xb, a_hi), (xa, a_hi - TRI_S / 2)]
        z = a_hi - TRI_S / 2
    pts += [(xa, z + 2 * TRI_S), (xa, 2000.0)]
    return pts


def back_polyline(front):
    """Same seam for the back layer, shifted LAP toward +X above the top plate, so the
    two layers overlap and no seam can be seen through. Below Z=0 (the clip lips) it
    stays on the front line."""
    xa = front[0][0]
    xl = xa + ROW_H + LAP      # straight cut clear of the whole dovetail band
    return [(xa, -2000.0), (xa, 0.0), (xl, 0.0), (xl, 2000.0)]


def _poly_region(left, right, clear):
    """Region between two seam polylines (each runs bottom to top). The whole clearance
    comes off the piece on the +X side of each seam, so the gap at every dovetail face
    equals `clear` and the -X piece stays at nominal size. Shrinking both pieces, as this
    did before 2026-11-03, doubled every gap."""
    m = box(-5000, 5000, -300, 300, -5000, 5000)
    if left is not None:
        m = m ^ xz_extrude(ccw(left + [(5000.0, 2000.0), (5000.0, -2000.0)])
                           .offset(-clear, JoinType.Miter))
    if right is not None:
        m = m ^ xz_extrude(ccw(right + [(-5000.0, 2000.0), (-5000.0, -2000.0)]))
    return m


def region(left, right):
    """Shiplap piece region. Front layer (Y < FIN_MID, carries the facets) is cut on the
    dovetail line; back layer on the same line shifted LAP. Each side's tongue sits
    behind or in front of its neighbour with LAP_CLEAR between them in Y."""
    lb = back_polyline(left) if left is not None else None
    rb = back_polyline(right) if right is not None else None
    F = _poly_region(left, right, JOINT_CLEAR)
    Bk = _poly_region(lb, rb, JOINT_CLEAR)
    c = LAP_CLEAR / 2
    ys = FIN_F + LAP_SPLIT_FROM_FRONT if LAP_SPLIT_FROM_FRONT is not None else FIN_MID
    return _compose(F, Bk)


def _compose(F, Bk):
    """Front layer from F, back layer from Bk, the shared middle from both."""
    c = LAP_CLEAR / 2
    ys = FIN_F + LAP_SPLIT_FROM_FRONT if LAP_SPLIT_FROM_FRONT is not None else FIN_MID
    front = F ^ box(-3000, 3000, -300, ys - c, -3000, 3000)
    back = Bk ^ box(-3000, 3000, ys + c, 300, -3000, 3000)
    return front + back + (F ^ Bk)


# Horizontal seam splitting the side extension. It sits below the monitor's top edge,
# where only the extension has material, so it never crosses a vertical seam.
HSEAM_Z = -25.0        # seam base line
HSEAM_TAIL = 10.0      # how far each tail reaches up into the top piece
HSEAM_NECK = 16.0      # tail width at the seam line; flanks run at 45 deg, so the head
                       # is 2*HSEAM_TAIL wider and no printed surface overhangs past 45 deg
HSEAM_TAILS = 4


def hseam_polyline():
    x0, x1 = -EXT_OVER + 14.0, -14.0
    pitch = (x1 - x0) / HSEAM_TAILS
    z0, z1 = HSEAM_Z, HSEAM_Z + HSEAM_TAIL
    pts = [(-3000.0, z0)]
    for i in range(HSEAM_TAILS):
        c = x0 + (i + 0.5) * pitch
        n = HSEAM_NECK / 2
        pts += [(c - n, z0), (c - n - HSEAM_TAIL, z1), (c + n + HSEAM_TAIL, z1), (c + n, z0)]
    return pts + [(3000.0, z0)]


def hregion(upper):
    line = hseam_polyline()
    zb = HSEAM_Z + HSEAM_TAIL + LAP     # back layer cut straight above the tails
    if upper:
        F = ccw(line + [(3000.0, 3000.0), (-3000.0, 3000.0)])
        Bk = rect(-3000, 3000, zb, 3000)
    else:
        F = ccw(line + [(3000.0, -3000.0), (-3000.0, -3000.0)])
        Bk = rect(-3000, 3000, -3000, zb)
    # The lower piece carries the tails and takes the whole clearance; the upper piece,
    # with the sockets, stays at nominal size.
    c = 0.0 if upper else JOINT_CLEAR
    return _compose(xz_extrude(F.offset(-c, JoinType.Miter)),
                    xz_extrude(Bk.offset(-c, JoinType.Miter)))


# --------------------------------------------------------------------------------------
# Facet relief on the viewer-facing side
# --------------------------------------------------------------------------------------
def relief_zone():
    r1 = (-EXT_OVER + 4, -4.0, -EXT_DROP + 4, Z_HI)                     # extension
    r2 = (-4.0, AXIS_X - KNUCKLE_R - 8, Z_LO, Z_HI)                      # over the monitor
    return r1, r2


def _inside_dist(x, z, r):
    return min(x - r[0], r[1] - x, z - r[2], r[3] - z)


def relief(lat):
    r1, r2 = relief_zone()
    flat, tris = lat.triangles()
    P = np.array([(p[0], p[1]) for p in flat])
    H = []
    for (x, z, k, j) in flat:
        d = max(_inside_dist(x, z, r1), _inside_dist(x, z, r2))
        f = min(1.0, max(0.0, d / TEX_FADE))
        wave = 0.5 + 0.5 * math.sin((x * 0.9 + z * 0.55) / 95.0)
        n = 0.3 * wave + 0.7 * _hash(k, j)
        H.append(f * (TEX_MIN + (TEX_MAX - TEX_MIN) * n))
    H = np.array(H)
    N = len(P)
    V = np.vstack([np.c_[P[:, 0], FIN_F - H + 0.2, P[:, 1]],
                   np.c_[P[:, 0], np.full(N, FIN_F + 1.0), P[:, 1]]])
    F = [tuple(t) for t in tris] + [(t[0] + N, t[2] + N, t[1] + N) for t in tris]
    edges = {}
    for t in tris:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            key = (min(a, b), max(a, b))
            edges[key] = edges.get(key, 0) + 1
    for (a, b), c in edges.items():
        if c == 1:
            F += [(a, b, b + N), (a, b + N, a + N)]
    tm = trimesh.Trimesh(V, np.array(F), process=True)
    trimesh.repair.fix_normals(tm)
    assert tm.is_watertight, "relief mesh not watertight"
    zone = xz_extrude(rect(*r1[:2], *r1[2:]) + rect(*r2[:2], *r2[2:]))
    return to_manifold(tm) ^ zone


# --------------------------------------------------------------------------------------
# Knuckle spine at the inner end
# --------------------------------------------------------------------------------------
def knuckle_bands():
    z0, z1 = Z_LO, HEIGHT - FIN_T - 1.0
    h = (z1 - z0 - (KNUCKLES - 1) * KNUCKLE_GAP) / KNUCKLES
    return [(z0 + i * (h + KNUCKLE_GAP), z0 + i * (h + KNUCKLE_GAP) + h) for i in range(KNUCKLES)]


def spine(panel, parity):
    """Own knuckles on bands with i % 2 == parity; clear the other side's bands."""
    r_off = KNUCKLE_R + KNUCKLE_CLEAR
    # teardrop: circle at the axis blending into the fin at 45 deg
    tip = KNUCKLE_R * math.sqrt(2)
    drop = (CrossSection.circle(KNUCKLE_R, SEG)
            + CrossSection([[(-KNUCKLE_R / math.sqrt(2), -KNUCKLE_R / math.sqrt(2)), (-tip, 0),
                             (-KNUCKLE_R / math.sqrt(2), KNUCKLE_R / math.sqrt(2))]])
            + rect(-tip - 6, -tip + 0.5, -FIN_T / 2, FIN_T / 2)).translate([AXIS_X, FIN_MID])
    for i, (za, zb) in enumerate(knuckle_bands()):
        if i % 2 == parity:
            panel = panel + drop.extrude(zb - za).translate([0, 0, za])
        else:
            keep_out = CrossSection.circle(r_off, SEG).translate([AXIS_X, FIN_MID])
            panel = panel - keep_out.extrude(zb - za + 2 * KNUCKLE_GAP).translate([0, 0, za - KNUCKLE_GAP])
    z_all0, z_all1 = knuckle_bands()[0][0], knuckle_bands()[-1][1]
    # nothing of this side above/below the spine reaches the axis
    panel = panel - box(AXIS_X - r_off, AXIS_X + 50, -100, 100, -100, z_all0 - KNUCKLE_GAP)
    panel = panel - box(AXIS_X - r_off, AXIS_X + 50, -100, 100, z_all1 + KNUCKLE_GAP, 400)
    hole = CrossSection.circle(PIN_HOLE_D / 2, 24).translate([AXIS_X, FIN_MID]).extrude(400).translate([0, 0, -100])
    return panel - hole


# --------------------------------------------------------------------------------------
# Whole panel for the left monitor, then cut along the seams
# --------------------------------------------------------------------------------------
def panel(parity):
    saddle_end = MONITOR_W - INNER_SADDLE_STOP
    body = yz_extrude(saddle_profile(), 0.0, saddle_end)
    fin = box(-EXT_OVER, AXIS_X, FIN_F, FIN_B, WALL - 0.5, HEIGHT)
    ext_low = box(-EXT_OVER, -1.0, FIN_F, FIN_B, -EXT_DROP, WALL)
    # One continuous rim: the front lip runs along the top, around the rounded corner and
    # down the outer edge; the back rib follows the outer edge and the same corner.
    sil = outline()
    # Rims follow the whole edge, both faces: top, both rounded corners, outer side, and the
    # extension's bottom. They stop short of the spine, and along the bottom they run only
    # under the extension (X < -1), never under the monitor.
    rim_zone = (rect(-EXT_OVER - 1, AXIS_X - KNUCKLE_R - 4, -EXT_DROP + 12, HEIGHT + 1)
                + rect(-EXT_OVER - 1, -1.0, -EXT_DROP - 1, HEIGHT + 1))
    front_band = (sil - sil.offset(-FIN_T, JoinType.Miter)) ^ rim_zone
    back_band = (sil - sil.offset(-3.0, JoinType.Miter)) ^ rim_zone
    front_rim = xz_extrude(front_band, FIN_F - RIB, FIN_B)
    back_rim = xz_extrude(back_band, FIN_B - 0.2, FIN_B + BACK_RIB)
    p = body + fin + ext_low + front_rim + back_rim
    lat = Lattice(-EXT_OVER - 10, AXIS_X + 10, -EXT_DROP - 10, HEIGHT + 10)
    p = p + relief(lat)
    p = p ^ xz_extrude(sil)
    if parity == 0:
        p = p + shelf_rail()
    # camera notch in the front lip, centred on the monitor
    cx = MONITOR_W / 2
    p = p - box(cx - CAM_NOTCH_W / 2, cx + CAM_NOTCH_W / 2, Y_OUT_F - 1, Y_IN_F + 0.01, -FRONT_LIP - 1, 0.01)
    p = spine(p, parity)
    return p, lat


CORNER_R = 30.0        # radius of the shield's outer top corner

# Webcam shelf: a triangular ledge that folds out of the LEFT panel only, just above the
# monitor tops, and reaches past the centre line over the right monitor. It floats
# SHELF_LIFT above the right shield and its back edge steps forward past the centre, so
# it never touches the right side at any angle up to PHI_MAX between the monitors.
# The webcam mount screws down with a standard 1/4"-20 screw from underneath.
SHELF_T = 3.0          # shelf plate thickness (ribs underneath carry the stiffness)
BRACE_T = 2.4          # brace wall thickness
BRACE_ROOT = 10.0      # brace depth under the plate at the panel (reaches the saddle lip's bottom)
BRACE_TIP = 3.0        # brace depth at the shelf's front edge
# (root u, v) -> (tip u, v), u = X - MONITOR_W. Roots sit on the saddle's front lip.
SHELF_BRACES = [((-78.0, -1.0), (-38.0, -41.0)),
                ((-15.0, -1.0), (-55.0, -41.0)),
                ((-55.0, -1.0), (-15.0, -41.0))]


GRID_PITCH = 13.0      # spacing of the criss-cross ribs
GRID_T = 2.0           # rib thickness
GRID_RIM = 2.4         # perimeter wall
# Grid footprint, a 45 deg parallelogram (u, v): its back edge sits on the saddle's front
# lip, its left edge follows the shelf's chamfer, its right edge stays clear of the right
# monitor. Every wall is at 45 deg or runs along the monitor edge, so it prints unsupported.
GRID_PLAN = [(-83.7, -0.5), (-35.5, -0.5), (8.5, -44.5), (-39.2, -44.5)]
SCREW_HEAD_R = 8.0     # clear cell around the hole for the screw head


def shelf_grid(z0):
    """Criss-cross grid under the shelf plate. Its bottom is flush with the bottom edge of
    the saddle's front lip, and its back wall is fused into that lip along its full height."""
    zb = -FRONT_LIP
    reg = CrossSection([[(MONITOR_W + u, v) for u, v in GRID_PLAN[::-1]]])
    if reg.area() < 0:
        reg = CrossSection([[(MONITOR_W + u, v) for u, v in GRID_PLAN]])
    lines = None
    span = 400.0
    for sgn in (1, -1):
        for k in range(-30, 31):
            c = k * GRID_PITCH
            # line u*sgn + v = c, as a thin rotated rectangle
            # offset perpendicular to the rib (normal of a line rotated 45*sgn deg)
            nx, ny = -sgn / math.sqrt(2), 1 / math.sqrt(2)
            r = rect(-span, span, -GRID_T / 2, GRID_T / 2).rotate(45 * sgn).translate(
                [MONITOR_W + CAM_U + c * nx, CAM_V + c * ny])
            lines = r if lines is None else lines + r
    rim = reg - reg.offset(-GRID_RIM, JoinType.Miter)
    plan = (lines ^ reg) + rim
    plan = plan - CrossSection.circle(SCREW_HEAD_R, 48).translate([MONITOR_W + CAM_U, CAM_V])
    ring = (CrossSection.circle(SCREW_HEAD_R + GRID_T, 48) - CrossSection.circle(SCREW_HEAD_R, 48)
            ).translate([MONITOR_W + CAM_U, CAM_V]) ^ reg
    plan = plan + ring
    return plan.extrude(z0 + 0.01 - zb).translate([0, 0, zb])


def _brace(x0, y0, x1, y1, top):
    L = math.hypot(x1 - x0, y1 - y0)
    a, b = (x1 - x0) / L, (y1 - y0) / L
    prof = CrossSection([[(0, top - BRACE_ROOT), (L, top - BRACE_TIP), (L, top), (0, top)]])
    m = prof.extrude(BRACE_T).translate([0, 0, -BRACE_T / 2])        # axes (s, z, w)
    # s along the brace, w across it; det = +1 so the mesh keeps its orientation
    return m.transform([[a, 0, b, x0], [b, 0, -a, y0], [0, 1, 0, 0]])
SHELF_LIFT = 1.0       # clearance above the right shield's top plate
SHELF_FRONT = -45.0    # how far in front of the screen face it reaches (left-monitor frame)
SHELF_BACK_W = 110.0   # how far it runs back along the left panel from the corner
SHELF_OVER = 25.0      # how far past the shared front corner it reaches
SHELF_LIP = 0.0        # no front lip: the screw holds the camera
PHI_MAX = 50.0         # largest total angle between the monitors it must clear
CAM_U, CAM_V = -25.0, -22.0   # webcam centre: left of the corner, in front of the screens
HOLE_D = 6.6           # clearance for 1/4"-20
SHELF_MARGIN = 6.0     # extra room behind the shelf for the panels sliding to meet


def _shelf_back_limit(u):
    """Deepest the shelf may reach (Y) at u = X - MONITOR_W past the corner, so it stays in
    front of the right shield's gusset (Y_right = FIN_F - GUSSET) for every angle, allowing
    for each panel sliding toward the centre to keep the spine aligned."""
    worst = FIN_F
    for phi in np.linspace(0, PHI_MAX, 26):
        p = math.radians(phi)
        yg = FIN_F - GUSSET
        worst = min(worst, -u * math.tan(p) + yg / math.cos(p))
    return worst - SHELF_MARGIN


# Aim: eyes level with the screen's centre, which sits SCREEN_CENTRE_DROP below the top
# edge. Viewing distance assumes a 30 in (762 mm) deep desk with the monitors' stand bases
# at the back edge (screens ~520 mm from the front edge) and eyes ~160 mm behind the front
# edge. The lens sits ~30 mm above the shelf top. The shelf tilts down toward you by the
# angle that points the lens at your eyes.
SCREEN_CENTRE_DROP = 21.0 + 335.7 / 2      # from the LG drawings: top bezel + half the screen
EYE_DIST = 680.0
LENS_ABOVE_SHELF = 30.0
SHELF_PIVOT_Y = 2.0                        # the plate tilts about this line, just behind the screen face


def shelf_aim():
    """Yaw and horizontal distance from the webcam to your eyes. You sit on the bisector
    between the monitors, EYE_DIST in front of the corner where they meet. In the left
    panel's frame that bisector runs at TOE_DEG toward -X from straight ahead (-Y)."""
    t = math.radians(TOE_DEG)
    ex, ey = -EYE_DIST * math.sin(t), -EYE_DIST * math.cos(t)
    dx, dy = ex - CAM_U, ey - CAM_V
    return math.atan2(-dx, -dy), math.hypot(dx, dy)   # yaw > 0 turns the camera toward -X


SHELF_YAW, AIM_DIST = shelf_aim()


def shelf_tilt_and_lift():
    """Solve tilt and lift together: lift keeps the tilted plate 1 mm above the right
    shield's front lip (which can reach 30 mm in front of the screens at 50 deg), and the
    lens height depends on lift."""
    a = 0.0
    for _ in range(20):
        lift = 1.0 + 30.0 * math.tan(a)
        lens_z = WALL + lift + SHELF_T + LENS_ABOVE_SHELF
        a = math.atan2(lens_z + SCREEN_CENTRE_DROP, AIM_DIST)
    return a, lift


SHELF_TILT, SHELF_LIFT = shelf_tilt_and_lift()


def tilt_matrix(z0):
    """3x4 rotation that pitches the plate down by SHELF_TILT toward the aim direction,
    about a horizontal axis through the webcam hole's line on the pivot."""
    f = np.array([-math.sin(SHELF_YAW), -math.cos(SHELF_YAW), 0.0])   # camera forward
    a = np.cross([0, 0, 1.0], f)                                       # tilt axis
    a /= np.linalg.norm(a)
    th = SHELF_TILT
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    R = np.eye(3) + math.sin(th) * K + (1 - math.cos(th)) * K @ K
    P = np.array([MONITOR_W + CAM_U, SHELF_PIVOT_Y, z0])
    return np.c_[R, P - R @ P]


def tilt_about_pivot(m, z0):
    return m.transform(tilt_matrix(z0).tolist())


SHELF_FRONT_AHEAD = 23.0   # front edge, measured along the aim from the camera centre
SCREW_SEAT = 1.0           # cone tip to top face; plastic over the screw head is ~4.5 mm


# The shelf is its own printed part. It slides onto a dovetail rail on the front face of
# the left inner piece's clip, from the outer (-X) side, until its closed end stops on the
# rail. Load path for the camera's weight: the shelf's back rests on the 45 deg fillet and
# the rail's upper flank (it can't drop), and the tipping moment from the camera sitting in
# front is taken by the dovetail flanks as a couple along the whole rail (it can't pitch
# forward or lift at the back).
RAIL_X0, RAIL_X1 = 540.0, 616.0    # inner piece only, behind the shelf's back edge
RAIL_D = 2.5                       # how far the rail stands proud of the clip's front face


def rail_profile(grow=0.0):
    """Dovetail rail in (Y, Z) on the clip's front face (Y = Y_OUT_F): 3 mm at the root,
    8 mm at the tip, 45 deg flanks, so it prints unsupported upside down and the shelf's
    slot prints unsupported upright."""
    y0, y1 = Y_OUT_F + 0.02, Y_OUT_F - RAIL_D
    cs = ccw([(y0, -3.5), (y0, -0.5), (y1, 2.0), (y1, -FRONT_LIP)])
    return cs.offset(grow, JoinType.Miter) if grow else cs


def shelf_rail():
    return yz_extrude(rail_profile(), RAIL_X0, RAIL_X1)


def webcam_shelf():
    """The separate shelf part: the old fused wedge, trimmed to sit in front of the clip and
    on top of its fillet with JOINT_CLEAR everywhere, with the rail slot cut along X. The
    slot is closed at its -X end (the end stop) and open at +X."""
    c = JOINT_CLEAR
    S = camera_shelf()
    front = box(-5000, 5000, -5000, Y_OUT_F - c, -5000, 5000)
    top = yz_extrude(ccw([(Y_OUT_F - 1, WALL + 1.5 * c - 1),
                          (FIN_F - c, WALL + 1.5 * c + (FIN_F - c - Y_OUT_F)),
                          (FIN_F - c, 500), (Y_OUT_F - 1, 500)]), -5000, 5000)
    shelf = S ^ (front + top)
    shelf = shelf - yz_extrude(rail_profile(c), RAIL_X0 - c, 5000)
    knuckles = CrossSection.circle(KNUCKLE_R + KNUCKLE_CLEAR + 0.3, SEG).translate(
        [AXIS_X, FIN_MID]).extrude(400).translate([0, 0, -100])
    return shelf - knuckles


def camera_shelf():
    """One solid wedge: a single tilted top plane, a flat bottom flush with the saddle's
    front lip, fused to the saddle top and the fin behind. Its front edge is square to the
    camera's aim, so lining the camera's front up with it sets the yaw. A pocket from
    below takes the 1/4-20 screw head."""
    z0 = WALL + SHELF_LIFT
    ztop = z0 + SHELF_T
    xb = MONITOR_W - SHELF_BACK_W
    xf = xb + (FIN_F - SHELF_FRONT)                 # 45 deg outer side, prints unsupported
    us = np.linspace(0.0, SHELF_OVER, 11)
    back = [(MONITOR_W + u, min(FIN_F, _shelf_back_limit(u))) for u in us]
    # outline reaches well forward; the aim-square front edge below trims it, so the
    # front is one clean line
    far = -200.0
    pts = [(xb + (FIN_F - far), far), (MONITOR_W + SHELF_OVER, far)] + back[::-1] + [(xb, FIN_F)]
    plan = CrossSection([pts])
    # right edge: straight from the saddle's end at the pivot to the front-right corner
    ub, vb = -INNER_SADDLE_STOP - 0.7, SHELF_PIVOT_Y
    uf, vf = SHELF_OVER, SHELF_FRONT
    k = (uf - ub) / (vb - vf)
    big = 400.0
    plan = plan ^ ccw([(MONITOR_W + ub + k * (vb - v), v) for v in (-big, big)]
                      + [(-5000, big), (-5000, -big)])
    # front edge square to the aim
    fx, fy = -math.sin(SHELF_YAW), -math.cos(SHELF_YAW)
    cx, cy = MONITOR_W + CAM_U, CAM_V
    ox, oy = cx + fx * SHELF_FRONT_AHEAD, cy + fy * SHELF_FRONT_AHEAD
    nx, ny = -fy, fx
    plan = plan ^ ccw([(ox + nx * big, oy + ny * big), (ox - nx * big, oy - ny * big),
                       (ox - nx * big - fx * big, oy - ny * big - fy * big),
                       (ox + nx * big - fx * big, oy + ny * big - fy * big)])
    zb = -FRONT_LIP
    solid = plan.extrude(ztop + 120 - zb).translate([0, 0, zb])
    # below the saddle's front lip line it may reach down to the lip bottom; behind it,
    # it sits on the saddle top (never down into the monitor)
    floor = (box(-5000, 5000, -5000, Y_OUT_F, zb, 500)
             + box(-5000, 5000, -5000, 5000, 0.0, 500))
    solid = solid ^ floor
    above = tilt_about_pivot(box(-5000, 5000, -5000, 5000, ztop, ztop + 400), z0)
    solid = solid - above
    # Toward the corner, where the right panel's lip swings under at wide angles, the
    # underside rises at 45 deg (prints unsupported) up to the plate's own thickness.
    xc = MONITOR_W + CAM_U + SCREW_HEAD_R + 2.0     # starts just past the screw-head pocket
    under = CrossSection([[(xc, zb - 1), (xc + 400, zb - 1), (xc + 400, zb - 1 + 400)]]
                         ).extrude(800).rotate([90, 0, 0]).translate([0, 400, 0])
    slab = tilt_about_pivot(box(-5000, 5000, -5000, 5000, z0, ztop), z0)
    solid = (solid - under) + (solid ^ slab)
    hole = CrossSection.circle(HOLE_D / 2, 48).translate([cx, cy])
    hole_cyl = tilt_about_pivot(hole.extrude(80).translate([0, 0, ztop - 60]), z0)
    # Screw-head pocket from below, with a 45 deg conical roof instead of a flat one so
    # the shelf prints upright with no support inside the pocket. The head bears on the
    # cone about 4.5 mm below the top face.
    hc = SCREW_HEAD_R - HOLE_D / 2
    zc = ztop - SCREW_SEAT - hc
    roof = Manifold.cylinder(hc + 0.01, SCREW_HEAD_R, HOLE_D / 2, 64).translate([cx, cy, zc - 0.01])
    pocket = tilt_about_pivot(
        CrossSection.circle(SCREW_HEAD_R, 64).translate([cx, cy]).extrude(80).translate([0, 0, zc - 80])
        + roof, z0)
    return solid - hole_cyl - pocket


def outline():
    """Panel silhouette in (X, Z): the extension's outer top AND bottom corners are rounded
    with the same radius. The bottom edge sits at -EXT_DROP; below the monitor's top edge
    only the extension (X < 0) and the clip lips (which stop at -REAR_LIP) reach down."""
    xo, R = -EXT_OVER, CORNER_R
    zb = -EXT_DROP
    top = [(xo + R + R * math.cos(math.radians(a)), HEIGHT - R + R * math.sin(math.radians(a)))
           for a in np.linspace(90, 180, 72)]
    bot = [(xo + R + R * math.cos(math.radians(a)), zb + R + R * math.sin(math.radians(a)))
           for a in np.linspace(180, 270, 72)]
    pts = [(5000.0, zb), (5000.0, HEIGHT)] + top + bot
    return ccw(pts)


def pieces(parity):
    p, lat = panel(parity)
    s = [seam_polyline(lat, x0) for x0 in SEAMS]
    bounds = [(None, s[0]), (s[0], s[1]), (s[1], s[2]), (s[2], None)]
    names = ["extension", "outer", "middle-camera", "inner"]
    out = {n: p ^ region(a, b) for n, (a, b) in zip(names, bounds)}
    # The side extension stays one piece (330 mm tall). It prints lying on its flat outer
    # edge, diagonally across the bed, so it needs no horizontal seam: a seam there would put
    # dovetail tails sideways on the bed, and a sideways tail always starts in mid-air.
    if parity == 0:
        out["webcam-shelf"] = webcam_shelf()
    return out


def mirror_right(m):
    return m.mirror([1, 0, 0]).translate([MONITOR_W, 0, 0])


def fit_test():
    return yz_extrude(saddle_profile(fin_height=20.0), 0.0, 20.0)


# --------------------------------------------------------------------------------------
# Export in print orientation: the piece's X axis points up.
# --------------------------------------------------------------------------------------
PRINT_FLAT = os.environ.get("PRINT_FLAT", "0") == "1"   # standing batches 4-5 parts per plate


def to_print(m, flip):
    """Default: lying flat, faceted front face up, back (sun side) down, so a slicer
    needs no rotation and support marks land on the hidden back. PRINT_FLAT=0 gives the
    old standing export: flip=False puts the min-X end on the bed, flip=True the max-X end."""
    if PRINT_FLAT:
        m = m.rotate([-90, 0, 0])            # use-frame -Y (front, facets) -> +Z (up)
    else:
        m = m.rotate([0, -90, 0]) if not flip else m.rotate([0, 90, 0])
    b = m.bounding_box()
    return m.translate([-(b[0] + b[3]) / 2, -(b[1] + b[4]) / 2, -b[2]])


def export(m, name):
    tm = to_trimesh(m)
    assert tm.is_watertight, f"{name} not watertight"
    tm.export(os.path.join(OUT, name))
    size = tm.bounds[1] - tm.bounds[0]
    fits_tall = size[2] <= MAX_BED
    fits_flat = max(size[0], size[1]) <= MAX_BED or (size[0] + size[1]) / math.sqrt(2) <= MAX_BED
    note = "fits" if fits_tall and max(size[0], size[1]) <= MAX_BED else (
        "fits diagonally" if fits_tall and fits_flat else "TOO BIG")
    return size, note


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".stl"):
            os.remove(os.path.join(OUT, f))
    report = []
    left = pieces(parity=0)
    right = {n: mirror_right(m) for n, m in pieces(parity=1).items()}
    # orientation: extension's free outer edge down; inner piece's knuckles up
    flips = {"left": {"extension": False, "outer": False, "middle-camera": False, "inner": False},
             "right": {"extension": True, "outer": True, "middle-camera": True, "inner": True}}
    for side, parts in (("left", left), ("right", right)):
        for n, m in parts.items():
            name = f"{side}_{n}.stl"
            if n == "webcam-shelf":      # prints the right way up, on its flat bottom
                b = m.bounding_box()
                mm = m.translate([-(b[0] + b[3]) / 2, -(b[1] + b[4]) / 2, -b[2]])
            else:
                mm = to_print(m, flips[side][n])
            report.append((name, *export(mm, name)))
    report.append(("fit_test_clip.stl", *export(to_print(fit_test(), False), "fit_test_clip.stl")))
    for name, s, note in report:
        print(f"{name:28s} {s[0]:7.1f} x {s[1]:7.1f} x {s[2]:7.1f} mm  {note}")


if __name__ == "__main__":
    main()
