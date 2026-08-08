import FreeCAD as App
import Part
from config import BASE_X, BASE_Y, WALL, FAN_INTAKE, FAN_EXHAUST


def make_lid(height=55.0):
    # Simple open-bottom enclosure shell. Fan openings are represented by cuts.
    outer = Part.makeBox(BASE_X, BASE_Y, height)
    inner = Part.makeBox(BASE_X - 2 * WALL, BASE_Y - 2 * WALL,
                         height - WALL, App.Vector(WALL, WALL, WALL))
    shell = outer.cut(inner)

    # Centered 140 mm intake opening in the lid.
    cx = (BASE_X - FAN_INTAKE) / 2.0
    cy = (BASE_Y - FAN_INTAKE) / 2.0
    intake = Part.makeBox(FAN_INTAKE, FAN_INTAKE, WALL + 2,
                          App.Vector(cx, cy, height - WALL - 1))
    shell = shell.cut(intake)
    return shell


if __name__ == "__main__":
    doc = App.newDocument("ASROCK_4x4_Lid")
    obj = doc.addObject("PartDesign::Feature", "Lid")
    obj.Shape = make_lid()
    doc.recompute()
