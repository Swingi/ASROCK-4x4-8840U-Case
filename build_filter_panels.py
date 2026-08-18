import os
import sys
import FreeCAD as App
import Part

PROJECT_DIR = r"D:/Download/ASROCK Box 4x4 8840U/repo/ASROCK-4x4-8840U-Case-main"
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)
for module_name in ("filter_panels", "config"):
    if module_name in sys.modules:
        del sys.modules[module_name]

from filter_panels import create_document

OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
STEP_DIR = os.path.join(OUTPUT_DIR, "step")
STL_DIR = os.path.join(OUTPUT_DIR, "stl")
FCSTD_DIR = os.path.join(OUTPUT_DIR, "freecad")


def build():
    for d in (STEP_DIR, STL_DIR, FCSTD_DIR):
        os.makedirs(d, exist_ok=True)
    doc, objs = create_document()
    doc.recompute()
    names = ("top_filter", "left_filter", "right_filter")
    for obj, name in zip(objs, names):
        Part.export([obj], os.path.join(STEP_DIR, f"ASROCK_4x4_{name}.step"))
        obj.Shape.exportStl(os.path.join(STL_DIR, f"ASROCK_4x4_{name}.stl"))
    doc.saveAs(os.path.join(FCSTD_DIR, "ASROCK_4x4_filter_panels.FCStd"))
    print("Filter panels build complete")
    return doc, objs


if __name__ == "__main__":
    build()
