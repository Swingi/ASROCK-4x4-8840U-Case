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


def build(root):
    from bottom import make_base
    from lid import make_lid

    step_dir = os.path.join(root, "step")
    stl_dir = os.path.join(root, "stl")

    base = make_base()
    lid = make_lid()

    export_shape(base, step_dir, "base")
    export_shape(base, stl_dir, "base")
    export_shape(lid, step_dir, "lid")
    export_shape(lid, stl_dir, "lid")

    return base, lid


if __name__ == "__main__":
    root = r"D:/Download/ASROCK Box 4x4 8840U/repo/ASROCK-4x4-8840U-Case-main"
    build(root)
    print("ASROCK 4x4 export completed:", root)
