import os
import importlib.util
import FreeCAD as App
import Part

# Load the project's config.py explicitly from the same directory.
# This avoids FreeCAD's Python module cache using an older config.py.
_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
_CONFIG_PATH = os.path.join(_PROJECT_DIR, "config.py")
_CONFIG_NAME = "_asrock_case_config"

spec = importlib.util.spec_from_file_location(_CONFIG_NAME, _CONFIG_PATH)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

BASE_X = config.BASE_X
BASE_Y = config.BASE_Y
BASE_THICKNESS = config.BASE_THICKNESS
FOOT_HEIGHT = config.FOOT_HEIGHT
FOOT_DIAMETER = config.FOOT_DIAMETER
FOOT_INSET = config.FOOT_INSET
ROD_HOLE_DIAMETER = config.ROD_HOLE_DIAMETER
ROD_HOLE_X = config.ROD_HOLE_X
ROD_HOLE_Y = config.ROD_HOLE_Y
LATTICE_X = config.LATTICE_X
LATTICE_Y = config.LATTICE_Y
LATTICE_SLOT_WIDTH = config.LATTICE_SLOT_WIDTH
LATTICE_RIB_WIDTH = config.LATTICE_RIB_WIDTH
LATTICE_EDGE = config.LATTICE_EDGE
WALL_THICKNESS = config.WALL_THICKNESS
WALL_CLEARANCE = config.WALL_CLEARANCE
GUIDE_RAIL_WIDTH = config.GUIDE_RAIL_WIDTH
GUIDE_HEIGHT = config.GUIDE_HEIGHT
GUIDE_EDGE = config.GUIDE_EDGE
CORNER_POST_SIZE = config.CORNER_POST_SIZE


def _cut_lamella_slots(shape):
    """Cut parallel ventilation slots through the central 150 x 150 field."""
    pitch = LATTICE_SLOT_WIDTH + LATTICE_RIB_WIDTH
    count = int((LATTICE_X + LATTICE_RIB_WIDTH) // pitch)
    field_x = (BASE_X - LATTICE_X) / 2.0
    field_y = (BASE_Y - LATTICE_Y) / 2.0

    for i in range(count):
        x = field_x + i * pitch + LATTICE_RIB_WIDTH
        if x + LATTICE_SLOT_WIDTH > field_x + LATTICE_X:
            break
        slot = Part.makeBox(
            LATTICE_SLOT_WIDTH,
            LATTICE_Y,
            BASE_THICKNESS + 2.0,
            App.Vector(x, field_y, -1.0),
        )
        shape = shape.cut(slot)
    return shape


def _cut_threaded_rod_holes(shape):
    """Cut four 4.30 mm clearance holes through the bottom plate."""
    for x in (ROD_HOLE_X, BASE_X - ROD_HOLE_X):
        for y in (ROD_HOLE_Y, BASE_Y - ROD_HOLE_Y):
            hole = Part.makeCylinder(
                ROD_HOLE_DIAMETER / 2.0,
                BASE_THICKNESS + 2.0,
                App.Vector(x, y, -1.0),
            )
            shape = shape.cut(hole)
    return shape


def _add_feet(shape):
    """Fuse four integral cylindrical feet to the underside of the plate."""
    for x in (FOOT_INSET, BASE_X - FOOT_INSET):
        for y in (FOOT_INSET, BASE_Y - FOOT_INSET):
            foot = Part.makeCylinder(
                FOOT_DIAMETER / 2.0,
                FOOT_HEIGHT,
                App.Vector(x, y, -FOOT_HEIGHT),
            )
            shape = shape.fuse(foot)
    return shape


def _add_wall_guides(shape):
    """Create the four plug-in guide rails around the perimeter."""
    channel = WALL_THICKNESS + 2.0 * WALL_CLEARANCE
    outer = GUIDE_EDGE
    inner = outer + GUIDE_RAIL_WIDTH + channel
    side_len = BASE_X - 2.0 * GUIDE_EDGE
    rails = []

    for y in (outer, inner):
        rails.append(Part.makeBox(side_len, GUIDE_RAIL_WIDTH, GUIDE_HEIGHT,
                                  App.Vector(GUIDE_EDGE, y, BASE_THICKNESS)))
        rails.append(Part.makeBox(side_len, GUIDE_RAIL_WIDTH, GUIDE_HEIGHT,
                                  App.Vector(GUIDE_EDGE, BASE_Y - y - GUIDE_RAIL_WIDTH, BASE_THICKNESS)))

    for x in (outer, inner):
        rails.append(Part.makeBox(GUIDE_RAIL_WIDTH, side_len, GUIDE_HEIGHT,
                                  App.Vector(x, GUIDE_EDGE, BASE_THICKNESS)))
        rails.append(Part.makeBox(GUIDE_RAIL_WIDTH, side_len, GUIDE_HEIGHT,
                                  App.Vector(BASE_X - x - GUIDE_RAIL_WIDTH, GUIDE_EDGE, BASE_THICKNESS)))

    for rail in rails:
        shape = shape.fuse(rail)

    for x in (GUIDE_EDGE, BASE_X - GUIDE_EDGE - CORNER_POST_SIZE):
        for y in (GUIDE_EDGE, BASE_Y - GUIDE_EDGE - CORNER_POST_SIZE):
            post = Part.makeBox(CORNER_POST_SIZE, CORNER_POST_SIZE, GUIDE_HEIGHT,
                                App.Vector(x, y, BASE_THICKNESS))
            shape = shape.fuse(post)

    return shape


def make_bottom():
    """Return the complete printable bottom as one fused FreeCAD Shape."""
    shape = Part.makeBox(BASE_X, BASE_Y, BASE_THICKNESS)
    shape = _cut_lamella_slots(shape)
    shape = _cut_threaded_rod_holes(shape)
    shape = _add_feet(shape)
    shape = _add_wall_guides(shape)
    return shape.removeSplitter()


def create_document():
    doc = App.newDocument("ASROCK_4x4_Bottom")
    obj = doc.addObject("PartDesign::Feature", "Bottom")
    obj.Label = "ASROCK 4x4 - Bottom (one piece)"
    obj.Shape = make_bottom()
    doc.recompute()
    return doc, obj


if __name__ == "__main__":
    create_document()
