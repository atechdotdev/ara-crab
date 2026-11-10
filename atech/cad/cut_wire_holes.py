"""SUPERSEDED in v6.1 by export_print.py, which exports these parts from the model itself.

v6: the wire-bobbin keyholes into the lid, the eight servo-lead holes and the eight slot
notches into the spine, the eight lead slots and wider screw holes (v6.1) into Sesame's internal frame, cut into the
v5 print STLs (the frame: upstream's Internal-Frame-v121.stl, written as -wired).

The same cutters as keyhole_shapes(), spine_hole_shapes(), spine_notch_boxes() and
frame_slot_boxes() in sesame_atech_wired.py (WIRE BOBBIN KEYHOLES, SPINE LEAD HOLES,
FRAME LEAD SLOTS). The print STLs are cut as meshes:
print_to_model.json maps each print STL into the model frame.

python cut_wire_holes.py v5_stl_dir out_dir print_to_model.json
"""
import json, sys
import numpy as np
import trimesh

LID_TOP, WALL = 95.2616, 2.0
BOBBIN_Y = {2: -38.0, 3: -18.0, 4: 2.2, 5: 22.1, 6: 42.0,
            10: -38.0, 11: -18.0, 12: 2.0, 13: 22.0, 14: 42.0}
BOBBIN_X = {"bay": (9.5, 35.5), "back": (6.0, 32.0)}
PEG_DX, KEY_TRAVEL, KEY_ENTRY_D, KEY_SLOT_W = 6.0, 4.0, 6.0, 3.4

SPINE_Y = 39.61
LEAD_HOLE_W, LEAD_HOLE_H, LEAD_HOLE_X = 9.0, 4.5, 8.0
LEAD_HOLE_Z = {"hip": 59.0, "knee": 66.5}
LEGS = (("FL", 1, -1), ("FR", -1, -1), ("RL", 1, 1), ("RR", -1, 1))

FRAME_TOP, SPINE = 53.8, 18.5
FRAME_SLOT_X, FRAME_SLOT_L = (13.4, 17.4), 9.0   # v6.1: through the 1 mm rib, no sliver
FRAME_SLOT_Y = (-20.0, -8.0, 8.0, 20.0)
SPINE_NOTCH = (SPINE - WALL - 0.1, 17.5, FRAME_TOP - 0.1, 58.0)
# v6.1: the frame's deck-screw holes wider for stock M2 pan-heads (FRAME SCREW HOLES WIDER)
FRAME_SCREWS = ((16.785, 36.04), (-16.785, 36.04), (15.93, -33.62), (-15.93, -33.62))
FRAME_SCREW_Z = FRAME_TOP - 1.27
FRAME_SCREW_POCKET_D, FRAME_SCREW_HOLE_D = 6.0, 2.6


def cyl(r, z0, z1, x, y):
    c = trimesh.creation.cylinder(radius=r, height=z1 - z0, sections=96)
    c.apply_translation([x, y, (z0 + z1) / 2])
    return c


def box(x0, x1, y0, y1, z0, z1):
    return trimesh.creation.box(bounds=[[x0, y0, z0], [x1, y1, z1]])


def keyholes():
    z0, z1 = LID_TOP - WALL - 0.3, LID_TOP + 1.0
    parts = []
    for n, y in BOBBIN_Y.items():
        sx = 1 if n <= 6 else -1
        xc = sum(BOBBIN_X["back" if n in (6, 14) else "bay"]) / 2
        for d in (-PEG_DX, PEG_DX):
            x = sx * (xc + d)
            xe = x - sx * KEY_TRAVEL
            parts += [cyl(KEY_ENTRY_D / 2, z0, z1, xe, y), cyl(KEY_SLOT_W / 2, z0, z1, x, y),
                      box(min(x, xe), max(x, xe), y - KEY_SLOT_W / 2, y + KEY_SLOT_W / 2, z0, z1)]
    return trimesh.boolean.union(parts, engine="manifold")


def spine_holes():
    r, L = LEAD_HOLE_H / 2, LEAD_HOLE_W - LEAD_HOLE_H
    parts = []
    for _, sx, sy in LEGS:
        for z in LEAD_HOLE_Z.values():
            x = sx * LEAD_HOLE_X
            y0 = sy * SPINE_Y - 3.0 if sy > 0 else -SPINE_Y - 3.0
            y1 = y0 + 6.0 + WALL
            parts.append(box(x - L / 2, x + L / 2, y0, y1, z - r, z + r))
            for dx in (-L / 2, L / 2):
                c = trimesh.creation.cylinder(radius=r, height=y1 - y0, sections=96)
                c.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
                c.apply_translation([x + dx, (y0 + y1) / 2, z])
                parts.append(c)
    return trimesh.boolean.union(parts, engine="manifold")


def frame_slots():
    return trimesh.boolean.union([box(*sorted((sx * FRAME_SLOT_X[0], sx * FRAME_SLOT_X[1])), y - FRAME_SLOT_L / 2,
                                      y + FRAME_SLOT_L / 2, 30.0, FRAME_TOP + 1.0)
                                  for sx in (1, -1) for y in FRAME_SLOT_Y], engine="manifold")


def frame_screw_cutters():
    parts = []
    for x, y in FRAME_SCREWS:
        parts += [cyl(FRAME_SCREW_POCKET_D / 2, 36.0, FRAME_SCREW_Z, x, y),
                  cyl(FRAME_SCREW_HOLE_D / 2, FRAME_SCREW_Z - 0.5, FRAME_SCREW_Z + 3.5, x, y)]
    return trimesh.boolean.union(parts, engine="manifold")


def spine_notches():
    x0, x1, z0, z1 = SPINE_NOTCH
    return trimesh.boolean.union([box(*sorted((sx * x0, sx * x1)), y - FRAME_SLOT_L / 2, y + FRAME_SLOT_L / 2, z0, z1)
                                  for sx in (1, -1) for y in FRAME_SLOT_Y], engine="manifold")


if __name__ == "__main__":
    src, dst, maps = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3]))
    for key, name, out, cut in (
            ("lid", "lid_print_upside_down.stl", None, keyholes()),
            ("part2", "deck_part2_spine_and_head.stl", None,
             trimesh.boolean.union([spine_holes(), spine_notches()], engine="manifold")),
            ("frame", "Internal-Frame-v121.stl", "Internal-Frame-v121-wired.stl",
             trimesh.boolean.union([frame_slots(), frame_screw_cutters()], engine="manifold"))):
        M = np.array(maps[key])
        m = trimesh.load(f"{src}/{name}")
        m.apply_transform(M)                                   # print -> model frame
        before = m.volume
        m = trimesh.boolean.difference([m, cut], engine="manifold")
        m.apply_transform(np.linalg.inv(M))                    # back to print orientation
        m.export(f"{dst}/{out or name}")
        print(f"{name}: removed {before - m.volume:.1f} mm3, watertight {m.is_watertight}, bodies {len(m.split(only_watertight=False))}")
