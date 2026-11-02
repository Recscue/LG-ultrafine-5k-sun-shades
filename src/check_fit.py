"""Does the shield's clip intersect the monitor's real rear shell?"""
import math
import build as B
import preview as P

mon = B.to_manifold(P.monitor_shell())
for n, m in B.pieces(0).items():
    v = (m ^ mon).volume()
    print(f"{n:15s} overlap with monitor: {v:9.2f} mm3")
slope = math.degrees(math.atan((P.MONITOR_D - B.EDGE_T) / P.REAR_PLATE_TOP))
print(f"monitor rear slope from the top edge: {slope:.1f} deg; clip rear lip: {B.REAR_TAPER_DEG} deg")
