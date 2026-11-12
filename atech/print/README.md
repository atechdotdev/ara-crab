# 3D Printing Guide

Atech-crab is 14 printed parts: Sesame's bottom cover and eight leg parts, unchanged, Sesame's internal frame with
eight lead slots added, plus a new **deck** (three parts that snap together) and **lid** that hold the Atech board. Print everything in **PLA**.

> [!NOTE]
> **Not printed yet.** The deck and lid pass Atech Atelier's fit check in CAD, but nobody has printed and
> assembled them. Print one set and test-fit the deck on the frame, with the servos in, before you print more.

## Bambu Lab printers: ready to print

Each file in [`gcode/`](gcode/) is sliced and checked. Open it in Bambu Studio or Bambu Handy and send it.

| Printer | Plates | File(s) | Time | PLA |
| ------- | ------ | ------- | ---- | --- |
| H2S | 1 | [`atech_crab_pla_h2s.gcode.3mf`](gcode/atech_crab_pla_h2s.gcode.3mf) | 4 h 52 min | 137 g |
| H2D | 1 | [`atech_crab_pla_h2d.gcode.3mf`](gcode/atech_crab_pla_h2d.gcode.3mf) | 5 h 03 min | 137 g |
| H2D Pro | 1 | [`atech_crab_pla_h2dp.gcode.3mf`](gcode/atech_crab_pla_h2dp.gcode.3mf) | 5 h 03 min | 137 g |
| H2C | 1 | [`atech_crab_pla_h2c.gcode.3mf`](gcode/atech_crab_pla_h2c.gcode.3mf) | 5 h 03 min | 138 g |
| X2D | 2 | [`plate 1`](gcode/atech_crab_pla_x2d_plate1.gcode.3mf) + [`plate 2`](gcode/atech_crab_pla_x2d_plate2.gcode.3mf) | 3 h 46 min + 1 h 12 min | 106 g + 30 g |
| P2S | 2 | [`plate 1`](gcode/atech_crab_pla_p2s_plate1.gcode.3mf) + [`plate 2`](gcode/atech_crab_pla_p2s_plate2.gcode.3mf) | 4 h 10 min + 52 min | 117 g + 20 g |
| P1S | 2 | [`plate 1`](gcode/atech_crab_pla_p1s_plate1.gcode.3mf) + [`plate 2`](gcode/atech_crab_pla_p1s_plate2.gcode.3mf) | 3 h 23 min + 1 h 35 min | 98 g + 39 g |
| X1 Carbon | 2 | [`plate 1`](gcode/atech_crab_pla_x1c_plate1.gcode.3mf) + [`plate 2`](gcode/atech_crab_pla_x1c_plate2.gcode.3mf) | 3 h 24 min + 1 h 36 min | 98 g + 39 g |
| X1 | 2 | [`plate 1`](gcode/atech_crab_pla_x1_plate1.gcode.3mf) + [`plate 2`](gcode/atech_crab_pla_x1_plate2.gcode.3mf) | 3 h 25 min + 1 h 38 min | 98 g + 39 g |
| X1E | 2 | [`plate 1`](gcode/atech_crab_pla_x1e_plate1.gcode.3mf) + [`plate 2`](gcode/atech_crab_pla_x1e_plate2.gcode.3mf) | 3 h 25 min + 1 h 36 min | 98 g + 39 g |
| A2L | 1 | [`atech_crab_pla_a2l.gcode.3mf`](gcode/atech_crab_pla_a2l.gcode.3mf) | 5 h 45 min | 137 g |
| A1 | 2 | [`plate 1`](gcode/atech_crab_pla_a1_plate1.gcode.3mf) + [`plate 2`](gcode/atech_crab_pla_a1_plate2.gcode.3mf) | 4 h 37 min + 1 h 01 min | 117 g + 20 g |
| A1 mini | 3 | [`plate 1`](gcode/atech_crab_pla_a1m_plate1.gcode.3mf) + [`plate 2`](gcode/atech_crab_pla_a1m_plate2.gcode.3mf) + [`plate 3`](gcode/atech_crab_pla_a1m_plate3.gcode.3mf) | 1 h 46 min + 2 h 18 min + 1 h 36 min | 49 g + 53 g + 34 g |

**Everything at once** (the 13 parts plus the 16 wire parts):

| Printer | Plates | File(s) | Time | PLA |
| ------- | ------ | ------- | ---- | --- |
| H2S | 1 | [`atech_crab_everything_pla_h2s.gcode.3mf`](gcode/atech_crab_everything_pla_h2s.gcode.3mf) | 6 h 03 min | 162 g |
| H2D | 1 | [`atech_crab_everything_pla_h2d.gcode.3mf`](gcode/atech_crab_everything_pla_h2d.gcode.3mf) | 6 h 16 min | 162 g |
| H2D Pro | 1 | [`atech_crab_everything_pla_h2dp.gcode.3mf`](gcode/atech_crab_everything_pla_h2dp.gcode.3mf) | 6 h 16 min | 162 g |
| H2C | 1 | [`atech_crab_everything_pla_h2c.gcode.3mf`](gcode/atech_crab_everything_pla_h2c.gcode.3mf) | 6 h 16 min | 164 g |
| X2D | 2 | [`plate 1`](gcode/atech_crab_everything_pla_x2d_plate1.gcode.3mf) + [`plate 2`](gcode/atech_crab_everything_pla_x2d_plate2.gcode.3mf) | 3 h 51 min + 2 h 18 min | 108 g + 53 g |
| P2S | 2 | [`plate 1`](gcode/atech_crab_everything_pla_p2s_plate1.gcode.3mf) + [`plate 2`](gcode/atech_crab_everything_pla_p2s_plate2.gcode.3mf) | 4 h 21 min + 1 h 55 min | 120 g + 42 g |
| P1S | 2 | [`plate 1`](gcode/atech_crab_everything_pla_p1s_plate1.gcode.3mf) + [`plate 2`](gcode/atech_crab_everything_pla_p1s_plate2.gcode.3mf) | 3 h 42 min + 2 h 30 min | 105 g + 57 g |
| X1 Carbon | 2 | [`plate 1`](gcode/atech_crab_everything_pla_x1c_plate1.gcode.3mf) + [`plate 2`](gcode/atech_crab_everything_pla_x1c_plate2.gcode.3mf) | 3 h 43 min + 2 h 31 min | 105 g + 58 g |
| X1 | 2 | [`plate 1`](gcode/atech_crab_everything_pla_x1_plate1.gcode.3mf) + [`plate 2`](gcode/atech_crab_everything_pla_x1_plate2.gcode.3mf) | 3 h 43 min + 2 h 32 min | 105 g + 58 g |
| X1E | 2 | [`plate 1`](gcode/atech_crab_everything_pla_x1e_plate1.gcode.3mf) + [`plate 2`](gcode/atech_crab_everything_pla_x1e_plate2.gcode.3mf) | 3 h 43 min + 2 h 31 min | 105 g + 58 g |
| A2L | 1 | [`atech_crab_everything_pla_a2l.gcode.3mf`](gcode/atech_crab_everything_pla_a2l.gcode.3mf) | 7 h 11 min | 162 g |
| A1 | 2 | [`plate 1`](gcode/atech_crab_everything_pla_a1_plate1.gcode.3mf) + [`plate 2`](gcode/atech_crab_everything_pla_a1_plate2.gcode.3mf) | 4 h 49 min + 2 h 10 min | 120 g + 42 g |
| A1 mini | 3 | [`plate 1`](gcode/atech_crab_everything_pla_a1m_plate1.gcode.3mf) + [`plate 2`](gcode/atech_crab_everything_pla_a1m_plate2.gcode.3mf) + [`plate 3`](gcode/atech_crab_everything_pla_a1m_plate3.gcode.3mf) | 2 h 31 min + 2 h 24 min + 2 h 04 min | 63 g + 55 g + 44 g |

- **H2S, H2D, H2D Pro, H2C, A2L:** one plate holds everything. The H2D file uses one nozzle (Bambu Studio's nozzle 1); the printer
  shows which before it starts.
- **256 mm beds (X2D, P2S, P1S, X1, A1):** two plates. **A1 mini** (180 mm): three. Print every plate file.
- **P1P:** Bambu Studio has no PLA Basic profile for it, so there is no file: slice the STLs below.
- All files: Bambu PLA Basic, **Textured PEI plate**, 0.4 mm nozzle.

<img src="../docs/img/print/plate_h2s.png" alt="All 13 parts on the H2S plate" width="45%">

Each file carries the printer's own Bambu start G-code (`check.py` compares it with Bambu Studio's profile for
that printer), its first layer is at 0.2 mm, and every part lays plastic on it. **Watch the first layer anyway:**
it should go down on the plate with every part and its brim. If the nozzle draws in the air, stop the print.

## Other printers: slice the STLs

All 14 STLs are in [`stl/`](stl/), already the right way up: load them and don't rotate them.

### Recommended settings

* **Material:** PLA / PLA+
* **Layer height:** 0.20 mm, 0.4 mm nozzle
* **Wall loops:** 2
* **Infill:** 15 %, gyroid
* **Supports:** tree, **from the build plate only**, threshold 40°, so nothing grows inside the servo pockets
* **Brim:** auto

These are the settings of the Bambu files above. Sesame's own guide
([`hardware/printing`](../../hardware/printing/README.md)) prints its parts at 8–10 % honeycomb infill with no
supports; either works for Sesame's parts.

### Parts

| Part | From | Qty | STL | Print orientation |
| ---- | ---- | --- | --- | ----------------- |
| Joint R1, R2, R3, R4 | Sesame | 1 each | [R1](stl/R1-v117.stl) · [R2](stl/R2-v117.stl) · [R3](stl/R3-v117.stl) · [R4](stl/R4-v117.stl) | as in the STL |
| Joint L1, L2, L3, L4 | Sesame | 1 each | [L1](stl/L1-v117.stl) · [L2](stl/L2-v117.stl) · [L3](stl/L3-v117.stl) · [L4](stl/L4-v117.stl) | as in the STL |
| Internal frame, with lead slots | Sesame, modified | 1 | [Internal-Frame-v121-wired.stl](stl/Internal-Frame-v121-wired.stl) | as in the STL |
| Bottom cover | Sesame | 1 | [Bottom-Cover-v121.stl](stl/Bottom-Cover-v121.stl) | as in the STL |
| Deck part 1 (plate) | Atech-crab | 1 | [deck_part1_plate.stl](stl/deck_part1_plate.stl) | floor down, walls up |
| Deck part 2a (spine) | Atech-crab | 1 | [deck_part2a_spine.stl](stl/deck_part2a_spine.stl) | upright, snap hooks up |
| Deck part 2b (head) | Atech-crab | 1 | [deck_part2b_head.stl](stl/deck_part2b_head.stl) | upright, snap hooks up |
| Lid | Atech-crab | 1 | [lid_print_upside_down.stl](stl/lid_print_upside_down.stl) | **upside down**: the top on the plate |

Sesame's parts are the same meshes as [`hardware/printing/stl`](../../hardware/printing/stl/), laid flat at the
origin, except the internal frame, which has the v6 lead slots cut into it. Sesame's **top cover is not printed**: the deck and lid replace it.

**Re-slice for a Bambu printer** (macOS, Bambu Studio installed): `python slice.py out_dir [h2s h2d x2d p2s]`
(`--parts stl_all --name atech_crab_everything` for everything; `stl_all/` links to `stl/` and `stl_wires/`).
It uses Bambu Studio's own printer profiles, so the start G-code is the printer's own.
**Check a sliced file:** `python check.py file.gcode.3mf ...`

## The wire openings (v5)

The deck and lid have an opening at every side port, **on both sides**: ports 2–6 on the right (+X) and ports
10–14 on the left (−X). Each opening is half in the lid and half in the deck:

- **A slot** at each port, 16.6 × 7.2 mm, so the jumpers go straight out of the header.
- **An 8 mm notch** under each slot, down to the gap under the board: the servo leads come up the spine, run under
  the board and leave here. An MG90S plug (the same 3-pin plug as an SG90, 7.6 × 2.6 mm) fits through.
- **USB-C** (port 8, at the back): the opening reaches 5 mm lower, through the seam.

On the left side a lid-screw post stands just inside the wall behind port 12's slot, so port 12's notch sits 2 mm
further back than the others.

Ports 6 and 14 are the back ports, where the side bays end and the wall steps in. Their slots cut through the
end of the bay and the wall behind it. A lid-screw post stands in each bay at the front end of these slots. The
slots go round it and leave it whole. On port 6 the post is in front of pins 1–2 (+12 V, 5 V), which take no
jumpers. On port 14 it is in front of pins 6 and 5 (line B, and half of line A), so the jumper housings there cannot go
straight out: use port 14 only for a cable that bends round the post.

| Left (ports 10–13) | Right (ports 2–5) |
| --- | --- |
| <img src="../docs/img/print/openings_left.jpg" alt="Wire openings on the left side"> | <img src="../docs/img/print/openings_right.jpg" alt="Wire openings on the right side"> |

The openings are open at the seam, so neither the deck nor the lid needs support for them.

## Servo lead holes and bobbin keyholes (v6)

- **8 lead holes in the spine**, one per servo, 9 × 4.5 mm with round ends, so a servo's plug passes through.
  They are in the spine's front and back walls: the side walls can't have them, because the femurs pass 0.2 mm
  outside. Front wall: the front legs' leads. Back wall: the rear legs' leads. On each leg's own side of the wall,
  the hip lead goes in the lower hole and the knee lead in the upper one. Inside, the lead goes up the spine to the
  gap under the board and out through its port's notch.
- **8 lead slots through the internal frame**, one per servo, 9 × 3.4 mm, up from the frame's underside wire
  channels into the spine (two per leg, at y ±8 and ±20 along each channel). With the bottom cover off, push the
  plug up its slot, then press the lead into the channel as Sesame's guide does. The spine wall over each slot
  has a 1.1 mm notch on its inside, so the plug gets past it. Use either these slots or the spine's end-wall holes.
- **20 keyholes in the lid's top**, two at each port (2–6 and 10–14), for the wire bobbins below. They are holes
  only, so the lid still prints top-down without supports.

## Wire parts: jumper holders, plug sleeves and bobbins

Small parts that keep the servo wiring in order. [`gcode/atech_crab_wires_pla_p2s.gcode.3mf`](gcode/atech_crab_wires_pla_p2s.gcode.3mf)
has all of them on one P2S plate (PLA Basic, Textured PEI, 1 h 22 min, 25 g); the STLs are in
[`stl_wires/`](stl_wires/), made by [`../cad/wire_parts.py`](../cad/wire_parts.py).

- **Port jumper holder (×4, ports 2–5).** Push the three jumpers of a port (GND, line A, line B) into
  its channel, then plug the holder into the port as one piece. The solid half covers pins 1–3
  (+12 V, 5 V, 3.3 V), toward the front of the robot, so no jumper can reach them. Its tongue sits
  in the deck's port slot and the lid holds it there. Upside down it does not go in. The same part,
  turned round, fits ports 10–13.
- **Servo plug sleeve (×8).** Thread it onto the jumpers, plug them into the servo's plug, then slide
  the sleeve over the joint so it cannot pull apart.
- **Wire bobbin (×4, one per leg).** It holds a port's slack on the lid: both servo leads and the port's
  jumpers, wound round its core (20 × 7 mm, 9 mm high). Pinch each end in a slit in the top flange.
  Drop its two pegs into the port's keyholes and slide it 4 mm outward, toward the port: the wires' pull keeps
  it locked. To take it off, slide it inward and lift. Prints upside down (top flange on the plate, pegs up),
  without supports. At port 12 (and nearly at port 6) the bobbin covers a lid screw: take the bobbin off first.

Checked in CAD against the deck, lid and Sesame's parts. **Not yet printed or test-fitted**: print
one holder first and try it in a port before printing the rest.

## After printing

1. Remove the brims and the tree supports.
2. **Snap the deck together, then screw it.** Set deck part 1 (the plate) floor-down over the spine and the head
   and press it down: six hooks click over the edge of the floor opening (four on the spine, two on the head behind
   the screen). That is enough to try it. For strength add 4 screws from above through the plate's floor: front
   right and back of the spine, left and right behind the head. The 0.55 mm keys fit the recesses under the plate, so
   it only goes one way. To take it apart, take the screws out and push each hook inward from above.
3. **Deck to frame:** the 4 corner screws go up from under the frame (head pocket 6.0 mm). Two more can go down
   from above: through the pads at the foot of the spine's front and back walls (reach them through the opening
   in the floor, before the board goes in).
3. Continue with the [assembly guide (PDF, v6.3)](../docs/atech_crab_v6.3_assembly.pdf).

**Screws: one kind for the whole body,** the kit's **M2 × 6 mm pan-head self-tapping** (4.5 mm head): 4 + 2
deck to frame, 4 deck plate to spine and head, 3 lid (their heads sink flush in the lid), 2 bottom cover, and
Sesame's legs and motor mounts. The only other kind: **M2.5 × 5 mm machine screws**, 8, for the servo horns
(they thread into the servos' metal shafts).

## Versions

| Version | Date | Changed |
| ------- | ---- | ------- |
| v6.3 | 2026-11-10 | One screw for the whole body (M2 × 6 pan-head): the lid's 3 countersunk M2 × 10 became pan-heads in flush pockets. Deck: the snaps plus 4 screws from above, into columns standing on the spine and the head. Hooks thinner (1.0 % / 1.3 % strain): printed upright, they bend across the layers. |
| v6.2 | 2026-11-10 | Deck: part 1 snaps onto part 2 with six hooks (no screws, no glue). Part 2 is now two files, the spine and the head, each printed upright with its hooks up. |
| v6.1 | 2026-11-10 | Frame: the four deck-screw holes wider (head pocket 5.05 → 6.0 mm, through-hole 2.28 → 2.6 mm) for the kit's screws; two pilots for screws from above; lead slots through the rib (no sliver). Deck: the part 1 / part 2 split modelled in Atech Atelier, joined by the kit's M2 screws from both sides (11 in all, each with 4 mm of thread), instead of glue. Made from the model by `export_print.py`. |
| v6 | 2026-11-09 | 8 lead slots through the internal frame; 8 servo-lead holes and 8 slot notches in the spine (deck part 2); 20 keyholes in the lid for the wire bobbins. |
| v5 | 2026-11-09 | Slots and lead notches at the back ports 6 and 14 as well, cut round the lid-screw posts. Deck part 1 and the lid only. |
| v4 | 2026-11-03 | Slots and lead notches on the left side too (ports 10–13). Deck part 1 and the lid only. |
| v3 | 2026-11-02 | Wire openings on the right side (ports 2–5), USB-C opening 5 mm lower. |

The CAD is [`../cad/sesame_atech_wired.py`](../cad/sesame_atech_wired.py) (Atech Atelier, FreeCAD). The v4
left-side openings were cut into the v3 print STLs with
[`../cad/cut_openings_left.py`](../cad/cut_openings_left.py), using the same boxes as the CAD, and the v5 openings at ports 6 and 14 into the v4 STLs with
[`../cad/cut_openings_back.py`](../cad/cut_openings_back.py). The v6 holes were cut into the v5 STLs with
[`../cad/cut_wire_holes.py`](../cad/cut_wire_holes.py). From v6.1 the deck, the lid and the frame are exported straight from the model by
[`../cad/export_print.py`](../cad/export_print.py), which also checks every joint screw's thread.
