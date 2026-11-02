"""Joint test coupons: a short slice of a real seam at three clearances, cut from the
actual pieces so the joint geometry is exactly what the full set uses.

Each coupon is a pair of halves joined by one dovetail tail plus the overlapping back
layer. The number of notches on each half's edge marks its clearance: 1 = 0.10 mm,
2 = 0.15 mm (the default), 3 = 0.20 mm per side. Print all three pairs together, in the
same filament and profile as the real parts, and use the clearance that slides together
by hand with no visible play.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FITS = [("1-notch", "0.10"), ("2-notch", "0.15"), ("3-notch", "0.20")]

if len(sys.argv) == 1:
    for tag, fit in FITS:
        env = dict(os.environ, FIT=fit, MJF="0")
        subprocess.run([sys.executable, __file__, tag], env=env, check=True)
    sys.exit(0)

import build as B

tag = sys.argv[1]
n = int(tag[0])
# one tail of the horizontal seam: the tail centred nearest the extension's middle
x0, x1 = -B.EXT_OVER + 14.0, -14.0
pitch = (x1 - x0) / B.HSEAM_TAILS
cx = x0 + 1.5 * pitch
w = pitch * 0.5 + B.HSEAM_TAIL + 4
z_lo, z_hi = B.HSEAM_Z - 14, B.HSEAM_Z + B.HSEAM_TAIL + B.LAP + 14
block = B.box(cx - w, cx + w, B.FIN_F - 6, B.FIN_B + 1, z_lo, z_hi)

parts = B.pieces(0)
lower = parts["extension-lower"] ^ block
upper = parts["extension"] ^ block
for i in range(n):  # clearance marker notches, 2 mm wide, on the outer side edge
    zc = z_lo + 4 + i * 4
    lower = lower - B.box(cx - w - 1, cx - w + 1.5, -100, 100, zc - 1, zc + 1)
    zc = z_hi - 4 - i * 4
    upper = upper - B.box(cx - w - 1, cx - w + 1.5, -100, 100, zc - 1, zc + 1)

# one tail of a vertical seam (outer | middle), the joint type used six times in the set
xa = B.SEAMS[1]
vb = B.box(xa - 12, xa + B.ROW_H + B.LAP + 12, B.FIN_F - 6, B.FIN_B + 1, 52.0, 116.0)
left_v = parts["outer"] ^ vb
right_v = parts["middle-camera"] ^ vb
for i in range(n):
    xc = xa - 8 + 0 * i
    zc = 56 + i * 4
    left_v = left_v - B.box(xa - 13, xa - 10.5, -100, 100, zc - 1, zc + 1)
    right_v = right_v - B.box(xa + B.ROW_H + B.LAP + 10.5, xa + B.ROW_H + B.LAP + 13, -100, 100, zc - 1, zc + 1)

out = os.path.join(HERE, "out", "coupons")
os.makedirs(out, exist_ok=True)
for name, m in (("horiz-bottom", lower), ("horiz-top", upper),
                ("vert-left", left_v), ("vert-right", right_v)):
    assert len(m.decompose()) == 1, f"{tag} {name} is not one body"
    # same orientation as the real parts (panel standing on its end), so the coupon tests
    # the same mix of layer-height and XY accuracy the full set will see
    m = B.to_print(m, False)
    tm = B.to_trimesh(m)
    assert tm.is_watertight
    path = os.path.join(out, f"coupon_{tag}_{name}.stl")
    tm.export(path)
    s = tm.bounds[1] - tm.bounds[0]
    print(f"{os.path.basename(path):30s} {s[0]:5.1f} x {s[1]:5.1f} x {s[2]:5.1f} mm  fit {B.JOINT_CLEAR} mm/side")
