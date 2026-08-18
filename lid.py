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

# The lid and all four side walls are ONE printable part.
LID_TOP_THICKNESS = 4.0
SIDE_WALL_HEIGHT = 58.0
FAN_OPENING_DIAMETER = 140.0
FAN_MOUNT_HOLE_SPACING = 124.5
FAN_MOUNT_HOLE_DIAMETER = 4.5
LID_CLEARANCE = 0.30
ROD_PASSAGE_DIAMETER = ROD_HOLE_DIAMETER + 0.8

# The bottom plate top is z=10. The lid is seated on the bottom guide
# system, so its walls start at z=10 and its top is at z=68.
LID_Z0 = BASE_THICKNESS
LID_TOP_Z = LID_Z0 + SIDE_WALL_HEIGHT


def _cut_rod_passages(shape):
    """Clearance holes through the lid for the four threaded rods."""
    for x in (ROD_HOLE_X, BASE_X - ROD_HOLE_X):
        for y in (ROD_HOLE_Y, BASE_Y - ROD_HOLE_Y):
            hole = Part.makeCylinder(
                ROD_PASSAGE_DIAMETER / 2.0,
                LID_TOP_THICKNESS + 2.0,
                App.Vector(x, y, LID_TOP_Z - 1.0),
            )
            shape = shape.cut(hole)
    return shape


def _cut_fan_opening(shape):
    cx = BASE_X / 2.0
    cy = BASE_Y / 2.0
    opening = Part.makeCylinder(
        FAN_OPENING_DIAMETER / 2.0,
        LID_TOP_THICKNESS + 2.0,
        App.Vector(cx, cy, LID_TOP_Z - 1.0),
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
                App.Vector(x, y, LID_TOP_Z - 1.0),
            )
            shape = shape.cut(hole)
    return shape


def _cut_side_ventilation(shape):
    """Large side openings; corners remain as structural posts."""
    wall = WALL_THICKNESS
    z0 = LID_Z0 + 8.0
    height = SIDE_WALL_HEIGHT - 16.0
    margin = 22.0
    width = BASE_X - 2.0 * margin

    cuts = [
        Part.makeBox(width, wall + 2.0, height,
                     App.Vector(margin, -1.0, z0)),
        Part.makeBox(width, wall + 2.0, height,
                     App.Vector(margin, BASE_Y - wall - 1.0, z0)),
        Part.makeBox(wall + 2.0, width, height,
                     App.Vector(-1.0, margin, z0)),
        Part.makeBox(wall + 2.0, width, height,
                     App.Vector(BASE_X - wall - 1.0, margin, z0)),
    ]
    for cut in cuts:
        shape = shape.cut(cut)
    return shape


def _add_corner_posts(shape):
    # Full-height corner posts reinforce the one-piece shell.
    rib = 8.0
    for x in (0.0, BASE_X - rib):
        for y in (0.0, BASE_Y - rib):
            block = Part.makeBox(rib, rib, SIDE_WALL_HEIGHT,
                                 App.Vector(x, y, LID_Z0))
            shape = shape.fuse(block)
    return shape


def _add_guide_tongues(shape):
    """Four short integral tongues sit in the bottom guide channels."""
    # The bottom guide rails begin at z=BASE_THICKNESS and are 12 mm high.
    # These tongues occupy the matching channel from the seating plane up.
    tongue_h = min(GUIDE_HEIGHT - 1.0, 10.0)
    tongue_w = WALL_THICKNESS
    z = LID_Z0

    x_positions = (
        GUIDE_EDGE + GUIDE_RAIL_WIDTH + WALL_CLEARANCE,
        BASE_X - GUIDE_EDGE - GUIDE_RAIL_WIDTH - WALL_CLEARANCE - tongue_w,
    )
    y_positions = (
        GUIDE_EDGE + GUIDE_RAIL_WIDTH + WALL_CLEARANCE,
        BASE_Y - GUIDE_EDGE - GUIDE_RAIL_WIDTH - WALL_CLEARANCE - tongue_w,
    )

    for x in x_positions:
        tongue = Part.makeBox(
            tongue_w, BASE_Y - 2.0 * GUIDE_EDGE, tongue_h,
            App.Vector(x, GUIDE_EDGE, z),
        )
        shape = shape.fuse(tongue)

    for y in y_positions:
        tongue = Part.makeBox(
            BASE_X - 2.0 * GUIDE_EDGE, tongue_w, tongue_h,
            App.Vector(GUIDE_EDGE, y, z),
        )
        shape = shape.fuse(tongue)
    return shape


def make_lid():
    # Top plate and all four walls are fused into one printable shell.
    top = Part.makeBox(BASE_X, BASE_Y, LID_TOP_THICKNESS,
                       App.Vector(0, 0, LID_TOP_Z))

    front = Part.makeBox(BASE_X, WALL_THICKNESS, SIDE_WALL_HEIGHT,
                         App.Vector(0, 0, LID_Z0))
    rear = Part.makeBox(BASE_X, WALL_THICKNESS, SIDE_WALL_HEIGHT,
                        App.Vector(0, BASE_Y - WALL_THICKNESS, LID_Z0))
    left = Part.makeBox(WALL_THICKNESS, BASE_Y - 2 * WALL_THICKNESS,
                        SIDE_WALL_HEIGHT,
                        App.Vector(0, WALL_THICKNESS, LID_Z0))
    right = Part.makeBox(WALL_THICKNESS, BASE_Y - 2 * WALL_THICKNESS,
                         SIDE_WALL_HEIGHT,
                         App.Vector(BASE_X - WALL_THICKNESS,
                                    WALL_THICKNESS, LID_Z0))

    shape = top.fuse(front).fuse(rear).fuse(left).fuse(right)
    shape = _cut_fan_opening(shape)
    shape = _cut_fan_mount_holes(shape)
    shape = _cut_rod_passages(shape)
    shape = _cut_side_ventilation(shape)
    shape = _add_corner_posts(shape)
    shape = _add_guide_tongues(shape)
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
