"""v5: wire openings at the back ports 6 (+X) and 14 (-X), cut into the v4 print STLs.

The same cutters as back_cutters() in sesame_atech_wired.py (PORT_Y_BACK): at each port a
slot through the bay's side and back walls and the tray wall behind them, and an 8 mm lead
notch under it, both cut round the lid-screw boss at (+-33.3, 35.5) so the boss stays whole.
The print STLs are cut as meshes: print_to_model.json maps each print STL into the model frame.
Part 2 (spine and head) stays inside |x| 18.5 and is not touched.

python cut_openings_back.py v4_stl_dir out_dir print_to_model.json
"""
import json, sys
import numpy as np
import trimesh

PORT_Y = {6: (34.18, 49.82), 14: (34.18, 49.82)}
X_IN, X_OUT = 30.0, 45.0          # from just past the board's edge (29.99) to beyond every wall
SLOT_Z = (79.45, 86.65)
LEAD_W, LEAD_Z0 = 8.0, 75.95
BOSS = (33.3, 35.5)               # the lid-screw boss in each bay (r 2.2)
BOSS_R = 2.4                      # kept out of the cut


def boxes():
    out = []
    for n, (y0, y1) in PORT_Y.items():
        sx = 1 if n == 6 else -1
        xa, xb = sorted((sx * X_IN, sx * X_OUT))
        keep = (sx * BOSS[0], BOSS[1], BOSS_R)
        out.append(("port%d" % n, (xa, xb, y0 - 0.5, y1 + 0.5) + SLOT_Z, keep))
        yc = (y0 + y1) / 2
        out.append(("sg90_%d" % n, (xa, xb, yc - LEAD_W / 2, yc + LEAD_W / 2, LEAD_Z0, SLOT_Z[0] + 0.1), keep))
    return out


def cutter():
    parts = []
    for _, (x0, x1, y0, y1, z0, z1), (cx, cy, r) in boxes():
        b = trimesh.creation.box(bounds=[[x0, y0, z0], [x1, y1, z1]])
        c = trimesh.creation.cylinder(radius=r, height=40.0, sections=96)
        c.apply_translation([cx, cy, 80.0])
        parts.append(trimesh.boolean.difference([b, c], engine="manifold"))
    return trimesh.boolean.union(parts, engine="manifold")


if __name__ == "__main__":
    src, dst, maps = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3]))
    cut = cutter()
    for key, name in (("part1", "deck_part1_plate.stl"), ("lid", "lid_print_upside_down.stl")):
        M = np.array(maps[key])
        m = trimesh.load(f"{src}/{name}")
        m.apply_transform(M)                                   # print -> model frame
        before = m.volume
        m = trimesh.boolean.difference([m, cut], engine="manifold")
        m.apply_transform(np.linalg.inv(M))                    # back to print orientation
        m.export(f"{dst}/{name}")
        print(f"{name}: removed {before - m.volume:.1f} mm3, watertight {m.is_watertight}, bodies {len(m.split(only_watertight=False))}")
