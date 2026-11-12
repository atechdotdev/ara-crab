"""Slice the Atech-crab parts for Bambu printers with the full system profiles.

Bambu keeps each printer's start/end G-code in separate "template" profiles. Loading
only `Bambu Lab H2S 0.4 nozzle.json` into the CLI falls back to fdm_machine_common's
generic Marlin start G-code (G28, G29, a purge line at X10), which skips the Bambu
homing and Z probing: the printer then starts printing in the air. This script resolves
each profile's `inherits` chain itself, merges the template G-codes in, and hands the
CLI flat profiles.

    python slice.py out_dir [printer ...]     # printers: see PRINTERS (default: all)
    python slice.py out_dir p2s --parts stl_wires --name atech_crab_wires   # another set of parts
    python slice.py out_dir h2s --parts stl_all --name atech_crab_everything --project   # unsliced project
"""
import json
import pathlib
import subprocess
import sys
import tempfile

APP = pathlib.Path("/Applications/BambuStudio.app/Contents")
CLI = APP / "MacOS/BambuStudio"
PROFILES = APP / "Resources/profiles/BBL"
HERE = pathlib.Path(__file__).parent
STL = sorted((HERE / "stl").glob("*.stl"))
NAME = "atech_crab"
NOZZLE = "1"         # --left: a two-nozzle printer prints with its left nozzle (fed by the Left AMS)
PROJECT = False      # --project: an unsliced Bambu Studio project .3mf (parts placed, settings in), to share

PRINTERS = {
    "h2s": ("Bambu Lab H2S 0.4 nozzle", "0.20mm Standard @BBL H2S", "@BBL H2S"),
    "h2d": ("Bambu Lab H2D 0.4 nozzle", "0.20mm Standard @BBL H2D", "@BBL H2D"),
    "x2d": ("Bambu Lab X2D 0.4 nozzle", "0.20mm Standard @BBL X2D", "@BBL X2D"),
    "p2s": ("Bambu Lab P2S 0.4 nozzle", "0.20mm Standard @BBL P2S", "@BBL P2S"),
    "x1c": ("Bambu Lab X1 Carbon 0.4 nozzle", "0.20mm Standard @BBL X1C", "@BBL X1C"),
    "x1": ("Bambu Lab X1 0.4 nozzle", "0.20mm Standard @BBL X1C", "@BBL X1"),
    "x1e": ("Bambu Lab X1E 0.4 nozzle", "0.20mm Standard @BBL X1C", "@BBL X1C"),
    "p1s": ("Bambu Lab P1S 0.4 nozzle", "0.20mm Standard @BBL X1C", "@BBL P1S"),
    "a1": ("Bambu Lab A1 0.4 nozzle", "0.20mm Standard @BBL A1", "@BBL A1"),
    "a1m": ("Bambu Lab A1 mini 0.4 nozzle", "0.20mm Standard @BBL A1M", "@BBL A1M"),
    "a2l": ("Bambu Lab A2L 0.4 nozzle", "0.20mm Standard @BBL A2L", "@BBL A2L"),
    "h2c": ("Bambu Lab H2C 0.4 nozzle", "0.20mm Standard @BBL H2C", "@BBL H2C"),
    "h2dp": ("Bambu Lab H2D Pro 0.4 nozzle", "0.20mm Standard @BBL H2DP", "@BBL H2DP"),
}
FILAMENTS = {"pla": "Bambu PLA Basic", "petg": "Bambu PETG Basic"}
JOBS = [(p, "pla") for p in PRINTERS]   # every Bambu printer with a PLA Basic profile (the P1P: use the P1S file)

# Supports where the parts need them: tree, from the build plate only, so no support
# grows on a part's own surface (the servo pockets stay clean).
PRINT_OVERRIDES = {
    "enable_support": "1",
    "support_type": "tree(auto)",
    "support_on_build_plate_only": "1",
    "support_threshold_angle": "40",
    "brim_type": "auto_brim",
    "wall_loops": "2",
    "sparse_infill_density": "15%",
    "sparse_infill_pattern": "gyroid",
    "curr_bed_type": "Textured PEI Plate",   # the default Cool Plate refuses PETG
}


def _index(kind):
    out = {}
    for f in (PROFILES / kind).glob("*.json"):
        try:
            d = json.loads(f.read_text())
        except ValueError:
            continue
        if "name" in d:
            out[d["name"]] = d
    return out


def resolve(index, name):
    d = index[name]
    base = resolve(index, d["inherits"]) if d.get("inherits") else {}
    return {**base, **d}


def preset(kind, system_name, extra=None):
    """The system profile with its `inherits` chain resolved and, for a printer, its
    G-code templates merged in. It keeps the system name and `from: system`: the CLI
    matches the process's `compatible_printers` against the printer by that name."""
    index = _index(kind)
    d = resolve(index, system_name)
    if kind == "machine":
        for tname, t in index.items():
            if tname.startswith(system_name + " template "):
                d.update({k: v for k, v in t.items() if k not in ("name", "instantiation", "inherits", "from", "type")})
    d.update(extra or {})
    d.update({"name": system_name, "from": "system", "inherits": "", "type": kind, "instantiation": "true"})
    return d


GAP = 10.0   # mm between parts: room for the auto brim and tree supports


def layout(machine, out):
    """Place the parts on plates (MaxRects, see below) and write each plate's parts to
    out/plate<n>/. Whatever does not fit on a plate goes on the next: on a 256 mm bed
    that makes two plates, each its own file, so every print is a plain one-plate job.
    (The CLI's own arrange also spills onto a second plate, inside one file.)"""
    import trimesh

    d = preset("machine", machine)
    area = d["printable_area"]
    if d.get("extruder_printable_area"):   # two nozzles: only where both reach
        areas = [[tuple(map(float, q.strip().split("x"))) for q in a.split(",")] for a in d["extruder_printable_area"]]
        lo_x = max(min(x for x, _ in a) for a in areas); hi_x = min(max(x for x, _ in a) for a in areas)
        lo_y = max(min(y for _, y in a) for a in areas); hi_y = min(max(y for _, y in a) for a in areas)
        area = [f"{lo_x}x{lo_y}", f"{hi_x}x{hi_y}"]
    xs, ys = zip(*(map(float, p.strip().split("x")) for p in area))
    excl = [tuple(map(float, p.strip().split("x"))) for p in d.get("bed_exclude_area") or []]
    x_min, y_min = min(xs) + GAP, min(ys) + GAP + (max(y for _, y in excl) if excl else 0)
    x_max, y_max = max(xs) - GAP, max(ys) - GAP
    todo = []
    for f in STL:
        m = trimesh.load(f, force="mesh")
        m.apply_translation(-m.bounds[0])
        todo.append((f.name, m))
    # MaxRects (best short side fit): each part's footprint plus GAP, into the free rectangles
    # left on the plate, turned 90 degrees where that fits better; biggest parts first, so
    # small ones fill the gaps beside them. What does not fit goes on the next plate.
    todo.sort(key=lambda t: -t[1].extents[0] * t[1].extents[1])
    plates = []
    while todo:
        free, placed, left = [(x_min, y_min, x_max - x_min + GAP, y_max - y_min + GAP)], [], []
        for name, m in todo:
            best = None
            for rot in (False, True):
                w, h = m.extents[:2] + GAP
                if rot: w, h = h, w
                for fx, fy, fw, fh in free:
                    if w <= fw + 1e-6 and h <= fh + 1e-6:
                        score = (min(fw - w, fh - h), max(fw - w, fh - h))
                        if best is None or score < best[0]:
                            best = (score, fx, fy, w, h, rot)
            if best is None:
                left.append((name, m))
                continue
            _, px, py, w, h, rot = best
            q = m.copy()
            if rot:
                q.apply_transform(trimesh.transformations.rotation_matrix(1.5707963, [0, 0, 1]))
                q.apply_translation(-q.bounds[0])
            placed.append((name, q.apply_translation([px, py, 0])))
            nf = []
            for fx, fy, fw, fh in free:   # split every free rectangle the part overlaps
                if px >= fx + fw or px + w <= fx or py >= fy + fh or py + h <= fy:
                    nf.append((fx, fy, fw, fh)); continue
                if px > fx: nf.append((fx, fy, px - fx, fh))
                if px + w < fx + fw: nf.append((px + w, fy, fx + fw - px - w, fh))
                if py > fy: nf.append((fx, fy, fw, py - fy))
                if py + h < fy + fh: nf.append((fx, py + h, fw, fy + fh - py - h))
            free = [a for a in nf if not any(a != b and b[0] <= a[0] and b[1] <= a[1] and
                                             a[0] + a[2] <= b[0] + b[2] and a[1] + a[3] <= b[1] + b[3] for b in nf)]
        if not placed:
            raise SystemExit(f"{machine}: {todo[0][0]} does not fit on the bed")
        folder = out / f"plate{len(plates) + 1}"
        folder.mkdir()
        for name, m in placed:
            m.export(folder / name)
        plates.append(sorted(folder.glob("*.stl")))
        todo = left
    return plates


def slice_one(printer, fil, out_dir):
    machine, process, suffix = PRINTERS[printer]
    names = _index("filament")   # some are "... @BBL X2D 0.4 nozzle", some "... @BBL H2S"
    filament = next(n for n in (f"{FILAMENTS[fil]} {suffix}", f"{FILAMENTS[fil]} {suffix} 0.4 nozzle") if n in names)
    outs = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        paths = {}
        # a two-nozzle printer (H2D) refuses "auto" nozzle choice from the CLI: one filament, nozzle 1
        dual = len(preset("machine", machine).get("extruder_printable_area") or []) > 1
        mextra = {"filament_map_mode": "Manual", "filament_map": [NOZZLE]} if dual else None
        for kind, name, extra in (("machine", machine, mextra), ("process", process, PRINT_OVERRIDES),
                                  ("filament", filament, None)):
            p = tmp / f"{kind}.json"
            p.write_text(json.dumps(preset(kind, name, extra)))
            paths[kind] = p
        parts = tmp / "parts"
        parts.mkdir()
        plates = layout(machine, parts)
        for i, stls in enumerate(plates, 1):
            tag = f"_plate{i}" if len(plates) > 1 else ""
            out = out_dir / f"{NAME}_{fil}_{printer}{tag}{'' if PROJECT else '.gcode'}.3mf"
            cmd = [str(CLI), "--arrange", "0", "--orient", "0", *([] if PROJECT else ["--slice", "0"]),
                   "--load-settings", f"{paths['machine']};{paths['process']}",
                   "--load-filaments", str(paths["filament"]),
                   "--export-3mf", str(out), *map(str, stls)]
            r = subprocess.run(cmd, capture_output=True, text=True, cwd=tmp)
            if r.returncode != 0 or not out.exists():
                sys.exit(f"{out.name}: slicing failed ({r.returncode})\n{r.stdout[-3000:]}\n{r.stderr[-3000:]}")
            print(out, "  ", ", ".join(s.stem for s in stls))
            outs.append(out)
    return outs


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--left" in args:
        args.remove("--left"); NOZZLE = "2"
    if "--project" in args:
        args.remove("--project"); PROJECT = True
    for flag in ("--parts", "--name"):
        if flag in args:
            i = args.index(flag)
            if flag == "--parts":
                STL = sorted((HERE / args[i + 1]).glob("*.stl"))
            else:
                NAME = args[i + 1]
            del args[i:i + 2]
    out_dir = pathlib.Path(args[0])
    out_dir.mkdir(parents=True, exist_ok=True)
    want = args[1:]          # printers ("x2d"), or printer:filament ("x2d:petg")
    if any(":" in w for w in want):
        jobs = [tuple(w.split(":")) if ":" in w else (w, "pla") for w in want]
    else:
        jobs = [(p, f) for p, f in JOBS if not want or p in want]
    for printer, fil in jobs:
        slice_one(printer, fil, out_dir)
