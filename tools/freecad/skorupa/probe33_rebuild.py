"""Read-only candidate repair study, no source or assembly changes."""
from pathlib import Path
import FreeCAD as A
import Part,MeshPart
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'hardware/skorupa/v33/shape-cache/mesh-proof'
s=Part.Shape();s.read(str(ROOT/'hardware/skorupa/v31/shape-cache/HeadFront.brep'))
def check(name,c):
    if c.isNull():print(name,'NULL',flush=True);return
    print(name,c.isValid(),len(c.Solids),c.Volume,flush=True)
    c.exportBrep(str(OUT/(name+'.brep')))
    m=MeshPart.meshFromShape(Shape=c,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
    m.write(str(OUT/(name+'.stl')))
    print(name,'mesh_solid',m.isSolid(),'far_inside',c.isInside(A.Vector(-240,0,119),1e-6,True),flush=True)
central=[]
for f in s.Faces:
    b=f.BoundBox
    if b.XMax<-189 and b.YMin>=-12.501 and b.YMax<=12.501 and b.ZMin>=103.99 and b.ZMax<=122.751:
        central.append(f)
print('central',len(central),flush=True)
for mode in ['defeature','gfa','remove_internal']:
    try:
        if mode=='defeature':c=s.defeaturing(central)
        elif mode=='gfa':c=s.generalFuse([],1e-5)[0]
        else:
            c=s.copy();c.removeInternalWires(0)
        check(mode,c)
    except Exception as e:print(mode,repr(e),flush=True)
