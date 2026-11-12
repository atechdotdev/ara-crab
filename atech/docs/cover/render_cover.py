"""The README photo (docs/img/cover.png): Cycles, transparent with a shadow.
    blender -b -P render_cover.py -- PARTS_DIR OUT.png      # PARTS_DIR from export_assembled.py
"""
import bpy, os, sys, math
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:]
PARTS, OUT = argv[0], argv[1]
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
def mat(name, rgb, rough=0.5, metal=0.0, coat=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if "Coat Weight" in b.inputs: b.inputs["Coat Weight"].default_value = coat
    return m
def srgb(h):
    c = [((h >> s) & 255) / 255 for s in (16, 8, 0)]
    return tuple((x / 12.92) if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)
M = {"lid": mat("lid", srgb(0x8DA4B8), 0.55), "deck": mat("deck", srgb(0xB9BEC3), 0.5),
     "frame": mat("frame", srgb(0x4A4D52), 0.55), "leg": mat("leg", srgb(0xC9CBCD), 0.45),
     "servo": mat("servo", srgb(0x3F6FA8), 0.4, coat=0.2), "screw": mat("screw", srgb(0xC8CCD0), 0.25, 1.0),
     "dark": mat("dark", srgb(0x2A2C30), 0.3), "battery": mat("battery", srgb(0x6E7378), 0.5)}
def pick(n):
    if n.startswith("Lid"): return M["lid"]
    if n.startswith("Deck"): return M["deck"]
    if n.startswith(("frame", "bottom_cover")): return M["frame"]
    if n.startswith(("femur", "foot")): return M["leg"]
    if n.startswith("servo"): return M["servo"]
    if n.startswith("Screw"): return M["screw"]
    if n.startswith("battery"): return M["battery"]
    return M["dark"]
objs = []
for f in sorted(os.listdir(PARTS)):
    if not f.endswith(".stl"): continue
    bpy.ops.wm.stl_import(filepath=os.path.join(PARTS, f))
    o = bpy.context.selected_objects[0]; o.name = f[:-4]
    o.data.materials.clear(); o.data.materials.append(pick(o.name))
    for p in o.data.polygons: p.use_smooth = False
    mod = o.modifiers.new("ws", "WEIGHTED_NORMAL") if hasattr(o.data, "use_auto_smooth") else None
    objs.append(o)
# the screen behind the head's window: a dark glass panel
bpy.ops.mesh.primitive_cube_add(location=(0, -83.2, 74.5)); sc = bpy.context.object
sc.scale = (19.5, 0.8, 9.5); sc.data.materials.append(mat("glass", (0.012, 0.014, 0.018), 0.08, coat=1.0))
lo = Vector((1e9,)*3); hi = Vector((-1e9,)*3)
for o in objs:
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c); lo = Vector(map(min, lo, w)); hi = Vector(map(max, hi, w))
ctr = (lo + hi) / 2; size = (hi - lo).length
scn = bpy.context.scene
scn.render.engine = "CYCLES"; scn.cycles.samples = 256; scn.cycles.use_denoising = True
try: scn.cycles.device = "GPU"
except Exception: pass
scn.render.resolution_x, scn.render.resolution_y = 1800, 1200
scn.render.film_transparent = True
scn.view_settings.view_transform = "AgX" if "AgX" in [i.identifier for i in scn.view_settings.bl_rna.properties["view_transform"].enum_items] else "Filmic"
# shadow catcher floor
bpy.ops.mesh.primitive_plane_add(size=size * 6, location=(ctr.x, ctr.y, lo.z))
fl = bpy.context.object; fl.is_shadow_catcher = True
# camera, the old cover's direction
d = Vector((1.0, -1.25, 0.85)).normalized()
cam = bpy.data.cameras.new("cam"); cam.lens = 85
co = bpy.data.objects.new("cam", cam); scn.collection.objects.link(co); scn.camera = co
co.location = ctr + d * size * 3.0
co.rotation_euler = (ctr - co.location).to_track_quat("-Z", "Y").to_euler()
# light: soft key, fill, rim, and a studio world
def area(loc, power, sz):
    l = bpy.data.lights.new("a", "AREA"); l.energy = power; l.size = sz
    lo_ = bpy.data.objects.new("a", l); scn.collection.objects.link(lo_); lo_.location = ctr + Vector(loc)
    lo_.rotation_euler = (ctr - lo_.location).to_track_quat("-Z", "Y").to_euler()
area((150, -220, 260), 2.2e5, 160); area((-260, -60, 120), 6e4, 200); area((-80, 260, 200), 9e4, 120)
w = bpy.data.worlds.new("w"); scn.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.9, 0.92, 0.95, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.35
scn.render.filepath = OUT
bpy.ops.render.render(write_still=True)
