"""Export the Atech-made print parts straight from the model (sesame_atech_wired.py), each in
its print orientation (print_to_model.json maps print -> model; this writes model -> print).

    freecadcmd -c "exec(open('export_print.py').read())"      # Atech Atelier's freecadcmd, from atech/cad

From v6.1 the deck and the frame are made here, not cut as meshes: deck part 1, deck part 2
(the spine and the head, two pieces in one file), the lid and Sesame's internal frame with its
lead slots and screw holes. It also reports each joint screw's thread: the kit's M2 screw,
6 mm shank, how much of it passes through clear plastic and how much cuts a thread.
"""
import json
import os
import re
import sys

P = "/Applications/Atech Atelier.app/Contents/Resources/Mod/AcadAgent/projects"
sys.path.insert(0, P)
for d, _, fs in os.walk("/Applications/Atech Atelier.app/Contents/Resources/Mod/AcadAgent"):
    if "atech_geom.py" in fs or "atech_cad.py" in fs:
        sys.path.insert(0, d)
import FreeCAD
import Mesh
import Part

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
OUT = os.path.join(HERE, "..", "print", "stl")
doc = FreeCAD.newDocument("export")
src = open(os.path.join(HERE, "sesame_atech_wired.py")).read()
src = re.sub(r"^.*ViewObject.*$", "", src, flags=re.M)
g = {"doc": doc, "__name__": "model"}
exec(compile(src, "model", "exec"), g)
V = FreeCAD.Vector

# --- each joint screw: clear through the part it enters, a thread in the other
parts = {"part 1": g["deck_p1"], "spine": g["pieces"]["spine"], "head": g["pieces"]["head"], "frame": g["SHAPES"]["frame"]}
shank, r_thread = g["KIT_SCREW"]["shank"], g["KIT_SCREW"]["d"] / 2
bad = 0
for what, x, y, z, sgn in g["JOINT_LOG"]:
    # the shank's 2.0 mm thread envelope, in 0.25 mm steps from under the head
    clear, bite = 0.0, 0.0
    for i in range(int(shank / 0.25)):
        z0 = z + sgn * (i * 0.25)
        seg = Part.makeCylinder(r_thread, 0.25, V(x, y, min(z0, z0 + sgn * 0.25)))
        hit = max(seg.common(s).Volume for s in parts.values())
        if hit < 0.02:
            clear += 0.25
        else:
            bite += 0.25
    head = Part.makeCylinder(g["KIT_SCREW"]["head_d"] / 2, g["KIT_SCREW"]["head_h"],
                             V(x, y, z if sgn < 0 else z - g["KIT_SCREW"]["head_h"]))
    knock = [n for n, s in parts.items() if head.common(s).Volume > 0.05]
    ok = bite >= 3.5 and not knock
    bad += not ok
    print("joint %-18s at (%6.1f, %6.1f): %.2f mm clear, %.2f mm thread%s  %s"
          % (what, x, y, clear, bite, ("; head hits " + ", ".join(knock)) if knock else "", "OK" if ok else "CHECK"))
print("joint screws:", len(g["JOINT_LOG"]), "problems:", bad)

# --- the print STLs
maps = json.load(open(os.path.join(HERE, "print_to_model.json")))
OUTPUTS = [("part1", g["deck_p1"], "deck_part1_plate.stl"),
           ("part2", Part.makeCompound([g["pieces"]["spine"], g["pieces"]["head"]]), "deck_part2_spine_and_head.stl"),
           ("lid", g["lid"], "lid_print_upside_down.stl"),
           ("frame", g["SHAPES"]["frame"], "Internal-Frame-v121-wired.stl")]
for key, shape, name in OUTPUTS:
    M = FreeCAD.Matrix(*[c for row in maps[key] for c in row])
    s = shape.copy()
    s.transformShape(M.inverse())          # model -> print
    bb = s.BoundBox
    Mesh.Mesh(s.tessellate(0.02)).write(os.path.join(OUT, name))
    print("wrote %-34s %d solid(s), %.1f mm3, print z %.2f..%.2f" % (name, len(s.Solids), s.Volume, bb.ZMin, bb.ZMax))
