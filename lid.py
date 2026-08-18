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


def _cut_rod_passages(shape):
    for x in (ROD_OFFSET_X, BASE_X - ROD_OFFSET_X):
        for y in (ROD_OFFSET_Y, BASE_Y - ROD_OFFSET_Y):
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


def _cut_io_openings(shape):
    """Open the real front and rear motherboard I/O sides.

    Front contains power, 2x USB-C, USB-A and audio. Rear contains 2x HDMI,
    dual LAN, 2x USB2 and DC-in. The openings are intentionally generous for
    connector shells and are parameterized in config.py for final FCStd fit.
    """
    front = Part.makeBox(
        FRONT_IO_WIDTH, WALL_THICKNESS + 4.0, FRONT_IO_HEIGHT,
        App.Vector((BASE_X - FRONT_IO_WIDTH) / 2.0, -2.0, FRONT_IO_Z),
    )
    rear = Part.makeBox(
        REAR_IO_WIDTH, WALL_THICKNESS + 4.0, REAR_IO_HEIGHT,
        App.Vector((BASE_X - REAR_IO_WIDTH) / 2.0,
                   BASE_Y - WALL_THICKNESS - 2.0, REAR_IO_Z),
    )
    return shape.cut(front).cut(rear)


def _cut_side_vents(shape):
    """Large side ventilation fields, leaving structural corner posts."""
    margin = 22.0
    z0 = LID_Z0 + 8.0
    height = SIDE_WALL_HEIGHT - 16.0
    width = BASE_X - 2.0 * margin
    cuts = [
        Part.makeBox(width, WALL_THICKNESS + 2.0, height,
                     App.Vector(margin, -1.0, z0)),
        Part.makeBox(width, WALL_THICKNESS + 2.0, height,
                     App.Vector(margin, BASE_Y - WALL_THICKNESS - 1.0, z0)),
        Part.makeBox(WALL_THICKNESS + 2.0, width, height,
                     App.Vector(-1.0, margin, z0)),
        Part.makeBox(WALL_THICKNESS + 2.0, width, height,
                     App.Vector(BASE_X - WALL_THICKNESS - 1.0, margin, z0)),
    ]
    for cut in cuts:
        shape = shape.cut(cut)
    return shape


def _add_filter_seats(shape):
    """Create retaining ledges for removable mesh filters on top and sides."""
    # Top filter: a 144 mm square mesh sits on a 2.5 mm recessed ledge around the fan opening.
    cx = BASE_X / 2.0
    cy = BASE_Y / 2.0
    outer = TOP_FILTER_SIZE / 2.0
    inner = FAN_OPENING_DIAMETER / 2.0 + 2.0
    z = LID_TOP_Z + LID_TOP_THICKNESS - 1.0

    # Four narrow rails around the circular fan opening, on the outside face.
    rail_w = TOP_FILTER_FRAME_WIDTH
    rails = [
        Part.makeBox(TOP_FILTER_SIZE, rail_w, TOP_FILTER_FRAME_THICKNESS,
                     App.Vector(cx - outer, cy - outer, z)),
        Part.makeBox(TOP_FILTER_SIZE, rail_w, TOP_FILTER_FRAME_THICKNESS,
                     App.Vector(cx - outer, cy + outer - rail_w, z)),
        Part.makeBox(rail_w, TOP_FILTER_SIZE - 2 * rail_w, TOP_FILTER_FRAME_THICKNESS,
                     App.Vector(cx - outer, cy - outer + rail_w, z)),
        Part.makeBox(rail_w, TOP_FILTER_SIZE - 2 * rail_w, TOP_FILTER_FRAME_THICKNESS,
                     App.Vector(cx + outer - rail_w, cy - outer + rail_w, z)),
    ]
    for rail in rails:
        shape = shape.fuse(rail)

    # Side filter retaining rails sit outside each vent field.
    margin = 22.0
    vent_w = BASE_X - 2 * margin
    vent_h = SIDE_WALL_HEIGHT - 16.0
    z0 = LID_Z0 + 8.0
    fw = SIDE_FILTER_FRAME_THICKNESS
    frame = 3.0

    # Front/rear horizontal and vertical filter rails.
    for y in (-fw, BASE_Y):
        for x in (margin - frame, BASE_X - margin):
            shape = shape.fuse(Part.makeBox(frame, fw, vent_h + 2 * frame,
                                            App.Vector(x, y, z0 - frame)))
        shape = shape.fuse(Part.makeBox(vent_w + 2 * frame, fw, frame,
                                        App.Vector(margin - frame, y, z0 - frame)))
        shape = shape.fuse(Part.makeBox(vent_w + 2 * frame, fw, frame,
                                        App.Vector(margin - frame, y, z0 + vent_h)))

    # Left/right filter rails.
    for x in (-fw, BASE_X):
        for y in (margin - frame, BASE_Y - margin):
            shape = shape.fuse(Part.makeBox(fw, frame, vent_h + 2 * frame,
                                            App.Vector(x, y, z0 - frame)))
        shape = shape.fuse(Part.makeBox(fw, vent_w + 2 * frame, frame,
                                        App.Vector(x, margin - frame, z0 - frame)))
        shape = shape.fuse(Part.makeBox(fw, vent_w + 2 * frame, frame,
                                        App.Vector(x, margin - frame, z0 + vent_h)))
    return shape


def _add_logo_recess(shape):
    """Shallow centered front recess for the supplied STAR WARS GALAXIES signet."""
    logo_w = 82.0
    logo_h = 48.0
    logo_depth = 1.2
    x = (BASE_X - logo_w) / 2.0
    y = -0.1
    z = LID_Z0 + SIDE_WALL_HEIGHT - 54.0
    recess = Part.makeBox(logo_w, logo_depth + 0.5, logo_h,
                          App.Vector(x, y, z))
    return shape.cut(recess)


def _add_corner_posts(shape):
    rib = 8.0
    for x in (0.0, BASE_X - rib):
        for y in (0.0, BASE_Y - rib):
            block = Part.makeBox(rib, rib, SIDE_WALL_HEIGHT,
                                 App.Vector(x, y, LID_Z0))
            shape = shape.fuse(block)
    return shape


def _add_guide_tongues(shape):
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
        shape = shape.fuse(Part.makeBox(
            tongue_w, BASE_Y - 2.0 * GUIDE_EDGE, tongue_h,
            App.Vector(x, GUIDE_EDGE, z)))
    for y in y_positions:
        shape = shape.fuse(Part.makeBox(
            BASE_X - 2.0 * GUIDE_EDGE, tongue_w, tongue_h,
            App.Vector(GUIDE_EDGE, y, z)))
    return shape


def _add_airflow_transition_baffles(shape):
    """Add thin internal transition vanes from the 140 mm fan region toward
    the 104 x 102 mm board envelope and back outward toward the lower region.

    They are thin guide surfaces rather than solid partitions, leaving the
    central airflow path open.
    """
    # Front/rear baffles: wide at the fan plane, narrow around board height,
    # then wide again near the lower exhaust region.
    zt = AIRFLOW_TRANSITION_TOP_Z
    zm = AIRFLOW_TRANSITION_BOARD_Z
    zb = AIRFLOW_TRANSITION_BOTTOM_Z
    top_l = (BASE_X - FAN_SIZE) / 2.0
    top_r = BASE_X - top_l
    mid_l = (BASE_X - MAINBOARD_X) / 2.0
    mid_r = BASE_X - mid_l
    t = 2.5

    def prism_xz(points, y0):
        pts = [App.Vector(x, y0, z) for x, z in points]
        pts.append(pts[0])
        return Part.Face(Part.makePolygon(pts)).extrude(App.Vector(0, t, 0))

    # Two sloped front/rear guide sheets, one on each side of the central path.
    for y0 in (WALL_THICKNESS + 2.0, BASE_Y - WALL_THICKNESS - 2.0 - t):
        p1 = [(top_l, zt), (mid_l, zm), (mid_l, zb), (top_l, zb)]
        p2 = [(mid_r, zm), (top_r, zt), (top_r, zb), (mid_r, zb)]
        shape = shape.fuse(prism_xz(p1, y0)).fuse(prism_xz(p2, y0))

    # Left/right guide sheets use the 102 mm board dimension.
    top_b = (BASE_Y - FAN_SIZE) / 2.0
    top_t = BASE_Y - top_b
    mid_b = (BASE_Y - MAINBOARD_Y) / 2.0
    mid_t = BASE_Y - mid_b

    def prism_yz(points, x0):
        pts = [App.Vector(x0, y, z) for y, z in points]
        pts.append(pts[0])
        return Part.Face(Part.makePolygon(pts)).extrude(App.Vector(t, 0, 0))

    for x0 in (WALL_THICKNESS + 2.0, BASE_X - WALL_THICKNESS - 2.0 - t):
        p1 = [(top_b, zt), (mid_b, zm), (mid_b, zb), (top_b, zb)]
        p2 = [(mid_t, zm), (top_t, zt), (top_t, zb), (mid_t, zb)]
        shape = shape.fuse(prism_yz(p1, x0)).fuse(prism_yz(p2, x0))
    return shape


def make_lid():
    top = Part.makeBox(BASE_X, BASE_Y, LID_TOP_THICKNESS,
                       App.Vector(0, 0, LID_TOP_Z))
    front = Part.makeBox(BASE_X, WALL_THICKNESS, SIDE_WALL_HEIGHT,
                         App.Vector(0, 0, LID_Z0))
    rear = Part.makeBox(BASE_X, WALL_THICKNESS, SIDE_WALL_HEIGHT,
                        App.Vector(0, BASE_Y - WALL_THICKNESS, LID_Z0))
    left = Part.makeBox(WALL_THICKNESS, BASE_Y - 2 * WALL_THICKNESS,
                        SIDE_WALL_HEIGHT, App.Vector(0, WALL_THICKNESS, LID_Z0))
    right = Part.makeBox(WALL_THICKNESS, BASE_Y - 2 * WALL_THICKNESS,
                         SIDE_WALL_HEIGHT,
                         App.Vector(BASE_X - WALL_THICKNESS, WALL_THICKNESS, LID_Z0))

    shape = top.fuse(front).fuse(rear).fuse(left).fuse(right)
    shape = _cut_fan_opening(shape)
    shape = _cut_fan_mount_holes(shape)
    shape = _cut_rod_passages(shape)
    shape = _cut_io_openings(shape)
    shape = _cut_side_vents(shape)
    shape = _add_corner_posts(shape)
    shape = _add_guide_tongues(shape)
    shape = _add_filter_seats(shape)
    shape = _add_logo_recess(shape)
    shape = _add_airflow_transition_baffles(shape)
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
