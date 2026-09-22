"""Diagnostic only: search a rigid, cable-end-first MG92B insertion path."""
import FreeCAD as A
import Part
from support34 import SOURCE, MASTER, instance
from audit34 import common_volume

doc = A.openDocument(str(MASTER))
support = instance(doc, 'ServoSupport34')
servo = Part.Shape()
servo.read(str(SOURCE / 'shape-cache/MG92BCase29.brep'))
slab = Part.makeBox(100, 100, 3, A.Vector(120, -50, 74))
for dz in (22, 21.5, 21, 20.5, 20, 19.8, 19.6, 19.4, 19.2, 19, 18.5, 18):
    possible = []
    for deg in range(0, 31, 2):
        pose = A.Placement(A.Vector(0, 0, dz), A.Rotation(A.Vector(1, 0, 0), deg), A.Vector(171, -.75, 77))
        s = servo.copy(); s.Placement = pose * s.Placement
        cut = s.common(slab)
        if cut.isNull() or cut.Volume < 1e-9:
            dy = 0
        else:
            box = cut.BoundBox
            if box.YLength > 23.3:
                continue
            dy = -.75 - (box.YMin + box.YMax) / 2
        s.translate(A.Vector(0, dy, 0))
        v = common_volume(s, support)
        if v < .01:
            possible.append((deg, round(dy, 3)))
    print(dz, possible, flush=True)
