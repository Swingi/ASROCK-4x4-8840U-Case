import os
import importlib.util
import FreeCAD as App
import Part

_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
_CONFIG_PATH = os.path.join(_PROJECT_DIR, "config.py")
spec = importlib.util.spec_from_file_location("_asrock_filter_config", _CONFIG_PATH)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)
for _name in dir(config):
    if _name.isupper():
        globals()[_name] = getattr(config, _name)


def _mesh_frame(width, height, thickness=2.5, frame=4.0, rib=2.0, pitch=6.0):
    """Printable frame carrying replaceable fine mesh.

    The centre remains open for real filter mesh. The printed ribs are only
    a support grid; they do not pretend to be the 120 um filter medium.
    """
    outer = Part.makeBox(width, height, thickness)
    inner = Part.makeBox(width - 2 * frame, height - 2 * frame,
                         thickness + 2.0, App.Vector(frame, frame, -1.0))
    shape = outer.cut(inner)

    x = frame + 1.0
    while x < width - frame - rib:
        shape = shape.fuse(Part.makeBox(rib, height - 2 * frame, thickness,
                                         App.Vector(x, frame, 0)))
        x += pitch

    y = frame + 1.0
    while y < height - frame - rib:
        shape = shape.fuse(Part.makeBox(width - 2 * frame, rib, thickness,
                                         App.Vector(frame, y, 0)))
        y += pitch
    return shape.removeSplitter()


def make_top_filter():
    return _mesh_frame(TOP_FILTER_SIZE, TOP_FILTER_SIZE,
                       TOP_FILTER_FRAME_THICKNESS, TOP_FILTER_FRAME_WIDTH)


def make_side_filter():
    # Matches the left/right vent field of the one-piece lid.
    margin = 22.0
    width = BASE_Y - 2 * margin + 6.0
    height = SIDE_WALL_HEIGHT - 10.0
    return _mesh_frame(width, height, SIDE_FILTER_FRAME_THICKNESS, 3.0)


def create_document():
    doc = App.newDocument("ASROCK_4x4_FilterPanels")
    top = doc.addObject("PartDesign::Feature", "TopFilter")
    top.Label = "Top dust filter frame - 140 mm fan"
    top.Shape = make_top_filter()

    left = doc.addObject("PartDesign::Feature", "LeftFilter")
    left.Label = "Left side dust filter frame"
    left.Shape = make_side_filter()

    right = doc.addObject("PartDesign::Feature", "RightFilter")
    right.Label = "Right side dust filter frame"
    right.Shape = make_side_filter()

    doc.recompute()
    return doc, (top, left, right)
