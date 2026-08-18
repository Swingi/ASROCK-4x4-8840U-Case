import os
import sys
import FreeCAD as App
import Part

PROJECT_DIR = r"D:/Download/ASROCK Box 4x4 8840U/repo/ASROCK-4x4-8840U-Case-main"
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)
for module_name in ("filter_tray", "config"):
    if module_name in sys.modules:
        del sys.modules[module_name]

from filter_tray import create_document

OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
STEP_DIR = os.path.join(OUTPUT_DIR, "step")
STL_DIR = os.path.join(OUTPUT_DIR, "stl")
FCSTD_DIR = os.path.join(OUTPUT_DIR, "freecad")


def build():
    for d in (STEP_DIR, STL_DIR, FCSTD_DIR):
        os.makedirs(d, exist_ok=True)
    doc, obj = create_document()
    doc.recompute()
    step_file = os.path.join(STEP_DIR, "ASROCK_4x4_filter_tray.step")
    stl_file = os.path.join(STL_DIR, "ASROCK_4x4_filter_tray.stl")
    fcstd_file = os.path.join(FCSTD_DIR, "ASROCK_4x4_filter_tray.FCStd")
    Part.export([obj], step_file)
    obj.Shape.exportStl(stl_file)
    doc.saveAs(fcstd_file)
    print("Filter tray build complete")
    print("STEP :", step_file)
    print("STL  :", stl_file)
    print("FCStd:", fcstd_file)
    return doc, obj


if __name__ == "__main__":
    build()
