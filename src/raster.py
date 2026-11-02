"""Tiny z-buffer rasterizer with flat shading, so previews show real facets."""
import numpy as np


def look_at(eye, target, up=(0, 0, 1)):
    eye, target, up = map(lambda v: np.asarray(v, float), (eye, target, up))
    f = target - eye; f /= np.linalg.norm(f)
    r = np.cross(f, up); r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return eye, r, u, f


def render(items, eye, target, size=(1600, 1000), fov_deg=30, bg=(1, 1, 1)):
    W, H = size
    eye, r, u, f = look_at(eye, target)
    fl = (H / 2) / np.tan(np.radians(fov_deg) / 2)
    img = np.ones((H, W, 3)) * np.array(bg)
    zb = np.full((H, W), np.inf)
    lights = [(np.array([-0.4, -0.75, 0.55]), 0.62), (np.array([0.6, -0.2, 0.3]), 0.22)]
    lights = [(d / np.linalg.norm(d), k) for d, k in lights]
    for tm, color in items:
        V = tm.vertices - eye
        cam = np.c_[V @ r, V @ u, V @ f]
        tris = cam[tm.faces]
        n = tm.face_normals
        shade = 0.22 + sum(k * np.clip(n @ d, 0, 1) for d, k in lights)
        # back-facing toward the camera still drawn (thin parts), keep simple
        col = np.clip(np.asarray(color)[None, :] * shade[:, None], 0, 1)
        for t, c in zip(tris, col):
            if np.any(t[:, 2] <= 1):
                continue
            px = W / 2 + fl * t[:, 0] / t[:, 2]
            py = H / 2 - fl * t[:, 1] / t[:, 2]
            x0, x1 = int(max(0, np.floor(px.min()))), int(min(W - 1, np.ceil(px.max())))
            y0, y1 = int(max(0, np.floor(py.min()))), int(min(H - 1, np.ceil(py.max())))
            if x0 > x1 or y0 > y1:
                continue
            gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            (ax, bx, cx), (ay, by, cy) = px, py
            den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
            if abs(den) < 1e-9:
                continue
            w0 = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / den
            w1 = ((cy - ay) * (gx - cx) + (ax - cx) * (gy - cy)) / den
            w2 = 1 - w0 - w1
            m = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
            if not m.any():
                continue
            iz = w0 / t[0, 2] + w1 / t[1, 2] + w2 / t[2, 2]
            z = 1 / np.where(m, iz, 1e-12)
            sub = zb[y0:y1 + 1, x0:x1 + 1]
            upd = m & (z < sub)
            sub[upd] = z[upd]
            img[y0:y1 + 1, x0:x1 + 1][upd] = c
    return img
