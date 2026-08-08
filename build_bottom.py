import os
import sys
import FreeCAD as App
import Part

# IMPORTANT: FreeCAD's Python console does not define __file__ when this
# script is launched with exec(open(...).read()). Therefore the project
# directory is configured explicitly here for the current local checkout.
PROJECT_DIR = r"D:/Download/ASROCK Box 4x4 8840U/repo/ASROCK-4x4-8840U-Case-main"

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from bottom import create_document

OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
STEP_DIR = os.path.join(OUTPUT_DIR, "step")
STL_DIR = os.path.join(OUTPUT_DIR, "stl")
FCSTD_DIR = os.path.join(OUTPUT_DIR, "freecad")


def build():
    os.makedirs(STEP_DIR, exist_ok=True)
    os.makedirs(STL_DIR, exist_ok=True)
    os.makedirs(FCSTD_DIR, exist_ok=True)

    doc, obj = create_document()
    doc.recompute()

    step_file = os.path.join(STEP_DIR, "ASROCK_4x4_bottom.step")
    stl_file = os.path.join(STL_DIR, "ASROCK_4x4_bottom.stl")
    fcstd_file = os.path.join(FCSTD_DIR, "ASROCK_4x4_bottom.FCStd")

    Part.export([obj], step_file)
    obj.Shape.exportStl(stl_file)
    doc.recompute()
    doc.saveAs(fcstd_file)

    print("Bottom build complete")
    print("STEP :", step_file)
    print("STL  :", stl_file)
    print("FCStd:", fcstd_file)
    return doc, obj


if __name__ == "__main__":
    build()
