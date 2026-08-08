import FreeCAD as App
import Part


def make_m3_mount(height=10.0, head_diameter=6.0, head_depth=3.0):
    body = Part.makeCylinder(5.0, height)
    clearance = Part.makeCylinder(1.7, height + 2, App.Vector(0, 0, -1))
    pocket = Part.makeCylinder(head_diameter / 2.0, head_depth,
                               App.Vector(0, 0, height - head_depth))
    return body.cut(clearance).cut(pocket)
