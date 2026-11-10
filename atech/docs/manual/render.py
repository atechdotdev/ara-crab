"""Render the Sesame-on-Atech assembly steps (Blender, Workbench). blender -b -P render.py -- parts_dir out_dir [step ...]"""
import bpy, sys, os, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
PARTS, OUT = argv[0], argv[1]
ONLY = set(argv[2:])

GRAPHITE, WHITE, BLUE, SKY = (0.27, 0.28, 0.30), (0.93, 0.93, 0.91), (0.12, 0.42, 0.86), (0.55, 0.78, 0.95)
COL = {"frame": GRAPHITE, "bottom_cover": GRAPHITE, "battery": (0.56, 0.58, 0.61),
       "femur": WHITE, "foot": WHITE, "servo": BLUE, "deck_part1": (0.96, 0.96, 0.94),
       "deck_part2": (0.80, 0.86, 0.80), "Lid": SKY, "Screw": (0.75, 0.77, 0.80),
       "motherboard": (0.10, 0.11, 0.13), "usbc_p8": (0.62, 0.64, 0.67), "orientation_p13": (0.62, 0.64, 0.67),
       "screen_10_11_cable": (0.86, 0.72, 0.38), "screen_10_11": (0.16, 0.16, 0.18),
       "jumper_housing": (0.06, 0.06, 0.06), "wire_brown": (0.42, 0.22, 0.10), "wire_red": (0.85, 0.10, 0.10),
       "wire_orange": (1.0, 0.50, 0.08), "wire_yellow": (1.0, 0.85, 0.10),
       "Holder": (0.93, 0.93, 0.91), "Bobbin": (0.93, 0.93, 0.91), "Sleeve": (0.93, 0.93, 0.91), "wp_": (0.93, 0.93, 0.91)}

def colour(name):
    for k in sorted(COL, key=len, reverse=True):
        if name.startswith(k):
            return COL[k]
    return (0.7, 0.7, 0.7)

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)
OBJ = {}
for f in sorted(os.listdir(PARTS)):
    if not f.endswith(".stl") or f == "Deck.stl":
        continue
    bpy.ops.wm.stl_import(filepath=os.path.join(PARTS, f))
    o = bpy.context.selected_objects[0]
    n = f[:-4]; o.name = n
    c = colour(n)
    real = bpy.data.materials.new(n + "_real"); real.diffuse_color = (*c, 1)
    g = (0.80, 0.81, 0.83)                           # context parts: pale grey
    if min(c) > 0.75:                                # a white printed part, when it is new: amber
        c = (0.98, 0.70, 0.28)
    full_c = c
    full = bpy.data.materials.new(n + "_full"); full.diffuse_color = (*full_c, 1)
    ghost = bpy.data.materials.new(n + "_ghost"); ghost.diffuse_color = (*g, 1)
    o.data.materials.clear(); o.data.materials.append(full)
    o["full"], o["ghost"], o["real"] = full.name, ghost.name, real.name
    OBJ[n] = o

def group(*prefixes):
    return [n for n in OBJ if any(n == p or n.startswith(p) for p in prefixes)]

BASE = group("frame", "servo_", "femur_", "foot_")
DECK = ["deck_part1", "deck_part2"]
FRAME_SCREWS = ["Screw_1", "Screw_2", "Screw_3", "Screw_4"]
BOTTOM = ["battery", "bottom_cover", "Screw_5", "Screw_6"]
ELEC = group("motherboard", "usbc_p8", "orientation_p13", "screen_10_11")
HOLD = group("Holder_")
BOB = group("Bobbin_")
SLV = group("Sleeve_")
WIRES = group("jumper_housing", "wire_")
WP = group("wp_")
LID = ["Lid", "Screw_7", "Screw_8", "Screw_9"]
ALL = BASE + DECK + FRAME_SCREWS + BOTTOM + ELEC + LID
UPTO5 = BASE + DECK + FRAME_SCREWS + BOTTOM + ELEC

# step: (context parts, new parts, {part: offset}, view direction, (zoom target, half size) or None)
STEPS = {
 "cover":   (ALL + HOLD + BOB, ALL + HOLD + BOB, {}, (1.0, -1.25, 0.85), None),
 "rear":    (ALL + HOLD + BOB + WIRES + SLV, ALL + HOLD + BOB + WIRES + SLV, {}, (0.55, 1.3, 0.75), None),
 "parts":   ([], ["deck_part1", "deck_part2", "Lid"], {"deck_part2": (0, 0, -30), "Lid": (0, 0, 40)}, (1.0, -1.2, 0.7), None),
 "wparts":  ([], WP, {}, (0.55, -1.0, 0.95), None),
 "s1_base": (BASE, BASE, {}, (1.0, -1.25, 0.8), None),
 "s1_slots": (BASE, ["frame"], {}, (0.12, -0.3, -1.4), ((0, 0, 40), 38)),
 "s2_glue": (DECK, DECK, {"deck_part2": (0, 0, -28)}, (1.0, -1.3, 0.45), None),
 "s2_holes": (DECK, ["deck_part2"], {}, (0.45, 1.4, 0.25), ((0, 40, 64), 26)),
 "s3_deck": (BASE + DECK + FRAME_SCREWS, DECK + FRAME_SCREWS,
             {**{d: (0, 0, 28) for d in DECK}, **{s: (0, 0, -34) for s in FRAME_SCREWS}}, (1.0, -1.25, -0.3), None),
 "s4_bottom": (BASE + DECK + FRAME_SCREWS + BOTTOM, BOTTOM,
             {"battery": (0, 0, -30), "bottom_cover": (0, 0, -52), "Screw_5": (0, 0, -72), "Screw_6": (0, 0, -72)}, (1.0, -1.2, -0.65), None),
 "s5_board": (UPTO5, ELEC,
             {"motherboard": (0, 0, 22), "usbc_p8": (0, 0, 40), "orientation_p13": (0, 0, 40)}, (0.9, -1.15, 1.15), None),
 "s6_holders": (UPTO5 + HOLD, HOLD, {h: (0, 0, 16) for h in HOLD}, (1.4, -0.6, 0.9), ((33, -8, 84), 40)),
 "s6_slots": (UPTO5 + ["Lid"], ["deck_part1", "Lid"], {}, (1.5, -0.45, 0.35), ((36, -8, 79), 40)),
 "s6_slots_left": (UPTO5 + ["Lid"], ["deck_part1", "Lid"], {}, (-1.5, -0.45, 0.35), ((-36, -8, 79), 40)),
 "s6_wires": (UPTO5 + HOLD + WIRES + SLV, WIRES + SLV, {}, (1.5, -0.55, 0.5), ((46, -8, 70), 44)),
 "s7_lid":  (ALL + HOLD + WIRES + SLV, LID, {"Lid": (0, 0, 30), "Screw_7": (0, 0, 48), "Screw_8": (0, 0, 48), "Screw_9": (0, 0, 48)}, (0.9, -1.15, 1.0), None),
 "s7_keyholes": (ALL, ["Lid"], {}, (0.35, -0.3, 1.5), ((22, -8, 95), 40)),
 "s7_bobbins": (ALL + HOLD + BOB, BOB, {b: (0, 0, 14) for b in BOB}, (0.9, -1.0, 1.1), ((22, -8, 100), 46)),
 "s7_usb":  (ALL, ["usbc_p8", "Lid", "deck_part1"], {}, (0.25, 1.4, 0.35), ((0, 52, 84), 26)),
}

AMBER = bpy.data.materials.new("amber"); AMBER.diffuse_color = (0.98, 0.70, 0.28, 1)
sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading
sh.light = "STUDIO"; sh.color_type = "MATERIAL"
sh.show_cavity = True; sh.cavity_type = "BOTH"
sh.show_shadows = True; sh.shadow_intensity = 0.35
sh.show_object_outline = True; sh.object_outline_color = (0.15, 0.15, 0.15)
sc.display.render_aa = "16"
sc.render.film_transparent = True
sc.view_settings.view_transform = "Standard"; sc.view_settings.exposure = 0.55
sc.render.resolution_x, sc.render.resolution_y = 1800, 1200
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGBA"
cam_data = bpy.data.cameras.new("cam"); cam_data.type = "ORTHO"; cam_data.clip_end = 5000
cam = bpy.data.objects.new("cam", cam_data); sc.collection.objects.link(cam); sc.camera = cam

for name, (ctx, new, off, d, zoom) in STEPS.items():
    if ONLY and name not in ONLY:
        continue
    vis = set(ctx) | set(new)
    pts = []
    for n, o in OBJ.items():
        o.hide_render = n not in vis
        o.location = Vector(off.get(n, (0, 0, 0)))
        o.data.materials[0] = bpy.data.materials[o["real"] if name in ("cover", "rear", "wparts") else o["full"] if (n in new) else o["ghost"]]
        if name == "s1_slots" and n == "frame":
            o.data.materials[0] = AMBER
        if n in vis:
            pts += [o.matrix_world @ Vector(c) for c in o.bound_box] if False else \
                   [Vector(c) + o.location for c in o.bound_box]
    d = Vector(d).normalized()
    up0 = Vector((0, 0, 1))
    right = d.cross(up0).normalized() * -1 if abs(d.z) < 0.99 else Vector((1, 0, 0))
    right = up0.cross(d).normalized() if abs(d.z) < 0.99 else Vector((1, 0, 0))
    up = d.cross(right).normalized()
    if zoom:
        centre, half = Vector(zoom[0]), zoom[1]
        scale = 2 * half
    else:
        centre = sum(pts, Vector()) / len(pts)
        us = [(p - centre).dot(right) for p in pts]; vs = [(p - centre).dot(up) for p in pts]
        centre = centre + right * (max(us) + min(us)) / 2 + up * (max(vs) + min(vs)) / 2
        w, h = max(us) - min(us), max(vs) - min(vs)
        scale = max(w, h * sc.render.resolution_x / sc.render.resolution_y) * 1.1
    cam_data.ortho_scale = scale
    cam.location = centre + d * 800
    rot = d.to_track_quat("Z", "Y")
    cam.rotation_euler = rot.to_euler()
    sc.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)
    print("rendered", name)
