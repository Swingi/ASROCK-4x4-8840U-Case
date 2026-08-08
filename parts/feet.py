import FreeCAD as App
import Part


def make_feet(height=40.0, diameter=14.0):
    return Part.makeCylinder(diameter / 2.0, height)
