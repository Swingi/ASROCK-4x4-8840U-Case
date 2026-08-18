import os
import importlib.util
import math
import FreeCAD as App
import Part

_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
_CONFIG_PATH = os.path.join(_PROJECT_DIR, "config.py")
spec = importlib.util.spec_from_file_location("_asrock_bottom_config", _CONFIG_PATH)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)
for _name in dir(config):
    if _name.isupper():
        globals()[_name] = getattr(config, _name)


def _hex_prism(cx, cy, z0, depth, across_flats):
    """Regular hexagonal prism used to capture an M3 safety/nyloc nut."""
    r = across_flats / math.sqrt(3.0)
    pts = []
    for i in range(6):
        a = math.radians(30.0 + i * 60.0)
        pts.append(App.Vector(cx + r * math.cos(a), cy + r * math.sin(a), z0))
    pts.append(pts[0])
    wire = Part.makePolygon(pts)
    return Part.Face(wire).extrude(App.Vector(0, 0, depth))


def _cut_lamella_slots(shape):
    pitch = LATTICE_SLOT_WIDTH + LATTICE_RIB_WIDTH
    count = int((LATTICE_X + LATTICE_RIB_WIDTH) // pitch)
    field_x = (BASE_X - LATTICE_X) / 2.0
    field_y = (BASE_Y - LATTICE_Y) / 2.0
    for i in range(count):
        x = field_x + i * pitch + LATTICE_RIB_WIDTH
        if x + LATTICE_SLOT_WIDTH > field_x + LATTICE_X:
            break
        slot = Part.makeBox(
            LATTICE_SLOT_WIDTH, LATTICE_Y, BASE_THICKNESS + 2.0,
            App.Vector(x, field_y, -1.0),
        )
        shape = shape.cut(slot)
    return shape


def _cut_threaded_rod_holes(shape):
    """M3 clearance holes through the bottom and all four feet."""
    for x in (ROD_OFFSET_X, BASE_X - ROD_OFFSET_X):
        for y in (ROD_OFFSET_Y, BASE_Y - ROD_OFFSET_Y):
            hole = Part.makeCylinder(
                ROD_HOLE_DIAMETER / 2.0,
                FOOT_HEIGHT + BASE_THICKNESS + 2.0,
                App.Vector(x, y, -FOOT_HEIGHT - 1.0),
            )
            shape = shape.cut(hole)
    return shape


def _add_feet_and_nut_captures(shape):
    """Add four wide feet with captured M3 washer and safety/nyloc nut seats.

    The M3 threaded rod passes through the bottom and foot. From underneath,
    a 7.2 mm washer sits in a shallow counterbore and an M3 safety/nyloc nut
    is captured in the deeper hexagonal pocket. This mechanically locks each
    rod to its foot without relying on printed threads.
    """
    for x in (ROD_OFFSET_X, BASE_X - ROD_OFFSET_X):
        for y in (ROD_OFFSET_Y, BASE_Y - ROD_OFFSET_Y):
            foot = Part.makeCylinder(
                FOOT_DIAMETER / 2.0, FOOT_HEIGHT,
                App.Vector(x, y, -FOOT_HEIGHT),
            )
            shape = shape.fuse(foot)

            # Washer recess at the underside of the foot.
            washer_pocket = Part.makeCylinder(
                M3_WASHER_OD / 2.0,
                M3_WASHER_POCKET_DEPTH,
                App.Vector(x, y, -FOOT_HEIGHT),
            )
            shape = shape.cut(washer_pocket)

            # Nut capture immediately above the washer recess.
            nut_pocket = _hex_prism(
                x, y,
                -FOOT_HEIGHT + M3_WASHER_POCKET_DEPTH,
                M3_NUT_POCKET_DEPTH,
                M3_NUT_POCKET_AF,
            )
            shape = shape.cut(nut_pocket)
    return shape


def _add_filter_drawer_guides(shape):
    rail_z = -FILTER_DRAWER_RAIL_HEIGHT
    x_left = (BASE_X - FILTER_DRAWER_WIDTH) / 2.0
    x_right = x_left + FILTER_DRAWER_WIDTH - FILTER_DRAWER_RAIL_WIDTH
    y_start = 8.0
    rail_length = FILTER_DRAWER_LENGTH
    for x in (x_left, x_right):
        rail = Part.makeBox(
            FILTER_DRAWER_RAIL_WIDTH, rail_length, FILTER_DRAWER_RAIL_HEIGHT,
            App.Vector(x, y_start, rail_z),
        )
        shape = shape.fuse(rail)
    stop_y = y_start + rail_length
    stop = Part.makeBox(
        FILTER_DRAWER_WIDTH, FILTER_DRAWER_STOP, FILTER_DRAWER_RAIL_HEIGHT,
        App.Vector(x_left, stop_y, rail_z),
    )
    shape = shape.fuse(stop)
    return shape


def _add_wall_guides(shape):
    """Continuous 12 mm deep plug-in guide for the one-piece lid."""
    channel = WALL_THICKNESS + 2.0 * WALL_CLEARANCE
    inner_x = GUIDE_EDGE + GUIDE_RAIL_WIDTH + channel
    inner_y = GUIDE_EDGE + GUIDE_RAIL_WIDTH + channel
    rails = [
        Part.makeBox(BASE_X - 2 * GUIDE_EDGE, GUIDE_RAIL_WIDTH, GUIDE_HEIGHT,
                     App.Vector(GUIDE_EDGE, GUIDE_EDGE, BASE_THICKNESS)),
        Part.makeBox(BASE_X - 2 * GUIDE_EDGE, GUIDE_RAIL_WIDTH, GUIDE_HEIGHT,
                     App.Vector(GUIDE_EDGE, BASE_Y - GUIDE_EDGE - GUIDE_RAIL_WIDTH,
                                BASE_THICKNESS)),
        Part.makeBox(GUIDE_RAIL_WIDTH, BASE_Y - 2 * GUIDE_EDGE, GUIDE_HEIGHT,
                     App.Vector(GUIDE_EDGE, GUIDE_EDGE, BASE_THICKNESS)),
        Part.makeBox(GUIDE_RAIL_WIDTH, BASE_Y - 2 * GUIDE_EDGE, GUIDE_HEIGHT,
                     App.Vector(BASE_X - GUIDE_EDGE - GUIDE_RAIL_WIDTH,
                                GUIDE_EDGE, BASE_THICKNESS)),
    ]
    rails += [
        Part.makeBox(BASE_X - 2 * inner_x, GUIDE_RAIL_WIDTH, GUIDE_HEIGHT,
                     App.Vector(inner_x, inner_y - GUIDE_RAIL_WIDTH, BASE_THICKNESS)),
        Part.makeBox(BASE_X - 2 * inner_x, GUIDE_RAIL_WIDTH, GUIDE_HEIGHT,
                     App.Vector(inner_x, BASE_Y - inner_y, BASE_THICKNESS)),
        Part.makeBox(GUIDE_RAIL_WIDTH, BASE_Y - 2 * inner_y, GUIDE_HEIGHT,
                     App.Vector(inner_x - GUIDE_RAIL_WIDTH, inner_y, BASE_THICKNESS)),
        Part.makeBox(GUIDE_RAIL_WIDTH, BASE_Y - 2 * inner_y, GUIDE_HEIGHT,
                     App.Vector(BASE_X - inner_x, inner_y, BASE_THICKNESS)),
    ]
    for rail in rails:
        shape = shape.fuse(rail)
    for x in (GUIDE_EDGE, BASE_X - GUIDE_EDGE - CORNER_POST_SIZE):
        for y in (GUIDE_EDGE, BASE_Y - GUIDE_EDGE - CORNER_POST_SIZE):
            post = Part.makeBox(CORNER_POST_SIZE, CORNER_POST_SIZE, GUIDE_HEIGHT,
                                App.Vector(x, y, BASE_THICKNESS))
            shape = shape.fuse(post)
    return shape


def make_bottom():
    shape = Part.makeBox(BASE_X, BASE_Y, BASE_THICKNESS)
    shape = _cut_lamella_slots(shape)
    shape = _add_feet_and_nut_captures(shape)
    shape = _cut_threaded_rod_holes(shape)
    shape = _add_filter_drawer_guides(shape)
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
