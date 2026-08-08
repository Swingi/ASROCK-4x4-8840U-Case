import FreeCAD as App
import Part


def make_lamella_field(size=150.0, width=3.0, gap=3.0, height=3.0):
    count = int((size + gap) // (width + gap))
    field = None
    for i in range(count):
        x = i * (width + gap)
        if x + width > size:
            break
        rib = Part.makeBox(width, size, height, App.Vector(x, 0, 0))
        field = rib if field is None else field.fuse(rib)
    return field
