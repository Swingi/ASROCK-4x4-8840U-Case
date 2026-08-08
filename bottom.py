import FreeCAD as App
import Part
from config import BASE_X, BASE_Y, BASE_Z, BASE_MARGIN, M3_CLEARANCE


def make_base():
    base = Part.makeBox(BASE_X, BASE_Y, BASE_Z)

    # Four corner M3 clearance holes.
    inset = 12.0
    for x in (inset, BASE_X - inset):
        for y in (inset, BASE_Y - inset):
            hole = Part.makeCylinder(M3_CLEARANCE / 2.0, BASE_Z + 2.0,
                                     App.Vector(x, y, -1.0))
            base = base.cut(hole)

    return base


if __name__ == "__main__":
    doc = App.newDocument("ASROCK_4x4_Base")
    obj = doc.addObject("PartDesign::Feature", "Base")
    obj.Shape = make_base()
    doc.recompute()
