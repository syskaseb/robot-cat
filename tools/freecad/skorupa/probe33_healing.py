"""Read-only OCC healing experiments; results are not installed geometry."""
from pathlib import Path
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[3]
d=A.openDocument(str(ROOT/'hardware/skorupa/v33/HeadDesign33.FCStd'))
optic=A.openDocument(str(ROOT/'hardware/skorupa/v32/OpticsDesign32.FCStd')).getObject('OpticalReserve32').Shape
original=Part.Shape();original.read(str(ROOT/'hardware/skorupa/v32/shape-cache/HeadFront.brep'))
print('fix API',original.fix.__doc__,flush=True)
for name,shape in [('original',original),('v33',d.getObject('HeadFace33').Shape)]:
    for mode in ['raw','fix','refine','sew']:
        s=shape.copy()
        if mode=='fix':print('fix result',s.fix(1e-7,1e-7,1e-5),flush=True)
        if mode=='refine':s=s.removeSplitter()
        if mode=='sew':
            shell=Part.makeShell(s.Faces);s=Part.makeSolid(shell);s.fix(1e-7,1e-7,1e-5)
        print(name,mode,'volume',s.Volume,'valid',s.isValid(),'closed',s.isClosed(),flush=True)
        for point in [A.Vector(-240,0,119),A.Vector(-180,0,117),A.Vector(-150,0,140)]:
            print(' inside',list(point),s.isInside(point,1e-6,True),flush=True)
        for a,b in [(s,optic),(optic,s)]:
            common=a.common(b,1e-5)
            print(' optics',common.isValid(),common.Volume,'operand volumes',s.Volume,optic.Volume,flush=True)
