"""v6.4: tighter servo-horn pockets in the four hip joints (L1 L2 R1 R2), so the horns press in and stay.

Each hip joint has two horn pockets: one printed flat (7.52 mm wide, Sesame's) and one in the upright
plate, printed on its side (8.00 mm wide). The horns fell out, so this adds a skin on every pocket
wall: the pocket outline, slice by slice, is shrunk by SKIN mm all round (width and length shrink by
2 x SKIN). The lead-in chamfer at the mouth, the screw holes and the rest of the part are unchanged.

    python3 atech/cad/tighten_horn_pockets.py            # the leg STLs, from print/stl_legs_orig/
    python3 atech/cad/tighten_horn_pockets.py --coupon   # also the fit-test piece
"""
import os
import sys

import numpy as np
import trimesh
from shapely.geometry import Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
PRINT = os.path.join(HERE, "..", "print")
SRC = os.path.join(PRINT, "stl_legs_orig")
OUT = os.path.join(PRINT, "stl")
SKIN = {"flat": 0.10, "side": 0.15}     # mm per wall: flat 7.52 -> 7.32 wide, side 8.00 -> 7.70 wide
STEP = 0.1
NORMALS = [np.array(v, float) / np.linalg.norm(v) for v in
           ([0, 0, 1], [1, 0, 0], [0, 1, 0], [1, 1, 0], [1, -1, 0])]


def find_pockets(m):
    """(normal, kind, [(d, hole polygon in 3D section frame, T)]) for each horn pocket."""
    found = []
    for n in NORMALS:
        d = m.vertices @ n
        rows = []
        for v in np.arange(d.min() + STEP / 2 + 0.033, d.max(), STEP):   # off the 0.1 grid of the part's own faces
            s = m.section(n, n * v)
            if s is None:
                continue
            s2, T = s.to_2D()
            for pf in s2.polygons_full:
                for h in pf.interiors:
                    H = Polygon(h)
                    xs = np.array(H.minimum_rotated_rectangle.exterior.coords)
                    e = sorted(np.linalg.norm(xs[i + 1] - xs[i]) for i in range(2))
                    if 7.3 < e[0] < 9.5 and 9 < e[1] < 26:
                        rows.append((v, H, T, e[0]))
        if rows:
            w0 = min(r[3] for r in rows)
            rows = [r for r in rows if r[3] <= w0 + 0.1]        # leave the chamfer at the mouth
            kind = "flat" if abs(n[2]) > 0.9 else "side"
            found.append((n, kind, w0, rows))
    return found


def skin_mesh(n, rows, skin):
    """The skin: each slice's hole minus the hole shrunk by `skin`, as a STEP-thick slab."""
    parts = []
    for v, H, T, _ in rows:
        ring = H.buffer(0.07, join_style=1).difference(H.buffer(-skin, join_style=2))   # 0.07 into the wall, so it fuses
        if ring.is_empty:
            continue
        slab = trimesh.creation.extrude_polygon(ring, STEP + 0.02)
        slab.apply_translation([0, 0, -STEP / 2 - 0.01])
        slab.apply_transform(T)          # section frame -> part
        parts.append(slab)
    return trimesh.boolean.union(parts, engine="manifold")


def tighten(name, skin=SKIN, src=None):
    m = trimesh.load(src or os.path.join(SRC, name))
    pockets = find_pockets(m)
    log = []
    for n, kind, w0, rows in pockets:
        sk = skin_mesh(n, rows, skin[kind])
        m = trimesh.boolean.union([m, sk], engine="manifold")
        m = max(m.split(only_watertight=False), key=lambda b: b.volume)   # drop zero-volume slivers
        log.append("%s pocket %.2f -> %.2f mm wide, %.1f mm deep" % (kind, w0, w0 - 2 * skin[kind], len(rows) * STEP))
    return clean(m), log


def clean(m):
    """Merge the hair-thin edges the slab union leaves (an STL round trip then has every edge on two faces)."""
    import manifold3d as mf
    M = mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, np.float32),
                            tri_verts=np.asarray(m.faces, np.uint32))).simplify(0.0005)
    o = M.to_mesh()
    return trimesh.Trimesh(o.vert_properties[:, :3], o.tri_verts)


if __name__ == "__main__":
    for nm in ("L1", "L2", "R1", "R2"):
        f = nm + "-v117.stl"
        m, log = tighten(f)
        m.export(os.path.join(OUT, f))
        assert trimesh.load(os.path.join(OUT, f)).is_watertight, f
        print(f, "|", "; ".join(log))
