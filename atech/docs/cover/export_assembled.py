"""The assembled v6.3 model, one STL per part, for render_cover.py.
    PARTS=/some/dir freecadcmd -c "exec(open(x27export_assembled.pyx27).read())"   # Atech Atelier freecadcmd
"""
import os, re, sys
HERE = "/Users/davidatech/dev/atech/New_Spyder/atech/cad"
P = "/Applications/Atech Atelier.app/Contents/Resources/Mod/AcadAgent/projects"
sys.path.insert(0, P)
for d, _, fs in os.walk("/Applications/Atech Atelier.app/Contents/Resources/Mod/AcadAgent"):
    if "atech_geom.py" in fs or "atech_cad.py" in fs:
        sys.path.insert(0, d)
os.chdir(HERE)
import FreeCAD, Mesh, MeshPart
doc = FreeCAD.newDocument("cov")
src = open(os.path.join(HERE, "sesame_atech_wired.py")).read()
src = re.sub(r"^.*ViewObject.*$", "", src, flags=re.M)
g = {"doc": doc, "__name__": "model", "__file__": os.path.join(HERE, "sesame_atech_wired.py")}
exec(compile(src, "model", "exec"), g)
OUT = os.environ["PARTS"]; os.makedirs(OUT, exist_ok=True)
for o in doc.Objects:
    if not hasattr(o, "Shape") or o.Shape.isNull() or o.Shape.Volume < 1e-3 or not o.Visibility and False:
        continue
    m = MeshPart.meshFromShape(Shape=o.Shape, LinearDeflection=0.03, AngularDeflection=0.2)
    m.write(os.path.join(OUT, o.Label + ".stl"))
    print("EXP", o.Label, round(o.Shape.Volume))
