import os
import importlib.util
import FreeCAD as App
import Part

_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
_CONFIG_PATH = os.path.join(_PROJECT_DIR, "config.py")
spec = importlib.util.spec_from_file_location("_asrock_lid_config", _CONFIG_PATH)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)
for _name in dir(config):
    if _name.isupper():
        globals()[_name] = getattr(config, _name)

# Lid + all four side walls is ONE printable part.
LID_TOP_THICKNESS = 4.0
SIDE_WALL_HEIGHT = 58.0
FAN_OPENING_DIAMETER = 140.0
FAN_MOUNT_HOLE_SPACING = 124.5
FAN_MOUNT_HOLE_DIAMETER = 4.5
LID_CLEARANCE = 0.30
ROD_HEAD_DIAMETER = 9.0
ROD_HEAD_DEPTH = 4.0


def _cut_rod_passages(shape):
    # The four rods line up with the four holes/feet in the bottom.
    for x in (ROD_HOLE_X, BASE_X - ROD_HOLE_X):
        for y in (ROD_HOLE_Y, BASE_Y - ROD_HOLE_Y):
            hole = Part.makeCylinder(
                ROD_HOLE_DIAMETER / 2.0 + LID_CLEARANCE,
                LID_TOP_THICKNESS + SIDE_WALL_HEIGHT + 2.0,
                App.Vector(x, y, -1.0),
            )
            shape = shape.cut(hole)
    return shape


def _cut_fan_opening(shape):
    # Upper 140 mm intake opening, centred on the lid.
    cx = BASE_X / 2.0
    cy = BASE_Y / 2.0
    opening = Part.makeCylinder(
        FAN_OPENING_DIAMETER / 2.0,
        LID_TOP_THICKNESS + 2.0,
        App.Vector(cx, cy, SIDE_WALL_HEIGHT - 1.0),
    )
    return shape.cut(opening)


def _cut_fan_mount_holes(shape):
    cx = BASE_X / 2.0
    cy = BASE_Y / 2.0
    d = FAN_MOUNT_HOLE_SPACING / 2.0
    for x in (cx - d, cx + d):
        for y in (cy - d, cy + d):
            hole = Part.makeCylinder(
                FAN_MOUNT_HOLE_DIAMETER / 2.0,
                LID_TOP_THICKNESS + 2.0,
                App.Vector(x, y, SIDE_WALL_HEIGHT - 1.0),
            )
            shape = shape.cut(hole)
    return shape


def _cut_side_ventilation(shape):
    # Large open exhaust areas on all four walls. The exact final vent
    # pattern can be refined after the first physical fit check.
    wall = WALL_THICKNESS
    z0 = 18.0
    height = 30.0
    margin = 22.0
    width = BASE_X - 2.0 * margin

    front = Part.makeBox(width, wall + 2.0, height,
                         App.Vector(margin, -1.0, z0))
    rear = Part.makeBox(width, wall + 2.0, height,
                        App.Vector(margin, BASE_Y - wall - 1.0, z0))
    left = Part.makeBox(wall + 2.0, width, height,
                        App.Vector(-1.0, margin, z0))
    right = Part.makeBox(wall + 2.0, width, height,
                         App.Vector(BASE_X - wall - 1.0, margin, z0))
    for cut in (front, rear, left, right):
        shape = shape.cut(cut)
    return shape


def _add_wall_ribs(shape):
    # Narrow corner ribs retain the one-piece shell's stiffness around the
    # large exhaust openings.
    rib = 6.0
    for x in (0.0, BASE_X - rib):
        for y in (0.0, BASE_Y - rib):
            block = Part.makeBox(rib, rib, SIDE_WALL_HEIGHT,
                                 App.Vector(x, y, 0.0))
            shape = shape.fuse(block)
    return shape


def _add_bottom_guide_tongues(shape):
    # Tongues project below each side wall and fit between the bottom's guide
    # rails. They are integral with the lid/side-wall part.
    tongue_depth = 8.0
    tongue_width = WALL_THICKNESS
    z = -tongue_depth
    for x in (GUIDE_EDGE + GUIDE_RAIL_WIDTH + WALL_CLEARANCE,
              BASE_X - GUIDE_EDGE - GUIDE_RAIL_WIDTH - WALL_CLEARANCE - tongue_width):
        tongue = Part.makeBox(tongue_width,
                              BASE_Y - 2.0 * GUIDE_EDGE,
                              tongue_depth,
                              App.Vector(x, GUIDE_EDGE, z))
        shape = shape.fuse(tongue)
    for y in (GUIDE_EDGE + GUIDE_RAIL_WIDTH + WALL_CLEARANCE,
              BASE_Y - GUIDE_EDGE - GUIDE_RAIL_WIDTH - WALL_CLEARANCE - tongue_width):
        tongue = Part.makeBox(BASE_X - 2.0 * GUIDE_EDGE,
                              tongue_width,
                              tongue_depth,
                              App.Vector(GUIDE_EDGE, y, z))
        shape = shape.fuse(tongue)
    return shape


def make_lid():
    # Top plate sits at SIDE_WALL_HEIGHT and all four walls descend to z=0.
    top = Part.makeBox(BASE_X, BASE_Y, LID_TOP_THICKNESS,
                       App.Vector(0, 0, SIDE_WALL_HEIGHT))

    front = Part.makeBox(BASE_X, WALL_THICKNESS, SIDE_WALL_HEIGHT,
                         App.Vector(0, 0, 0))
    rear = Part.makeBox(BASE_X, WALL_THICKNESS, SIDE_WALL_HEIGHT,
                        App.Vector(0, BASE_Y - WALL_THICKNESS, 0))
    left = Part.makeBox(WALL_THICKNESS, BASE_Y - 2 * WALL_THICKNESS,
                        SIDE_WALL_HEIGHT,
                        App.Vector(0, WALL_THICKNESS, 0))
    right = Part.makeBox(WALL_THICKNESS, BASE_Y - 2 * WALL_THICKNESS,
                         SIDE_WALL_HEIGHT,
                         App.Vector(BASE_X - WALL_THICKNESS, WALL_THICKNESS, 0))

    shape = top.fuse(front).fuse(rear).fuse(left).fuse(right)
    shape = _cut_fan_opening(shape)
    shape = _cut_fan_mount_holes(shape)
    shape = _cut_rod_passages(shape)
    shape = _cut_side_ventilation(shape)
    shape = _add_wall_ribs(shape)
    shape = _add_bottom_guide_tongues(shape)
    return shape.removeSplitter()


def create_document():
    doc = App.newDocument("ASROCK_4x4_Lid")
    obj = doc.addObject("PartDesign::Feature", "Lid")
    obj.Label = "ASROCK 4x4 - Lid + Side Walls (one piece)"
    obj.Shape = make_lid()
    doc.recompute()
    return doc, obj


if __name__ == "__main__":
    create_document()
