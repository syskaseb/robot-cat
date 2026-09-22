"""Tiny three-document API probe; writes only to a caller's empty scratch dir."""
import sys
from pathlib import Path
import FreeCAD as A
import Part


def main():
    folder = Path(sys.argv[1]).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    assert not list(folder.iterdir())
    p = A.newDocument("ProbeParameters")
    v = p.addObject("App::VarSet", "Vars")
    v.addProperty("App::PropertyFloat", "Diameter")
    v.Diameter = 2.4
    p.saveAs(str(folder / "ProbeParameters.FCStd"))
    m = A.newDocument("ProbeModule")
    shape = m.addObject("Part::Feature", "Box")
    shape.Shape = Part.makeBox(1, 2, 3)
    m.saveAs(str(folder / "ProbeModule.FCStd"))
    link = m.addObject("App::Link", "MountInterface")
    link.setLink(v)
    m.saveAs(str(folder / "ProbeModule.FCStd"))
    asm = A.newDocument("ProbeAssembly")
    asm.saveAs(str(folder / "ProbeAssembly.FCStd"))
    instance = asm.addObject("App::Link", "Instance")
    instance.setLink(shape)
    asm.saveAs(str(folder / "ProbeAssembly.FCStd"))
    for name in list(A.listDocuments()):
        A.closeDocument(name)
    A.openDocument(str(folder / "ProbeAssembly.FCStd"))
    print("AUTOLOADED", sorted(A.listDocuments()), flush=True)
    assert len(A.listDocuments()) == 3


if __name__ == "__main__":
    main()
