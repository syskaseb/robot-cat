"""Fine-tolerance mesh export unsupported by MCP export_model parameters.

The six native parts were authored with MCP. Default MCP tessellation made
the small journals >0.8% low-volume and faceted the nominal fit diameters.
This only tessellates saved parts, never creates or repairs printable CAD.
"""
import FreeCAD as A
import MeshPart
from support34 import OUT

folder = OUT / 'coupons'
doc = A.openDocument(str(folder / 'PETGFit34.FCStd'))
for name in ['Seat220', 'Seat221', 'Seat222', 'Journal78', 'Journal79', 'Journal80']:
    mesh = MeshPart.meshFromShape(Shape=doc.getObject(name).Shape,
        LinearDeflection=.005, AngularDeflection=.05, Relative=False)
    mesh.write(str(folder / (name + '.stl')))
    print(name, mesh.CountFacets, flush=True)
