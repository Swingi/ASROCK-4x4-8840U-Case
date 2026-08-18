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
            hole = Part.makeCylinder(ROD_PASSAGE_DIAMETER / 2.0,
                                     LID_TOP_THICKNESS + 2.0,
                                     App.Vector(x, y, LID_TOP_Z - 1.0))
            shape = shape.cut(hole)
    return shape


def _cut_fan_opening(shape):
    opening = Part.makeCylinder(FAN_OPENING_DIAMETER / 2.0,
                                LID_TOP_THICKNESS + 2.0,
                                App.Vector(BASE_X / 2.0, BASE_Y / 2.0,
                                           LID_TOP_Z - 1.0))
    return shape.cut(opening)


def _cut_fan_mount_holes(shape):
    cx, cy = BASE_X / 2.0, BASE_Y / 2.0
    d = FAN_MOUNT_HOLE_SPACING / 2.0
    for x in (cx - d, cx + d):
        for y in (cy - d, cy + d):
            hole = Part.makeCylinder(FAN_MOUNT_HOLE_DIAMETER / 2.0,
                                     LID_TOP_THICKNESS + 2.0,
                                     App.Vector(x, y, LID_TOP_Z - 1.0))
            shape = shape.cut(hole)
    return shape


def _cut_io_openings(shape):
    """Front and rear openings for the actual motherboard connector groups."""
    front = Part.makeBox(FRONT_IO_WIDTH, WALL_THICKNESS + 4.0, FRONT_IO_HEIGHT,
                         App.Vector((BASE_X - FRONT_IO_WIDTH) / 2.0,
                                    -2.0, FRONT_IO_Z))
    rear = Part.makeBox(REAR_IO_WIDTH, WALL_THICKNESS + 4.0, REAR_IO_HEIGHT,
                        App.Vector((BASE_X - REAR_IO_WIDTH) / 2.0,
                                   BASE_Y - WALL_THICKNESS - 2.0,
                                   REAR_IO_Z))
    return shape.cut(front).cut(rear)


def _cut_side_vents(shape):
    """Vent/filter fields only on left and right side walls.

    Front and rear remain structurally closed except for their motherboard
    I/O openings, so the connector locations stay visible and accessible.
    """
    margin = 22.0
    z0 = LID_Z0 + 8.0
    height = SIDE_WALL_HEIGHT - 16.0
    width = BASE_Y - 2.0 * margin
    cuts = [
        Part.makeBox(WALL_THICKNESS + 2.0, width, height,
                     App.Vector(-1.0, margin, z0)),
        Part.makeBox(WALL_THICKNESS + 2.0, width, height,
                     App.Vector(BASE_X - WALL_THICKNESS - 1.0,
                                margin, z0)),
    ]
    for cut in cuts:
        shape = shape.cut(cut)
    return shape


def _add_filter_seats(shape):
    """Integrated retaining rails for removable mesh filters on top and sides."""
    # Top: square filter frame around the 140 mm fan opening.
    cx, cy = BASE_X / 2.0, BASE_Y / 2.0
    outer = TOP_FILTER_SIZE / 2.0
    rail_w = TOP_FILTER_FRAME_WIDTH
    z = LID_TOP_Z + LID_TOP_THICKNESS
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

    # Left/right side filter frames around the vent openings.
    margin = 22.0
    vent_len = BASE_Y - 2.0 * margin
    vent_h = SIDE_WALL_HEIGHT - 16.0
    z0 = LID_Z0 + 8.0
    frame = 3.0
    rail_t = SIDE_FILTER_FRAME_THICKNESS

    for x in (-rail_t, BASE_X):
        # vertical rails
        shape = shape.fuse(Part.makeBox(rail_t, frame, vent_h + 2 * frame,
                                        App.Vector(x, margin - frame, z0 - frame)))
        shape = shape.fuse(Part.makeBox(rail_t, frame, vent_h + 2 * frame,
                                        App.Vector(x, BASE_Y - margin, z0 - frame)))
        # horizontal rails
        shape = shape.fuse(Part.makeBox(rail_t, vent_len, frame,
                                        App.Vector(x, margin, z0 - frame)))
        shape = shape.fuse(Part.makeBox(rail_t, vent_len, frame,
                                        App.Vector(x, margin, z0 + vent_h)))
    return shape


def _add_logo_recess(shape):
    """Shallow centered front recess for the supplied STAR WARS GALAXIES signet."""
    logo_w, logo_h = 82.0, 48.0
    x = (BASE_X - logo_w) / 2.0
    z = LID_Z0 + SIDE_WALL_HEIGHT - 54.0
    recess = Part.makeBox(logo_w, 1.7, logo_h, App.Vector(x, -0.1, z))
    return shape.cut(recess)


def _add_corner_posts(shape):
    rib = 8.0
    for x in (0.0, BASE_X - rib):
        for y in (0.0, BASE_Y - rib):
            shape = shape.fuse(Part.makeBox(rib, rib, SIDE_WALL_HEIGHT,
                                            App.Vector(x, y, LID_Z0)))
    return shape


def _add_guide_tongues(shape):
    tongue_h = min(GUIDE_HEIGHT - 1.0, 10.0)
    tongue_w = WALL_THICKNESS
    z = LID_Z0
    x_positions = (GUIDE_EDGE + GUIDE_RAIL_WIDTH + WALL_CLEARANCE,
                   BASE_X - GUIDE_EDGE - GUIDE_RAIL_WIDTH - WALL_CLEARANCE - tongue_w)
    y_positions = (GUIDE_EDGE + GUIDE_RAIL_WIDTH + WALL_CLEARANCE,
                   BASE_Y - GUIDE_EDGE - GUIDE_RAIL_WIDTH - WALL_CLEARANCE - tongue_w)
    for x in x_positions:
        shape = shape.fuse(Part.makeBox(tongue_w, BASE_Y - 2 * GUIDE_EDGE,
                                         tongue_h, App.Vector(x, GUIDE_EDGE, z)))
    for y in y_positions:
        shape = shape.fuse(Part.makeBox(BASE_X - 2 * GUIDE_EDGE, tongue_w,
                                         tongue_h, App.Vector(GUIDE_EDGE, y, z)))
    return shape


def _add_airflow_transition_baffles(shape):
    """Thin internal baffles create the requested wide-to-board-to-wide transition."""
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

    for y0 in (WALL_THICKNESS + 2.0,
               BASE_Y - WALL_THICKNESS - 2.0 - t):
        left = [(top_l, zt), (mid_l, zm), (mid_l, zb), (top_l, zb)]
        right = [(mid_r, zm), (top_r, zt), (top_r, zb), (mid_r, zb)]
        shape = shape.fuse(prism_xz(left, y0)).fuse(prism_xz(right, y0))

    top_b = (BASE_Y - FAN_SIZE) / 2.0
    top_t = BASE_Y - top_b
    mid_b = (BASE_Y - MAINBOARD_Y) / 2.0
    mid_t = BASE_Y - mid_b

    def prism_yz(points, x0):
        pts = [App.Vector(x0, y, z) for y, z in points]
        pts.append(pts[0])
        return Part.Face(Part.makePolygon(pts)).extrude(App.Vector(t, 0, 0))

    for x0 in (WALL_THICKNESS + 2.0,
               BASE_X - WALL_THICKNESS - 2.0 - t):
        low = [(top_b, zt), (mid_b, zm), (mid_b, zb), (top_b, zb)]
        high = [(mid_t, zm), (top_t, zt), (top_t, zb), (mid_t, zb)]
        shape = shape.fuse(prism_yz(low, x0)).fuse(prism_yz(high, x0))
    return shape


def make_lid():
    # Top + all four walls are one fused printable part.
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
