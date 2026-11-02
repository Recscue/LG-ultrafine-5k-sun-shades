"""Place both panels at several angles between the monitors (front corners touching,
each panel slid along its monitor so the spine axes meet) and check that nothing on
the left side touches anything on the right, and the webcam clears both."""
import math
import numpy as np
import trimesh
import build as B
import export_view as EV

L = {n: B.to_trimesh(m) for n, m in B.pieces(0).items()}
R = {n: B.to_trimesh(B.mirror_right(m)) for n, m in B.pieces(1).items()}


def place(tm, side, toe, slide):
    t = tm.copy()
    if side < 0:
        t.apply_translation([-B.MONITOR_W + slide, 0, 0]); ang = math.radians(toe)
    else:
        t.apply_translation([-slide, 0, 0]); ang = math.radians(-toe)
    t.apply_transform(trimesh.transformations.rotation_matrix(ang, [0, 0, 1], [0, 0, 0]))
    return B.to_manifold(t)


def cam_at(toe, slide):
    """Webcam follows the left panel."""
    out = []
    for m, _ in EV.webcam_local():
        t = m.copy()
        t.apply_translation([-B.MONITOR_W + slide, 0, 0])
        t.apply_transform(trimesh.transformations.rotation_matrix(math.radians(toe), [0, 0, 1], [0, 0, 0]))
        out.append(B.to_manifold(t))
    return out


ok = True
for phi in (0, 10, 20, 30, 40, 50):
    toe = phi / 2
    slide = B.FIN_MID * math.tan(math.radians(toe)) - (B.AXIS_X - B.MONITOR_W)
    lm = [place(m, -1, toe, slide) for m in L.values()]
    rm = [place(m, 1, toe, slide) for m in R.values()]
    shelf_vs_right = sum((a ^ b).volume() for a in lm[3:] for b in rm)
    spine = (lm[3] ^ rm[3]).volume()
    cam = sum((c ^ b).volume() for c in cam_at(toe, slide) for b in rm + lm)
    flag = "ok" if max(shelf_vs_right, cam) < 1e-3 else "COLLIDES"
    ok &= flag == "ok"
    print(f"angle between monitors {phi:2d} deg: left inner vs right {shelf_vs_right:8.3f} mm3,"
          f" webcam vs shield {cam:8.3f} mm3  {flag}")
print("ALL CLEAR" if ok else "FAILS")
