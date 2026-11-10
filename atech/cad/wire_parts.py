"""Wire parts for Atech-crab: a jumper holder for each servo port, a sleeve for each servo plug, a bobbin per leg.

    freecadcmd -c "exec(open('wire_parts.py').read())"     # Atech Atelier's freecadcmd

Port jumper holder (4, ports 2-5; the same part turned round fits ports 10-13). It holds the
three male-to-male jumpers of a port, GND, line A and line B (pins 4, 5, 6), in a row at
2.54 mm, and is solid over pins 1-3 (+12 V, 5 V, 3.3 V), so no jumper can reach them. It sits
between the board's edge and the side wall, its tongue in the deck's port slot; the lid traps
it. Pin 1 is at the front (-Y) of ports 2-5: the SDK's 14-port pin map, checked on a board
(a module goes in with +12 V on its left). The channel is 1.2 mm off the slot's middle, so
upside down the jumpers meet the PCB and it does not go in.
Checked against this model (sesame_atech_wired.py): no overlap with the deck, the lid or
any Sesame part; it stays inside the deck's outline (x <= 37.9, the deck's side at 38).

Servo plug sleeve (8): a tube over a servo's 3-pin plug and the jumpers plugged into it,
so they cannot pull apart. Thread it on before plugging in.

Wire bobbin (4, one per leg): sits on the lid's top by its port and holds the port's slack, both
servo leads and the jumpers, wound round its core. Two mushroom pegs go into the lid's keyholes
(sesame_atech_wired.py, WIRE BOBBIN KEYHOLES) and slide 4 mm outward to lock. Checked at all ten
ports, locked and at the entry: no overlap with the lid, the deck, the screws, the board or the
modules, and the pegs' heads slide clear under the lid's skin. Printed upside down, pegs up.

Writes the STLs to ../print/stl_wires/ (one file per part to print).
"""
import sys, re, os
P = "/Applications/Atech Atelier.app/Contents/Resources/Mod/AcadAgent/projects"
sys.path.insert(0, P)
for d, _, fs in os.walk("/Applications/Atech Atelier.app/Contents/Resources/Mod/AcadAgent"):
    if "atech_geom.py" in fs or "atech_cad.py" in fs: sys.path.insert(0, d)
import FreeCAD, Part, Mesh
from FreeCAD import Vector as V
doc = FreeCAD.newDocument("m")
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()   # run it from atech/cad
src = open(os.path.join(HERE, "sesame_atech_wired.py")).read()
src = re.sub(r"^.*ViewObject.*$", "", src, flags=re.M)
g = {"doc": doc, "__name__": "model"}
exec(compile(src, "model", "exec"), g)
OUT = os.path.join(HERE, "..", "print", "stl_wires") + "/"
os.makedirs(OUT, exist_ok=True)

def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))

# --- the holder, in a port frame: y = along the row from the row centre toward pin 6
#     (pin k at (k - 3.5) * 2.54), x / z = the model's (mouth at the port, wall at 36..38)
PIN = 2.54; HC = PIN / 2 + 0.15          # half channel cell: a 2.54 mm Dupont housing + 0.15
ZC = 83.65                               # contact centreline
SLOT_HALF = (15.64 + 1.0) / 2            # the deck slot: housing + 0.5 a side
X_B0, X_T0, X_T1 = 30.3, 35.8, 37.9      # body (in the bay) from past the PCB edge (29.99); tongue in the wall slot
Z0, Z1 = 79.65, 86.45                    # slot 79.45..86.65, 0.2 clear
CH_Y0, CH_Y1 = 1 * PIN / 2 - HC, 5 * PIN / 2 + HC    # pins 4..6 (y +1.27..+6.35)
CH_Z0, CH_Z1 = ZC - HC, ZC + HC
YL = -SLOT_HALF + 0.2                    # solid over pins 1..3, against the slot's pin-1 end
body = box(X_B0, X_T0, YL, CH_Y1 + 1.2, Z0, Z1)
tongue = box(X_T0 - 0.01, X_T1, YL, CH_Y1, Z0, Z1)       # +Y side open in the slot (only wires there)
chan = box(X_B0 - 1, X_T1 + 1, CH_Y0, CH_Y1, CH_Z0, CH_Z1)
holder = body.fuse(tongue).removeSplitter().cut(chan)
# lead-in chamfer at the board end of the channel
print("holder bbox (port frame)", holder.BoundBox, "vol", round(holder.Volume, 1))
print("walls: roof %.2f floor %.2f +Y %.2f, -Y block %.2f" % (Z1 - CH_Z1, CH_Z0 - Z0, 1.2, CH_Y0 - YL))

# place on ports 2..5: +Y in the port frame = toward pin 6 = +Y in the model (pin 1 at -Y)
import numpy as np
centres = {2: -38.0, 3: -18.0, 4: 2.2, 5: 22.1}
deck, lid, board = g["deck"], g["lid"], g["board"]
others = {n: g["SHAPES"][n] for n in g["SHAPES"]}
placed = []
for n, yc in centres.items():
    h = holder.copy(); h.translate(V(0, yc, 0)); placed.append(h)
    for nm, s in [("Deck", deck), ("Lid", lid)] + list(others.items()):
        v = h.common(s).Volume
        if v > 1e-3: print("  port", n, "overlaps", nm, round(v, 3))
    # flipped upside down about the contact line: the jumpers' housings drop 2.4 mm -> into the PCB?
print("PCB top", round(g["PCB_TOP"], 2), "| channel floor", round(CH_Z0, 2), "| flipped channel floor", round(Z0 + Z1 - CH_Z1, 2))
# the jumpers themselves: 2.54 sq x 14 housing from the mouth, check they clear deck/lid
for n, yc in centres.items():
    for k in (4, 5, 6):
        y = yc + (k - 3.5) * PIN
        j = box(21.8, 35.8, y - 1.27, y + 1.27, ZC - 1.27, ZC + 1.27)
        for nm, s in (("Deck", deck), ("Lid", lid)):
            v = j.common(s).Volume
            if v > 1e-3: print("  jumper", n, k, "hits", nm, round(v, 3))
# export: print orientation = as placed (floor face down), origin at 0
hp = holder.copy(); bb = hp.BoundBox; hp.translate(V(-bb.XMin, -bb.YMin, -bb.ZMin))
for i in range(1, 5):
    Mesh.Mesh(hp.tessellate(0.02)).write(OUT + "port_jumper_holder_%d.stl" % i)
# servo coupler: a sleeve over the servo plug and the jumper housings plugged into it
IW, IH, W, L = 8.3, 3.4, 1.2, 24.0
sleeve = box(0, IW + 2 * W, 0, L, 0, IH + 2 * W).cut(box(W, W + IW, -1, L + 1, W, W + IH))
for i in range(1, 9):
    Mesh.Mesh(sleeve.tessellate(0.02)).write(OUT + "servo_plug_sleeve_%d.stl" % i)
# --- wire bobbin (4, one per leg): on the lid's top by its servo port, both servo leads and
#     the port's jumpers wound round its core. Two mushroom pegs under it go into the lid's
#     keyholes (sesame_atech_wired.py, WIRE BOBBIN KEYHOLES) and slide 4 mm outward to lock.
#     Built in a +X port frame: x = |x| in the model, z = 0 on the lid's top.
import atech_cad as cad
LT = g["LID_TOP"]
NECK_R, NECK_L, HEAD_R = 1.5, 2.05, 2.7          # skin 2.0; keyhole slot 3.4, entry 6.0
def bobbin_shape(span):
    xb0, xb1 = span; xc = (xb0 + xb1) / 2; W, Y = xb1 - xb0, 9.0
    base = cad.rounded_box(W, 2 * Y, 1.6, 3.0, at=(xb0, -Y, 0))
    core = cad.rounded_box(W - 6, 7.0, 9.01, 3.0, at=(xb0 + 3, -3.5, 1.6 - 0.005))
    top = cad.rounded_box(W, 2 * Y, 1.6, 3.0, at=(xb0, -Y, 10.6))
    b = cad.fuse_one(base, core, top)
    # a slit in the top flange's long edges: pinch each lead's end there
    b = cad.cut(b, [box(xc - 0.7, xc + 0.7, Y - 4, Y + 1, 10.5, 12.3),
                    box(xc - 0.7, xc + 0.7, -Y - 1, -Y + 4, 10.5, 12.3)])
    for d in (-g["PEG_DX"], g["PEG_DX"]):
        x = xc + d
        neck = Part.makeCylinder(NECK_R, NECK_L + 0.01, V(x, 0, -NECK_L))
        cone = Part.makeCone(HEAD_R, NECK_R, HEAD_R - NECK_R, V(x, 0, -NECK_L - (HEAD_R - NECK_R)))
        cyl = Part.makeCylinder(HEAD_R, 0.6, V(x, 0, -NECK_L - (HEAD_R - NECK_R) - 0.6))
        b = cad.fuse_one(b, neck, cone, cyl)
    return b.removeSplitter()

def place_bobbin(b, n, dx=0.0):
    """Into the model on port n's keyholes; dx = 0 locked, -4 at the entry."""
    s = b.copy()
    if n > 6: s.mirror(V(0, 0, 0), V(1, 0, 0))
    s.translate(V((dx if n <= 6 else -dx), g["BOBBIN_Y"][n], LT))
    return s

others_all = []
for o in doc.Objects:
    try: sh = Part.getShape(o)          # the board and the modules are App::Parts
    except Exception: continue
    if sh is None or sh.isNull() or o.Name.startswith("Holder") or sh.Volume < 1e-6: continue
    if o.Name == "Lid": continue
    others_all.append((o.Name, sh))
bad = 0
for n in g["BOBBIN_Y"]:
    b = bobbin_shape(g["bobbin_span"](n))
    for dx in (0.0, -g["KEY_TRAVEL"]):
        p = place_bobbin(b, n, dx)
        v = p.common(lid).Volume
        if dx == 0.0 and v > 1e-3: print("  bobbin", n, "locked: overlaps the lid", round(v, 3)); bad += 1
        for nm, s in others_all + [("Deck", deck)]:
            v = p.common(s).Volume
            if v > 1e-3: print("  bobbin", n, dx, "hits", nm, round(v, 3)); bad += 1
    # the head's slide path under the skin, entry to lock
    sx = 1 if n <= 6 else -1
    for d in (-g["PEG_DX"], g["PEG_DX"]):
        xl = sx * (sum(g["bobbin_span"](n)) / 2 + d)
        path = cad.fuse_one(Part.makeCylinder(HEAD_R, 2.2, V(xl, g["BOBBIN_Y"][n], LT - 2 - 2.2)),
                            Part.makeCylinder(HEAD_R, 2.2, V(xl - sx * 4, g["BOBBIN_Y"][n], LT - 2 - 2.2)),
                            box(min(xl, xl - sx * 4), max(xl, xl - sx * 4), g["BOBBIN_Y"][n] - HEAD_R, g["BOBBIN_Y"][n] + HEAD_R, LT - 4.2, LT - 2))
        for nm, s in others_all + [("Lid", lid), ("Deck", deck)]:
            v = path.common(s).Volume
            if v > 1e-3: print("  peg path", n, round(xl, 1), "hits", nm, round(v, 3)); bad += 1
    # the board, the modules (meshes) and the ribbons: no point of theirs in the path
    for o in doc.Objects:
        if o.TypeId == "Mesh::Feature": pts = [(p.x, p.y, p.z) for p in o.Mesh.Points]
        elif o.Name.startswith("screen_"): pts = [(p.x, p.y, p.z) for p in o.Shape.tessellate(0.2)[0]]
        else: continue
        for d in (-g["PEG_DX"], g["PEG_DX"]):
            xl = sx * (sum(g["bobbin_span"](n)) / 2 + d); xs = sorted((xl, xl - sx * 4)); y = g["BOBBIN_Y"][n]
            hit = [p for p in pts if xs[0] - HEAD_R - 0.3 < p[0] < xs[1] + HEAD_R + 0.3 and abs(p[1] - y) < HEAD_R + 0.3 and p[2] > LT - 4.5]
            if hit: print("  peg path", n, round(xl, 1), "near", o.Name, "top z", round(max(p[2] for p in hit), 2)); bad += 1
print("bobbins checked at ports", sorted(g["BOBBIN_Y"]), "problems:", bad)
bb_bay = bobbin_shape(g["BOBBIN_X"]["bay"])
# print it upside down: top flange on the plate, pegs up (the head's 45-degree cone prints unsupported)
bp = bb_bay.copy(); bp.rotate(V(0, 0, 0), V(1, 0, 0), 180); bb = bp.BoundBox; bp.translate(V(-bb.XMin, -bb.YMin, -bb.ZMin))
for i in range(1, 5):
    Mesh.Mesh(bp.tessellate(0.02)).write(OUT + "wire_bobbin_%d.stl" % i)
bbk = bobbin_shape(g["BOBBIN_X"]["back"])     # the narrower-placed one for ports 6 / 14 is the same part
print("bobbin bbox", bb_bay.BoundBox, "vol", round(bb_bay.Volume, 1))

# a review scene: model + holders + bobbins on ports 2-5
for i, h in enumerate(placed):
    o = doc.addObject("Part::Feature", "Holder_%d" % (i + 2)); o.Shape = h
for n in (2, 3, 4, 5):
    o = doc.addObject("Part::Feature", "Bobbin_%d" % n); o.Shape = place_bobbin(bb_bay, n)
REVIEW = os.environ.get("WIRE_REVIEW_DIR")
if REVIEW:
    os.makedirs(REVIEW, exist_ok=True)
    for o in doc.Objects:
        if o.TypeId == "Mesh::Feature":
            o.Mesh.write(os.path.join(REVIEW, o.Name + ".stl")); continue
        try: sh = Part.getShape(o)
        except Exception: continue
        if sh is None or sh.isNull() or sh.Volume < 1e-6: continue
        Mesh.Mesh(sh.tessellate(0.1)).write(os.path.join(REVIEW, o.Name + ".stl"))
print("wrote", OUT)
