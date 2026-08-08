import os
import FreeCAD as App
import Part

from bottom import create_document


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
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
