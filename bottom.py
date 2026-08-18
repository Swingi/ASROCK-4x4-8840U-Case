import os
import importlib.util
import FreeCAD as App
import Part

# Load the project's config.py explicitly from this directory.
_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
_CONFIG_PATH = os.path.join(_PROJECT_DIR, "config.py")
_CONFIG_NAME = "_asrock_case_config"
spec = importlib.util.spec_from_file_location(_CONFIG_NAME, _CONFIG_PATH)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

# Export parameters locally for a compact geometry script.
for _name in dir(config):
    if _name.isupper():
        globals()[_name] = getattr(config, _name)


def _cut_lamella_slots(shape):
    """Cut the ventilation slots through the central 150 x 150 mm field."""
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
    """Create four 4.30 mm clearance holes through the bottom plate."""
    for x in (ROD_HOLE_X, BASE_X - ROD_HOLE_X):
        for y in (ROD_HOLE_Y, BASE_Y - ROD_HOLE_Y):
            hole = Part.makeCylinder(
                ROD_HOLE_DIAMETER / 2.0,
                BASE_THICKNESS + 2.0,
                App.Vector(x, y, -1.0),
            )
            shape = shape.cut(hole)
    return shape


def _add_feet_and_threads(shape):
    """Add four wide integral feet aligned exactly with the rod holes.

    Each foot has a blind 3.30 mm M4 tap-drill hole from its top, so a
    threaded M4 rod can pass through the 4.30 mm plate hole and screw into
    the foot itself.
    """
    for x in (ROD_HOLE_X, BASE_X - ROD_HOLE_X):
        for y in (ROD_HOLE_Y, BASE_Y - ROD_HOLE_Y):
            foot = Part.makeCylinder(
                FOOT_DIAMETER / 2.0,
                FOOT_HEIGHT,
                App.Vector(x, y, -FOOT_HEIGHT),
            )
            shape = shape.fuse(foot)

            # Blind tap-drill hole starts directly under the bottom plate.
            thread_hole = Part.makeCylinder(
                FOOT_THREAD_CORE_DIAMETER / 2.0,
                FOOT_THREAD_DEPTH,
                App.Vector(x, y, -FOOT_THREAD_DEPTH),
            )
            shape = shape.cut(thread_hole)
    return shape


def _add_filter_drawer_guides(shape):
    """Add underside rails for a removable dust-filter drawer.

    The tray slides in from the front between the two front feet. The
    guides are integrated into the printed bottom; the filter tray itself
    remains a separate printable part.
    """
    rail_z = -FILTER_DRAWER_RAIL_HEIGHT
    x_left = (BASE_X - FILTER_DRAWER_WIDTH) / 2.0
    x_right = x_left + FILTER_DRAWER_WIDTH - FILTER_DRAWER_RAIL_WIDTH
    y_start = 8.0
    rail_length = FILTER_DRAWER_LENGTH

    for x in (x_left, x_right):
        rail = Part.makeBox(
            FILTER_DRAWER_RAIL_WIDTH,
            rail_length,
            FILTER_DRAWER_RAIL_HEIGHT,
            App.Vector(x, y_start, rail_z),
        )
        shape = shape.fuse(rail)

    # Rear stop keeps the drawer from being pushed too far into the case.
    stop_y = y_start + rail_length
    stop = Part.makeBox(
        FILTER_DRAWER_WIDTH,
        FILTER_DRAWER_STOP,
        FILTER_DRAWER_RAIL_HEIGHT,
        App.Vector(x_left, stop_y, rail_z),
    )
    shape = shape.fuse(stop)
    return shape


def _add_wall_guides(shape):
    """Create a robust continuous plug-in guide for the one-piece lid.

    The future lid's 3 mm side-wall tongues fit into a continuous channel
    with 0.30 mm clearance on each side. Two parallel raised rails define
    the channel on all four sides. The guide is intentionally deeper than
    the old 8 mm version to resist rocking of the one-piece lid + walls.
    """
    channel = WALL_THICKNESS + 2.0 * WALL_CLEARANCE
    outer_x = GUIDE_EDGE
    outer_y = GUIDE_EDGE
    inner_x = GUIDE_EDGE + GUIDE_RAIL_WIDTH + channel
    inner_y = GUIDE_EDGE + GUIDE_RAIL_WIDTH + channel

    # Four outer rails.
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

    # Four inner rails. Together with the outer rails they form the wall slot.
    rails += [
        Part.makeBox(BASE_X - 2 * inner_x, GUIDE_RAIL_WIDTH, GUIDE_HEIGHT,
                     App.Vector(inner_x, inner_y - GUIDE_RAIL_WIDTH,
                                BASE_THICKNESS)),
        Part.makeBox(BASE_X - 2 * inner_x, GUIDE_RAIL_WIDTH, GUIDE_HEIGHT,
                     App.Vector(inner_x, BASE_Y - inner_y, BASE_THICKNESS)),
        Part.makeBox(GUIDE_RAIL_WIDTH, BASE_Y - 2 * inner_y, GUIDE_HEIGHT,
                     App.Vector(inner_x - GUIDE_RAIL_WIDTH, inner_y,
                                BASE_THICKNESS)),
        Part.makeBox(GUIDE_RAIL_WIDTH, BASE_Y - 2 * inner_y, GUIDE_HEIGHT,
                     App.Vector(BASE_X - inner_x, inner_y, BASE_THICKNESS)),
    ]

    for rail in rails:
        shape = shape.fuse(rail)

    # Strong corner blocks tie the guide rails together.
    for x in (GUIDE_EDGE, BASE_X - GUIDE_EDGE - CORNER_POST_SIZE):
        for y in (GUIDE_EDGE, BASE_Y - GUIDE_EDGE - CORNER_POST_SIZE):
            post = Part.makeBox(
                CORNER_POST_SIZE,
                CORNER_POST_SIZE,
                GUIDE_HEIGHT,
                App.Vector(x, y, BASE_THICKNESS),
            )
            shape = shape.fuse(post)

    return shape


def make_bottom():
    """Return the complete printable bottom as one fused FreeCAD Shape."""
    shape = Part.makeBox(BASE_X, BASE_Y, BASE_THICKNESS)
    shape = _cut_lamella_slots(shape)
    shape = _cut_threaded_rod_holes(shape)
    shape = _add_feet_and_threads(shape)
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
