import FreeCAD as App
import Part
import os


def export_shape(shape, directory, name):
    os.makedirs(directory, exist_ok=True)
    step_path = os.path.join(directory, name + ".step")
    stl_path = os.path.join(directory, name + ".stl")
    Part.export([shape], step_path)
    shape.exportStl(stl_path)
    return step_path, stl_path


if __name__ == "__main__":
    from bottom import make_base
    from lid import make_lid
    root = os.path.dirname(os.path.abspath(__file__))
    export_shape(make_base(), os.path.join(root, "step"), "base")
    export_shape(make_lid(), os.path.join(root, "step"), "lid")
