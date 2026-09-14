import zipfile, os, xml.etree.ElementTree as ET, numpy as np
from OCP.BRepTools import BRepTools
from OCP.BRep import BRep_Builder, BRep_Tool
from OCP.TopoDS import TopoDS_Shape, TopoDS
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopLoc import TopLoc_Location
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib

SRC = '/tmp/claude-0/v17/src'
PIVOT_X = 21.0
def flip(p): return (2*PIVOT_X - p[0], -p[1], p[2])

def shapefiles():
    root = ET.parse(os.path.join(SRC,'Document.xml')).getroot()
    od = root.find('ObjectData'); n2f = {}
    for o in od.findall('Object'):
        for p in o.iter('Property'):
            if p.get('name') == 'Shape':
                pt = p.find('.//Part')
                if pt is not None and pt.get('file'): n2f[o.get('name')] = pt.get('file')
    return n2f

def load(name, n2f=None):
    n2f = n2f or shapefiles()
    sh = TopoDS_Shape(); b = BRep_Builder()
    BRepTools.Read_s(sh, os.path.join(SRC, n2f[name]), b)
    return sh

def tris(shape, defl=2.0):
    BRepMesh_IncrementalMesh(shape, defl, False, 0.5, True)
    out=[]; exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        f = TopoDS.Face(exp.Current()); loc = TopLoc_Location()
        tr = BRep_Tool.Triangulation_s(f, loc)
        if tr is not None:
            t = loc.Transformation()
            pts=[]
            for i in range(1, tr.NbNodes()+1):
                p = tr.Node(i).Transformed(t); pts.append((p.X(),p.Y(),p.Z()))
            for i in range(1, tr.NbTriangles()+1):
                a,b_,c = tr.Triangle(i).Get(); out.append((pts[a-1],pts[b_-1],pts[c-1]))
        exp.Next()
    return out

def bbox(shape):
    bb = Bnd_Box(); BRepBndLib.Add_s(shape, bb)
    return (bb.CornerMin().X(), bb.CornerMax().X(), bb.CornerMin().Y(),
            bb.CornerMax().Y(), bb.CornerMin().Z(), bb.CornerMax().Z())

def gbbox(name, n2f=None):
    """globalny bbox po odwroceniu nadbudowy"""
    xm,xM,ym,yM,zm,zM = bbox(load(name,n2f))
    return (2*PIVOT_X-xM, 2*PIVOT_X-xm, -yM, -ym, zm, zM)

# ---- ray casting na siatce trojkatow (szybkie, bez booleanow) ----
class Solid:
    def __init__(self, shape, defl=1.5, glob=True):
        t = np.array(tris(shape, defl), dtype=float)   # (N,3,3)
        if glob:
            t = t.copy()
            t[:,:,0] = 2*PIVOT_X - t[:,:,0]
            t[:,:,1] = -t[:,:,1]
        self.v0 = t[:,0]; self.e1 = t[:,1]-t[:,0]; self.e2 = t[:,2]-t[:,0]
    def crossings(self, orig, direc):
        d = np.asarray(direc, dtype=float)
        o = np.asarray(orig, dtype=float)
        pv = np.cross(d, self.e2)
        det = np.einsum('ij,ij->i', self.e1, pv)
        ok = np.abs(det) > 1e-12
        inv = np.zeros_like(det); inv[ok] = 1.0/det[ok]
        tv = o - self.v0
        u = np.einsum('ij,ij->i', tv, pv) * inv
        qv = np.cross(tv, self.e1)
        v = np.einsum('j,ij->i', d, qv) * inv
        tt = np.einsum('ij,ij->i', self.e2, qv) * inv
        hit = ok & (u >= -1e-9) & (v >= -1e-9) & (u+v <= 1+1e-9) & (tt > 1e-6)
        return int(hit.sum())
    def in_cavity(self, p):
        up = self.crossings(p, (0,0,1))
        if up % 2 == 1 or up < 2: return False
        for d in ((0,1,0),(0,-1,0)):
            c = self.crossings(p, d)
            if c % 2 == 1 or c < 2: return False
        return True
    def in_material(self, p):
        return self.crossings(p, (0,0,1)) % 2 == 1
