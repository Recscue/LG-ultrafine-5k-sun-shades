"""Check the webcam stand-in: its lens faces your eyes and it sits flat (no roll)."""
import math
import numpy as np
import build as B
import export_view as EV

body, foot, lens = [m for m, _ in EV.webcam_local()]
# lens disc normal = facing direction (the face pointing away from the body)
c_body, c_lens = body.centroid, lens.centroid
face = c_lens - c_body
face /= np.linalg.norm(face)
t = math.radians(B.TOE_DEG)
eye = np.array([B.MONITOR_W - B.EYE_DIST * math.sin(t), -B.EYE_DIST * math.cos(t), -B.SCREEN_CENTRE_DROP])
to_eye = eye - c_lens
to_eye /= np.linalg.norm(to_eye)
print(f"camera facing vs direction to your eyes: {math.degrees(math.acos(np.clip(face @ to_eye, -1, 1))):.2f} deg off")
# roll: the body's long axis (width) should stay horizontal
pts = body.vertices - c_body
u, s, vt = np.linalg.svd(pts, full_matrices=False)
width_axis = vt[0]
print(f"camera roll (long axis vs horizontal): {math.degrees(math.asin(abs(width_axis[2]))):.2f} deg")
