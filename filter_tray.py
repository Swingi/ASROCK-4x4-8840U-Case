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

FILTER_MARGIN = 4.0
FILTER_THICKNESS = 2.5
HANDLE_DEPTH = 10.0
HANDLE_HEIGHT = 8.0


def make_filter_tray():
    # Sliding tray for the removable dust filter. It is intentionally a
    # separate print from the bottom because it must slide out.
    width = FILTER_DRAWER_WIDTH - 2.0 * FILTER_DRAWER_CLEARANCE
    length = FILTER_DRAWER_LENGTH - 2.0 * FILTER_DRAWER_CLEARANCE
    wall = 3.0
    z = -FILTER_DRAWER_THICKNESS

    outer = Part.makeBox(width, length, FILTER_DRAWER_THICKNESS,
                         App.Vector(FILTER_DRAWER_CLEARANCE,
                                    FILTER_DRAWER_CLEARANCE, z))

    # Raised perimeter retaining lip for the magnetic dust filter.
    tray = outer
    for x, y, sx, sy in (
        (0, 0, width, wall),
        (0, length - wall, width, wall),
        (0, wall, wall, length - 2 * wall),
        (width - wall, wall, wall, length - 2 * wall),
    ):
        tray = tray.fuse(Part.makeBox(sx, sy, FILTER_DRAWER_RAIL_HEIGHT,
                                      App.Vector(x + FILTER_DRAWER_CLEARANCE,
                                                 y + FILTER_DRAWER_CLEARANCE,
                                                 z + FILTER_DRAWER_THICKNESS)))

    # Small front pull handle.
    handle = Part.makeBox(width * 0.35, HANDLE_DEPTH, HANDLE_HEIGHT,
                          App.Vector((BASE_X - width * 0.35) / 2.0,
                                     -HANDLE_DEPTH,
                                     z))
    tray = tray.fuse(handle)
    return tray.removeSplitter()


def create_document():
    doc = App.newDocument("ASROCK_4x4_Filter_Tray")
    obj = doc.addObject("PartDesign::Feature", "FilterTray")
    obj.Label = "ASROCK 4x4 - Dust Filter Tray"
    obj.Shape = make_filter_tray()
    doc.recompute()
    return doc, obj


if __name__ == "__main__":
    create_document()
