"""Can each joint actually be assembled? A dovetail only goes together by sliding one
piece through the panel's thickness (Y). For every joint, move one piece along +Y and -Y
in steps and report the direction that never collides on the way in."""
import build as B

parts = B.pieces(0)
pairs = [("extension", "outer"), ("outer", "middle-camera"), ("middle-camera", "inner"),
         ("extension-lower", "extension")]
steps = [0.25, 0.5, 1, 2, 3, 5, 8, 12, 18, 25, 35, 50, 70]
ok_all = True
for a, b in pairs:
    A, Bm = parts[a], parts[b]
    res = {}
    for sgn in (1, -1):
        worst = max((A.translate([0, sgn * d, 0]) ^ Bm).volume() for d in steps)
        res[sgn] = worst
    good = [s for s, v in res.items() if v < 1e-3]
    ok_all &= bool(good)
    if good:
        how = "toward the back" if good[0] > 0 else "toward the front"
        print(f"{a:16s} + {b:14s}: assembles. {a} slides on {how} (collision-free path)")
    else:
        print(f"{a:16s} + {b:14s}: BLOCKED both ways (+Y {res[1]:.1f} mm3, -Y {res[-1]:.1f} mm3)")
print("ALL JOINTS ASSEMBLE" if ok_all else "SOME JOINTS CANNOT BE ASSEMBLED")
