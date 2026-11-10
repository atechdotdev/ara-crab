"""Example: "the Sesame walking robot refitted for the Atech board and screen, same servos"

Atelier 0.1.3's sesame_atech.py plus wire openings (2026-11-02): the USB-C opening
reaches 5 mm lower, through the lid/deck seam; a slot at servo ports 2-5 and an
SG90 lead notch under each; (v4, 2026-11-03) the same slots and notches on the
other side, at ports 10-13; and (v5, 2026-11-09) at the back ports 6 and 14. See the
WIRE OPENINGS block. (v6, 2026-11-09) a pair of keyholes in the lid's top at each servo
port, for the clip-on wire bobbins (WIRE BOBBIN KEYHOLES), and eight holes through the
spine's end walls, one per servo lead (SPINE LEAD HOLES).

A remix of an open design. Sesame (Dorian Todd's quadruped, Apache-2.0)
keeps everything below its top cover exactly as upstream prints it: the
internal frame, the bottom cover, the 14500 battery, the eight MG90S servos
and the eight leg parts (agent_kit/third_party/sesame, see its NOTICE.md; its
STEP made into BREPs by projects/import_sesame.py). Only the top cover is new:

  Deck  screws onto the frame with the original four M2 screws. A spine the
        width of the original cover rises between the hips to a tray just
        over the femurs, which holds the Atech 14-port board flat on four
        posts with a 5 mm gap under it for the cables, and a head in front
        that holds the screen behind a 36 x 17 mm window.
  Lid   closes the tray and the head (fitted after the modules), three M2
        screws down into bosses in the deck's side bays, and holds the
        screen's back with a rib.

Hardware: the board lies flat, the USB-C module on port 8 at the back, the
IMU ("orientation", the SDK's icm40608: the walk steers by its heading) on
port 13, the screen cabled from ports 10+11, upright in the head with its
connector edge down. Its two ribbons loop down into the right bay, run flat
under the board and come up into the screen from below. The servo leads plug
into ports 2-5 (one leg each: hip on line A, knee on line B) and drop through
the spine to the servos.

The outline is MEASURED, not guessed: every pose of the firmware's
movement-sequences.h replayed on these legs. Above the femur tops the legs
reach the front and rear corners beyond |x| 37 and x 12..26 behind y 56 (the
dance pose lifts the rear feet there). So the tray is |x| <= 32.3 at both
ends, the side bays reach |x| 38 only between y -49.5 and 40 (a 36.8 step in
front of that), the back wall stops at y 54.9, and the head (|x| <= 23, down
to z 64) sits where no leg rises above z 57.

Numbered features: 1 spine with the four frame screw bosses; 2 tray floor and
lead slot; 3 board posts; 4 tray walls up to the board's top face; 5 side bays;
6 head with the screen window and its side ribs; 7 lid with the USB-C opening
and the screen's back rib; 8 lid screws into bay bosses.
"""
import gzip
import os

import Part
from FreeCAD import Vector, Placement, Rotation

import atech_geom
import atech_ports as ap
import atech_cad as cad

V = Vector
PARTS_DIR = os.path.join(os.path.dirname(atech_geom.__file__), "third_party", "sesame")


def sesame(name):
    """One upstream Sesame part, already in this frame (z up, front -Y)."""
    s = Part.Shape()
    with gzip.open(os.path.join(PARTS_DIR, name + ".brep.gz"), "rt", encoding="utf-8") as fh:
        s.importBrepFromString(fh.read())
    return s.Solids[0]


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def plan(pieces, z0, z1, grow=0.0):
    """Fuse rounded plan pieces (x0, x1, y0, y1, r) into one prism z0..z1,
    each grown by `grow` (negative shrinks: a wall's inside)."""
    return cad.fuse_one(*[cad.rounded_box(x1 - x0 + 2 * grow, y1 - y0 + 2 * grow, z1 - z0,
                                          max(0.5, r + grow), at=(x0 - grow, y0 - grow, z0))
                          for x0, x1, y0, y1, r in pieces])


UPSTREAM = ["frame", "bottom_cover", "battery"] + \
    ["femur_" + k for k in ("L1", "L2", "R1", "R2")] + ["foot_" + k for k in ("L3", "L4", "R3", "R4")] + \
    ["servo_%s_%s" % (j, s) for j in ("hip", "knee") for s in ("FL", "FR", "RL", "RR")]
SHAPES = {n: sesame(n) for n in UPSTREAM}

# === PARAMETERS (measured from the upstream parts where they matter) ===
FRAME_TOP = SHAPES["frame"].BoundBox.ZMax                      # 53.80
FEMUR_TOP = max(SHAPES["femur_" + k].BoundBox.ZMax for k in ("L1", "L2", "R1", "R2"))   # 71.75
FRAME_SCREW_Z = FRAME_TOP - 1.27     # the screws' heads sit under the frame's 1.27 mm top plate
FRAME_SCREWS = ((16.785, 36.04), (-16.785, 36.04), (15.93, -33.62), (-15.93, -33.62))
BOTTOM_SCREW_Z = SHAPES["bottom_cover"].BoundBox.ZMax - 1.27 - 0.2   # 0.2 mm under its seat
BOTTOM_SCREWS = ((0.0, -29.46), (0.0, 30.67))
SPINE = 18.5                 # half width: the original cover's (18.69); the femurs swing outside it
SPINE_Y = 39.61              # the frame's ends
WALL = 2.0
FLOOR_Z0 = FEMUR_TOP + 1.2   # tray underside, over the femur tops
LEAD_GAP = 5.0               # under the board: the ribbons and servo leads
BOARD_Y = -8.0               # board centre: 8 mm forward, clear of the rear feet (back wall < y 56)
CLEAR = 0.3                  # round the board
BAY_X, BAY_Y = 38.0, (-49.5, 40.0)  # MEASURED: above the floor the legs stay beyond |x| 39.7 there
HEAD_X, HEAD_Z0 = 23.0, 64.0
LID_SCREWS = ((33.3, 35.5), (-33.3, 35.5), (-33.3, -2.5))   # in the bays, clear of leads, ribbons, the IMU and the walls
COLOURS = {"frame": "graphite", "bottom": "graphite", "battery": "satin_grey",
           "femur": "matte_white", "foot": "matte_white", "servo": "toy_blue",
           "Deck": "matte_white", "Lid": "sky", "Screw": "chrome"}

# === HARDWARE ===
board = ap.board_object(doc)
FLAT_BACK = Rotation(V(0, 0, 1), 180).multiply(Rotation(V(1, 0, 0), 90))   # components up, port 8 at +Y
board.Placement = Placement(V(), FLAT_BACK)
b0 = ap.bbox(board)
BOARD_Z0 = FLOOR_Z0 + WALL + LEAD_GAP
board.Placement = Placement(V(-(b0.XMin + b0.XMax) / 2, BOARD_Y - (b0.YMin + b0.YMax) / 2,
                              BOARD_Z0 - b0.ZMin), FLAT_BACK)
BB = ap.bbox(board)
PCB_TOP = BB.ZMin + 2.5      # the face modules seat on (MEASURED: 2.5 above the underside)
usb = ap.seat(doc, "usbc", 8)
imu = ap.seat(doc, "orientation", 13)       # heading for the walk (the firmware steers by it)
UB = ap.bbox(usb)
X0, X1 = BB.XMin - CLEAR - WALL, BB.XMax + CLEAR + WALL
Y0 = BB.YMin - CLEAR - WALL                  # front of the tray
Y1 = UB.YMax + 0.25 + WALL                   # back wall just behind the USB-C mouth
HY0 = Y0 - 15.0                              # front of the head
FT, BU = FLOOR_Z0 + WALL, BB.ZMin            # floor top, board underside
# the screen: upright behind the head's front wall (0.2 mm off it), its
# connector edge down; the ribbons run flat under the board, one above the
# other, and come up into it from below
SCREEN_C = (0.0, HY0 + WALL + 0.2 + 9.64 / 2, BU - 8.6 + 19.5 / 2)
# the ribbons' waypoints: found by an offline search over this geometry
# (no ribbon within 0.3 mm of the board, the floor, the bay walls, the
# screen or the lid; 1.0 mm between them; no twist) - each leaves its plug
# outward, loops down into the bay, runs flat under the board (port 10's
# low, port 11's above it) and drops in front of the board into the screen
ROUTE = {
    10: [(-34.69, -38.52, 81.25), (-34.32, -38.9, 78.31), (-26.87, -41.63, 78.56),
         (-22.72, -46.71, 78.44), (-14.32, -61.97, 78.07), (-12.8, -69.35, 78.0),
         (-10.21, -72, 72.08), (-8.71, -73.86, 68.07)],
    11: [(-33.86, -18.94, 81.89), (-32.65, -18.38, 77.88), (-27.53, -21.92, 77.51),
         (-12.12, -39.25, 76.21), (-2.21, -53.92, 78.28), (9.34, -66.29, 77.49),
         (9.7, -70.03, 76.26), (9.89, -72.2, 74.18), (10.32, -72.07, 68.51)]}
scr, ribbons = ap.cable(doc, "screen", (10, 11), ap.module_placement(
    "screen", SCREEN_C, face="-Y", cable="-Z"), via=ROUTE, smooth=True)
SB = ap.bbox(scr)

# === DECK ===
TRAY = [(X0, X1, Y0, Y1, 4.0), (-BAY_X, BAY_X, BAY_Y[0], BAY_Y[1], 4.0),
        # a narrower step at the bays' front: port 10's ribbon loops 1 mm
        # past y -48; the feet come to |x| 37.95 between y -52 and -50
        (-BAY_X + 1.2, BAY_X - 1.2, BAY_Y[0] - 1.5, BAY_Y[0] + 8.0, 2.5)]
HEADP = [(-HEAD_X, HEAD_X, HY0, Y0 + WALL, 4.0)]
TOP = PCB_TOP - 0.3          # the deck stops under the modules' slide paths
# 1 spine: a tube the original cover's size, open into the frame below
spine = cad.cut(box(-SPINE, SPINE, -SPINE_Y, SPINE_Y, FRAME_TOP, FLOOR_Z0 + 0.5),
                box(-SPINE + WALL, SPINE - WALL, -SPINE_Y + WALL, SPINE_Y - WALL, FRAME_TOP - 1, FLOOR_Z0 + 1))
bosses = [Part.makeCylinder(2.4, 9.0, V(x, y, FRAME_TOP)) for x, y in FRAME_SCREWS]
# 2-5 tray: floor, walls, bays, four posts under the board's corners
tray = cad.cut(plan(TRAY, FLOOR_Z0, TOP), plan(TRAY, FT, TOP + 1, grow=-WALL))
posts = [box(x - 2, x + 2, y - 2, y + 2, FT - 0.5, BU - 0.1)
         for x in (BB.XMin + 3, BB.XMax - 3) for y in (BB.YMin + 3, BB.YMax - 3)]
# 6 head: in front of the tray and lower, open at the top into the lid
head = cad.cut(plan(HEADP, HEAD_Z0, TOP), plan(HEADP, HEAD_Z0 + WALL, TOP + 1, grow=-WALL))
deck = cad.fuse_one(spine, tray, head, *(bosses + posts))
deck = cad.cut(deck, [
    # the tray's front wall gives way to the head above the floor (the
    # screen's back rib fences the board); below it, it is the head's back
    box(-HEAD_X + WALL, HEAD_X - WALL, Y0 - 1, Y0 + WALL + 0.5, FT, TOP + 1),
    # the lead slot: the spine's inside, up through the floor
    box(-SPINE + WALL, SPINE - WALL, -SPINE_Y + WALL, SPINE_Y - WALL, FLOOR_Z0 - 1, FT + 1)] +
    # the frame screws' thread-forming pilots (M2: 1.7 mm), from below
    [Part.makeCylinder(0.85, 7.0, V(x, y, FRAME_TOP - 0.5)) for x, y in FRAME_SCREWS])
# the window shows the 25.6 x 13.5 active area with room to spare; the frame
# round it is the lip the screen's face rests 0.2 mm behind
FACE_C = ((SB.XMin + SB.XMax) / 2, SB.ZMin + 19.5 / 2)
WIN = Part.Face(cad.rounded_rect_wire(36.0, 17.0, 2.0, (FACE_C[0], HY0 - 1.0, FACE_C[1]), "Y")).extrude(V(0, WALL + 2.0, 0))
deck = cad.cut(deck, WIN)
# side ribs 0.2 mm off the screen's ends (the lid's rib holds its back)
deck = cad.fuse_one(deck, *[box(x0, x1, SB.YMin + 1.0, SB.YMax + 2.0, HEAD_Z0 + WALL - 0.5, TOP)
                            for x0, x1 in ((SB.XMin - 1.8, SB.XMin - 0.2), (SB.XMax + 0.2, SB.XMax + 1.8))])

# === LID ===
LID_TOP = UB.ZMax + 0.6 + WALL
lid = cad.cut(cad.fuse_one(plan(TRAY, TOP, LID_TOP), plan(HEADP, TOP, LID_TOP)),
              [plan(TRAY, TOP - 1, LID_TOP - WALL, grow=-WALL),
               plan(HEADP, TOP - 1, LID_TOP - WALL, grow=-WALL),
               # one space: the head's inside joins the tray's
               box(-HEAD_X + WALL, HEAD_X - WALL, Y0 - 1, Y0 + WALL + 1, TOP - 1, LID_TOP - WALL), WIN])
lid = cad.socket_opening(lid, usb, margin=1.5)
# a rib down from the lid 0.2 mm behind the screen's top half
lid = cad.fuse_one(lid, box(SB.XMin + 2.0, SB.XMax - 2.0, SB.YMax + 0.2, SB.YMax + 1.8, TOP + 0.3, LID_TOP - WALL + 0.5))
lid_screws = []
for x, y in LID_SCREWS:
    lid, deck = cad.screw_through(lid, deck, (x, y, LID_TOP), size="M2", ribs=0)
    lid_screws.append(cad.screw("csk_phillips", "M2", 10, at=(x, y, LID_TOP), axis="-Z"))

# === WIRE OPENINGS: USB-C 5 mm lower, servo ports 2-6 and 10-14, SG90 leads ===
# Wire openings for the Sesame deck and lid, in the model frame (mm), shared by the
# FreeCAD model and the mesh cut of the print files. Each one straddles the seam
# (z = TOP = 82.15): part of it comes out of the lid, part out of the deck.
SEAM = 82.15
# USB-C (port 8, mouth facing +Y at y 52.62, x -5..5, z 86.59..90.09): the lid's
# opening was the mouth + 1.5 mm, z 85.09..91.59; now it reaches 5 mm lower, z 80.09,
# through the seam into the deck's back wall.
USB = (-6.5, 6.5, 52.7, 62.0, 85.09 - 5.0, 91.59)
# Servo ports 2-5 (headers face +X, mouths at x 21.73, contacts z 82.45..84.85):
# a slot through the side wall at each, 0.5 mm past the housing at each end, from
# 0.5 mm under the board (z 79.45) to 1.8 mm over the header (86.65), so the
# jumpers go straight out. Under its middle an 8 mm notch down to z 75.95, 1 mm over
# the bay floor: the SG90 leads come up the spine, run in the 5 mm gap under the
# board and leave here. 8 mm also passes an SG90's 3-pin plug (7.6 x 2.6 mm).
PORT_Y = {2: (-45.82, -30.18), 3: (-25.82, -10.18), 4: (-5.62, 10.02), 5: (14.28, 29.92)}
X_IN, X_OUT = 30.0, 45.0          # from just past the board's edge to beyond every wall
SLOT_Z = (79.45, 86.65)
LEAD_W, LEAD_Z0 = 8.0, 75.95


# v4 (2026-11-03): the same openings on the -X side, at ports 10-13 (headers face -X),
# so the leads can leave on either side. They cut the side wall only (x -38..-36): the
# lid-screw boss at (-33.3, -2.5) stands 0.5 mm inside it, behind port 12's slot, and
# port 12's lead notch sits 2 mm further back to clear it (the boss spans y -4.7..-0.3).
PORT_Y_LEFT = {10: (-45.82, -30.18), 11: (-25.82, -10.18), 12: (-5.82, 9.82), 13: (14.18, 29.82)}
X_OUT_LEFT, X_IN_LEFT = -45.0, -35.8
LEAD_SHIFT_LEFT = {12: 2.0}


# v5 (2026-11-09): ports 6 and 14, the back ports of each column (y 34.18..49.82), get the
# same slot and lead notch. There the bay ends (y 40) and the tray wall steps in to |x| 32.3,
# so each slot cuts the bay's side and back walls and the tray wall behind them, from x 30
# out. The lid-screw boss at (+-33.3, 35.5) stands free in the bay at the slot's front end;
# the slot is cut round it (2.4 mm from its axis, it is 2.2 thick), so the boss stays whole.
PORT_Y_BACK = {6: (34.18, 49.82), 14: (34.18, 49.82)}
BACK_BOSS_R = 2.4


def back_cutters():
    """[(name, box, boss keep-out (x, y, r))] for ports 6 and 14."""
    out = []
    for n, (y0, y1) in PORT_Y_BACK.items():
        sx = 1 if n == 6 else -1
        xa, xb = sorted((sx * X_IN, sx * X_OUT))
        keep = (sx * LID_SCREWS[0][0], LID_SCREWS[0][1], BACK_BOSS_R)
        out.append(("port%d" % n, (xa, xb, y0 - 0.5, y1 + 0.5) + SLOT_Z, keep))
        yc = (y0 + y1) / 2
        out.append(("sg90_%d" % n, (xa, xb, yc - LEAD_W / 2, yc + LEAD_W / 2, LEAD_Z0, SLOT_Z[0] + 0.1), keep))
    return out


def back_cutter_shapes():
    return [box(*b).cut(Part.makeCylinder(r, 40.0, V(x, y, 60.0))) for _, b, (x, y, r) in back_cutters()]


def opening_boxes():
    out = [("usb", USB)]
    for n, (y0, y1) in PORT_Y.items():
        out.append(("port%d" % n, (X_IN, X_OUT, y0 - 0.5, y1 + 0.5) + SLOT_Z))
        yc = (y0 + y1) / 2
        out.append(("sg90_%d" % n, (X_IN, X_OUT, yc - LEAD_W / 2, yc + LEAD_W / 2, LEAD_Z0, SLOT_Z[0] + 0.1)))
    for n, (y0, y1) in PORT_Y_LEFT.items():
        out.append(("port%d" % n, (X_OUT_LEFT, X_IN_LEFT, y0 - 0.5, y1 + 0.5) + SLOT_Z))
        yc = (y0 + y1) / 2 + LEAD_SHIFT_LEFT.get(n, 0.0)
        out.append(("sg90_%d" % n, (X_OUT_LEFT, X_IN_LEFT, yc - LEAD_W / 2, yc + LEAD_W / 2, LEAD_Z0, SLOT_Z[0] + 0.1)))
    return out

deck = cad.cut(deck, [box(*b) for _, b in opening_boxes()] + back_cutter_shapes())
lid = cad.cut(lid, [box(*b) for _, b in opening_boxes()] + back_cutter_shapes())

# v6 (2026-11-09): WIRE BOBBIN KEYHOLES. A wire bobbin (wire_parts.py) sits on the lid's top
# next to each servo port and holds that port's slack: both servo leads and the jumpers,
# wound round its core. Two mushroom pegs under it drop into a pair of keyholes through the
# lid's 2 mm top skin and slide 4 mm OUTWARD to lock, so the wires' pull keeps them locked.
# Ports 2-5 / 10-13 sit over the bays (the bobbin x 9.5..35.5 from the middle); ports 6 / 14
# behind them, where the lid narrows to |x| 32.3 (x 6..32). Inside |x| 38 the legs never
# rise over the lid (the measured outline), so the bobbins stay clear of them. Holes only:
# the lid still prints top-down with nothing under it.
BOBBIN_Y = {2: -38.0, 3: -18.0, 4: 2.2, 5: 22.1, 6: 42.0,
            10: -38.0, 11: -18.0, 12: 2.0, 13: 22.0, 14: 42.0}
BOBBIN_X = {"bay": (9.5, 35.5), "back": (6.0, 32.0)}     # |x| span of the bobbin
PEG_DX = 6.0                     # pegs at the bobbin's middle +- 6 (locked)
KEY_TRAVEL, KEY_ENTRY_D, KEY_SLOT_W = 4.0, 6.0, 3.4     # the peg's head 5.4, neck 3.0


def bobbin_span(n):
    return BOBBIN_X["back" if n in (6, 14) else "bay"]


def keyhole_pegs():
    """[(port, x_locked, y)] in the model frame: the pegs' necks when locked."""
    out = []
    for n, y in BOBBIN_Y.items():
        sx = 1 if n <= 6 else -1
        xc = sum(bobbin_span(n)) / 2
        out += [(n, sx * (xc + d), y) for d in (-PEG_DX, PEG_DX)]
    return out


def keyhole_shapes(z0=LID_TOP - WALL - 0.3, z1=LID_TOP + 1.0):
    out = []
    for n, x, y in keyhole_pegs():
        sx = 1 if x > 0 else -1
        xe = x - sx * KEY_TRAVEL                     # the entry: inward of the lock
        h = z1 - z0
        out.append(cad.fuse_one(Part.makeCylinder(KEY_ENTRY_D / 2, h, V(xe, y, z0)),
                                Part.makeCylinder(KEY_SLOT_W / 2, h, V(x, y, z0)),
                                box(min(x, xe), max(x, xe), y - KEY_SLOT_W / 2, y + KEY_SLOT_W / 2, z0, z1)))
    return out

lid = cad.cut(lid, keyhole_shapes())

# v6: SPINE LEAD HOLES. Eight holes, one per servo, through the spine's front and back end
# walls (y +-37.61..39.61), so each servo lead goes straight into the spine and up its
# inside to the gap under the board. The side walls can't have them: the femurs pass
# 0.2 mm outside. Front wall: the front legs' leads; back wall: the rear legs'. A leg's
# hip lead in the lower row, its knee lead in the upper; the leg's own side of the wall.
# Each hole is 9 x 4.5 mm with round ends, so a servo's 3-pin plug (7.6 x 2.6) passes
# through. |x| <= 12.5 keeps 1.4 mm off the frame-screw bosses (r 2.4 at |x| ~16); the
# top row ends 4 mm under the tray floor's underside (z 72.95).
LEAD_HOLE_W, LEAD_HOLE_H, LEAD_HOLE_X = 9.0, 4.5, 8.0
LEAD_HOLE_Z = {"hip": 59.0, "knee": 66.5}            # hole centres
SPINE_HOLES = {(leg, joint): (sx * LEAD_HOLE_X, sy, LEAD_HOLE_Z[joint])
               for leg, sx, sy in (("FL", 1, -1), ("FR", -1, -1), ("RL", 1, 1), ("RR", -1, 1))
               for joint in ("hip", "knee")}


def spine_hole_shapes():
    out = []
    r, L = LEAD_HOLE_H / 2, LEAD_HOLE_W - LEAD_HOLE_H
    for (x, sy, z) in SPINE_HOLES.values():
        y0 = sy * SPINE_Y - 3.0 if sy > 0 else -SPINE_Y - 3.0      # through the 2 mm wall, 3 mm past each side
        out.append(cad.fuse_one(box(x - L / 2, x + L / 2, y0, y0 + 6.0 + WALL, z - r, z + r),
                                *[Part.makeCylinder(r, 6.0 + WALL, V(x + d, y0, z), V(0, 1, 0)) for d in (-L / 2, L / 2)]))
    return out

deck = cad.cut(deck, spine_hole_shapes())

# v6: FRAME LEAD SLOTS. Eight slots, one per servo, up through Sesame's internal frame into
# the spine, where the frame's underside wire channels run (x +-15.5..18, recessed z
# 38.1..44.6, y -27..27). Each slot is 9 x 4 mm, a plug on edge: x 13.4 (v6.1: through the 1 mm rib to the battery bay; 14.0 and 14.3 left slivers; the battery at 13.9 leaves 3.5 mm)
# (the battery reaches |x| 13.9) to 17.4. The spine's wall stands over x 16.5..18.5, so a
# notch 1.1 deep in its inner face (z up to 58) gives the plug its last millimetre; the wall
# keeps 0.9..1.0 mm there. Front legs: y -20 and -8; rear legs: y 8 and 20 (on +x, y 20 runs
# into the frame's own battery-wire slot). With the bottom cover off, push the plug up the
# slot, then press the lead into the channel as upstream does.
FRAME_SLOT_X, FRAME_SLOT_L = (13.4, 17.4), 9.0   # v6.1: through the 1 mm rib, no sliver
FRAME_SLOT_Y = (-20.0, -8.0, 8.0, 20.0)
FRAME_SLOT_SKIP = {(1, 20.0)}   # v6.1: the frame's own battery-wire opening (x 13.5..19, y 17..26) is there
SPINE_NOTCH = (SPINE - WALL - 0.1, 17.5, FRAME_TOP - 0.1, 58.0)     # x0, x1, z0, z1


def frame_slot_boxes():
    out = []
    for sx in (1, -1):
        for y in FRAME_SLOT_Y:
            if (sx, y) in FRAME_SLOT_SKIP: continue
            xa, xb = sorted((sx * FRAME_SLOT_X[0], sx * FRAME_SLOT_X[1]))
            out.append((xa, xb, y - FRAME_SLOT_L / 2, y + FRAME_SLOT_L / 2, 30.0, FRAME_TOP + 1.0))
    return out


def spine_notch_boxes():
    x0, x1, z0, z1 = SPINE_NOTCH
    return [tuple(sorted((sx * x0, sx * x1))) + (y - FRAME_SLOT_L / 2, y + FRAME_SLOT_L / 2, z0, z1)
            for sx in (1, -1) for y in FRAME_SLOT_Y]

SHAPES["frame"] = cad.cut(SHAPES["frame"], [box(*b) for b in frame_slot_boxes()])

# v6.1 (2026-11-10): FRAME SCREW HOLES WIDER. Printed, the frame's four deck-screw holes were
# too tight for stock M2 pan-heads: the head pocket under the top plate is 5.05 mm across and
# the hole through the 1.27 mm plate 2.28. Now 6.0 and 2.6. Above z 46 the pocket is a closed
# ring with 0.9 mm or more of wall left; below, it is already open on one side.
FRAME_SCREW_POCKET_D, FRAME_SCREW_HOLE_D = 6.0, 2.6


def frame_screw_cutters():
    out = []
    for x, y in FRAME_SCREWS:
        out.append(Part.makeCylinder(FRAME_SCREW_POCKET_D / 2, FRAME_SCREW_Z - 36.0, V(x, y, 36.0)))
        out.append(Part.makeCylinder(FRAME_SCREW_HOLE_D / 2, 4.0, V(x, y, FRAME_SCREW_Z - 0.5)))
    return out

SHAPES["frame"] = cad.cut(SHAPES["frame"], frame_screw_cutters())
deck = cad.cut(deck, [box(*b) for b in spine_notch_boxes()])

# v6.1 (2026-11-10): DECK PRINT SPLIT AND SCREW JOINTS. The deck prints as part 1 (the tray
# floor and everything above, z >= FLOOR_Z0) and part 2, which is TWO pieces: the spine and
# the head (below the floor they do not meet). Until now the split lived only in the print
# STLs; here it is modelled. The walls are 2 mm, too thin for cad.split's lip (it says so), so
# the joint is the printed one: each piece's walls stand KEY_H = 0.55 mm up into a matching
# recess in part 1's underside (KEY_GAP over them; not over the head's front wall, where the
# window leaves slivers too thin to print). It was glued; now screws hold it, and every joint
# takes screws FROM BOTH SIDES.
#   The screws are the kit's (MEASURED by hand, 2026-11-10): M2 thread-forming, a 4.5 mm pan
# head about 2 mm tall, a 6 mm shank. Each goes through a CLEAR_D hole in the part it enters
# and cuts its thread in a PILOT_D pilot PILOT_DEPTH deep in the other; with the head down,
# 3.9..4.7 mm of thread bites. A head that goes INTO a part sits in a HEAD_POCKET_D pocket.
#   Deck part 1 to the spine / the head, from above: heads on part 1's floor (they stand 2 mm,
# under the board's 5 mm gap; checked against the ribbons), into columns on part 2 that stand
# on ledges fused to its walls - spine: x +-15.5 in front (the lead holes end at |x| 12.5),
# x 0 behind; head: x +-18 on the back of its rear wall (the ribbons drop at x -9 and +10).
#   From below: heads under ledges on part 2, up into columns that hang from part 1's floor -
# spine: x +-15.5 behind it; head: x +-10. Open air under each ledge, for the screwdriver.
#   The deck to the frame, from below: the four corner screws (FRAME SCREW HOLES WIDER). From
# above: two more, down through pads at the foot of the spine's end walls (x 0, between the
# lead holes) into pilots in the frame's solid ends; reach them through the floor's lead slot
# before the board goes in. |x| <= 18.1 keeps every column inside the spine's outline, where
# the femurs never come.
SPLIT_Z, KEY_H, KEY_GAP = FLOOR_Z0, 0.55, 0.05
KIT_SCREW = {"d": 2.0, "head_d": 4.5, "head_h": 2.0, "shank": 6.0}
CLEAR_D, PILOT_D, PILOT_DEPTH, HEAD_POCKET_D = 2.4, 1.7, 5.0, KIT_SCREW["head_d"] + 0.5
COL_R = 2.6                                    # a column round a pilot: 1.75 mm of wall
FT_TOP = FLOOR_Z0 + WALL                       # part 1's floor top
# (x, y, the wall face its ledge stands against: y, +1 / -1 = the side the ledge is on, ledge z)
# (front-left of the spine is from below: port 11's ribbon lies flat over the floor there)
DOWN = {"spine": [(15.5, -41.5, -SPINE_Y, -1, 62.0), (0.0, 41.5, SPINE_Y, 1, 62.0)],
        "head": [(18.0, -67.0, Y0 + WALL, 1, HEAD_Z0), (-18.0, -67.0, Y0 + WALL, 1, HEAD_Z0)]}
UP = {"spine": [(-15.5, -42.3, -SPINE_Y, -1, 66.0), (15.5, 42.3, SPINE_Y, 1, 66.0), (-15.5, 42.3, SPINE_Y, 1, 66.0)],
      "head": [(10.0, -65.5, Y0 + WALL, 1, 66.0), (-10.0, -65.5, Y0 + WALL, 1, 66.0)]}
FRAME_DOWN = ((0.0, -34.8), (0.0, 34.8))
PAD_T = 2.0


def split_deck(d):
    """(part 1, {"spine": piece, "head": piece}), the key on each piece, the recess in part 1."""
    big = box(-200, 200, -300, 300, 0, SPLIT_Z)
    lower, upper = d.common(big), d.cut(big)
    # the walls' section just under the split, raised: z SPLIT_Z - 0.1 .. SPLIT_Z + KEY_H, so
    # it overlaps its piece by 0.1; none on the head's front wall (the window's slivers)
    key = lower.common(box(-200, 200, HY0 + WALL + 0.5, 300, SPLIT_Z - KEY_H - 0.1, SPLIT_Z))
    key.translate(V(0, 0, KEY_H))
    lifted = key.copy(); lifted.translate(V(0, 0, KEY_GAP))
    pieces = {}
    for s in lower.Solids:
        name = "head" if s.BoundBox.YMax < Y0 + WALL + 0.5 else "spine"
        ks = [k for k in key.Solids if k.common(s).Volume > 1e-3]
        pieces[name] = cad.fuse_one(s, *ks)
    return cad.cut(upper, [key, lifted]), pieces


def cyl(r, x, y, z0, z1):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0))


def ledge(x, y, wy, side, z0, t=2.0):
    """A ledge round (x, y) reaching 0.1 into the wall face at y = wy."""
    y0, y1 = sorted((wy - side * 0.1, y + side * COL_R))
    return cad.fuse_one(box(x - COL_R, x + COL_R, y0, y1, z0, z0 + t), cyl(COL_R, x, y, z0, z0 + t))


deck_p1, pieces = split_deck(deck)
joint_screws, JOINT_LOG = [], []
for name in ("spine", "head"):
    p = pieces[name]
    for x, y, wy, side, lz in DOWN[name]:
        # from above: through part 1's floor into a column on a ledge on part 2
        top = SPLIT_Z - 0.1
        p = cad.fuse_one(p, ledge(x, y, wy, side, lz), cyl(COL_R, x, y, lz + 1.0, top))
        p = cad.cut(p, cyl(PILOT_D / 2, x, y, top - PILOT_DEPTH, top + 0.1))
        deck_p1 = cad.cut(deck_p1, cyl(CLEAR_D / 2, x, y, SPLIT_Z - 0.5, FT_TOP + 0.5))
        joint_screws.append(cad.screw("pan_phillips", "M2", KIT_SCREW["shank"], at=(x, y, FT_TOP), axis="-Z"))
        JOINT_LOG.append(("%s, from above" % name, x, y, FT_TOP, -1))
    for x, y, wy, side, lz in UP[name]:
        # from below: the head under a ledge on part 2, up into a column hanging from part 1
        p = cad.fuse_one(p, ledge(x, y, wy, side, lz))
        p = cad.cut(p, cyl(CLEAR_D / 2, x, y, lz - 0.5, lz + 2.5))
        bot = lz + 2.0 + 0.1
        deck_p1 = cad.fuse_one(deck_p1, cyl(COL_R, x, y, bot, SPLIT_Z + 0.5))
        deck_p1 = cad.cut(deck_p1, cyl(PILOT_D / 2, x, y, bot - 0.1, bot + PILOT_DEPTH))
        joint_screws.append(cad.screw("pan_phillips", "M2", KIT_SCREW["shank"], at=(x, y, lz), axis="+Z"))
        JOINT_LOG.append(("%s, from below" % name, x, y, lz, 1))
    pieces[name] = p
# the deck to the frame from above: pads at the foot of the spine's end walls, pilots in the frame
sp = pieces["spine"]
for x, y in FRAME_DOWN:
    side = 1 if y > 0 else -1
    wy = side * (SPINE_Y - WALL)                # the end wall's inner face
    y0, y1 = sorted((wy + side * 0.1, y - side * 3.0))
    sp = cad.fuse_one(sp, box(x - 3.0, x + 3.0, y0, y1, FRAME_TOP, FRAME_TOP + PAD_T))
    sp = cad.cut(sp, cyl(CLEAR_D / 2, x, y, FRAME_TOP - 0.5, FRAME_TOP + PAD_T + 0.5))
    SHAPES["frame"] = cad.cut(SHAPES["frame"], cyl(PILOT_D / 2, x, y, FRAME_TOP - PILOT_DEPTH, FRAME_TOP + 0.1))
    joint_screws.append(cad.screw("pan_phillips", "M2", KIT_SCREW["shank"], at=(x, y, FRAME_TOP + PAD_T), axis="-Z"))
    JOINT_LOG.append(("frame, from above", x, y, FRAME_TOP + PAD_T, -1))
pieces["spine"] = sp
deck_p2 = Part.makeCompound([pieces["spine"], pieces["head"]])
deck = cad.fuse_one(deck_p1, pieces["spine"], pieces["head"])   # the whole deck, for the checks

# === SCREWS (upstream's, where upstream puts them) ===
screws = [cad.screw("pan_phillips", "M2", 8, at=(x, y, FRAME_SCREW_Z), axis="+Z") for x, y in FRAME_SCREWS]
screws += [cad.screw("pan_phillips", "M2", 8, at=(x, y, BOTTOM_SCREW_Z), axis="+Z") for x, y in BOTTOM_SCREWS]
screws += joint_screws

# === OBJECTS ===
for n in UPSTREAM:
    o = doc.addObject("Part::Feature", n)
    o.Shape = SHAPES[n]
    o.ViewObject.ShapeColor = cad.color(COLOURS[n.split("_")[0]])
for name, shape in (("Deck_part1", deck_p1), ("Deck_spine", pieces["spine"]), ("Deck_head", pieces["head"]),
                    ("Lid", lid)):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shape
    o.ViewObject.ShapeColor = cad.color(COLOURS[name.split("_")[0]])
for i, s in enumerate(screws + lid_screws):
    o = doc.addObject("Part::Feature", "Screw_%d" % (i + 1))
    o.Shape = s
    o.ViewObject.ShapeColor = cad.color(COLOURS["Screw"])

# upstream fits: each servo horn is pressed into its femur, and each knee
# servo sits in its femur's pocket (the leg shell slides over the motor)
INTENDED_OVERLAPS = [("femur_" + f, "servo_%s_%s" % (j, s)) for j in ("hip", "knee")
                     for f, s in (("L1", "FL"), ("L2", "RL"), ("R1", "FR"), ("R2", "RR"))]

# "imported": Sesame's own parts, printed as upstream made them - ./check
# judges their fit, not their walls
INTENT = {"board": "flat", "fitted_after": ["Lid"],
          "imported": ["frame", "bottom_cover", "battery", "femur_L1", "femur_L2", "femur_R1", "femur_R2",
                       "foot_L3", "foot_L4", "foot_R3", "foot_R4", "servo_hip_FL", "servo_hip_FR",
                       "servo_hip_RL", "servo_hip_RR", "servo_knee_FL", "servo_knee_FR",
                       "servo_knee_RL", "servo_knee_RR"]}
