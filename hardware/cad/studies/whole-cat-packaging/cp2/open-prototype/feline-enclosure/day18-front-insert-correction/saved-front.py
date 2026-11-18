"""Read only requested world-positioned BReps from the saved FreeCAD file."""
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Shape
from OCP.BRepTools import BRepTools
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.TopAbs import TopAbs_IN
from OCP.gp import gp_Pnt
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
import numpy as np

class Saved:
    def __init__(self,filename):
        self.zip=ZipFile(BytesIO(Path(filename).read_bytes()))
        doc=ElementTree.fromstring(self.zip.read("Document.xml"))
        self.members={}
        for obj in doc.findall("./ObjectData/Object"):
            ref=obj.find('./Properties/Property[@name="Shape"]/Part')
            if ref is not None and ref.get("file"):
                self.members[obj.get("name")]=ref.get("file")
        self.shapes={}
        self.boxes={}
        self.classifiers={}
        # The stored BRep already carries the world transform. This independent
        # source STEP datum catches an accidental second application of Placement.
        assert np.allclose(self.bounds("VL53L5CX"),[-208.566,-6.35,94,-206,6.35,111.78],atol=1e-4)
    def shape(self,n):
        if n not in self.shapes:
            s=TopoDS_Shape()
            BRepTools.Read_s(s,BytesIO(self.zip.read(self.members[n])),BRep_Builder())
            self.shapes[n]=s
        return self.shapes[n]
    def bounds(self,n):
        if n not in self.boxes:
            b=Bnd_Box()
            BRepBndLib.AddOptimal_s(self.shape(n),b,False,False)
            self.boxes[n]=np.array([*b.CornerMin().Coord(),*b.CornerMax().Coord()])
        return self.boxes[n]
    def inside(self,n,positions):
        b=self.bounds(n)
        pts=np.asarray(positions)
        ids=np.flatnonzero(np.all((pts>=b[:3])&(pts<=b[3:]),axis=1))
        if len(ids) and n not in self.classifiers:
            self.classifiers[n]=BRepClass3d_SolidClassifier(self.shape(n))
        for i in ids:
            self.classifiers[n].Perform(gp_Pnt(*pts[i]),1e-6)
            if self.classifiers[n].State()==TopAbs_IN:
                return int(i)
        return None
    def common(self,a,b):
        u,v=self.bounds(a),self.bounds(b)
        lower=np.linalg.norm(np.maximum(0,np.maximum(u[:3]-v[3:],v[:3]-u[3:])))
        if lower>1e-5:return {"bounds_separation_mm":float(lower)}
        op=BRepAlgoAPI_Common(self.shape(a),self.shape(b))
        if not op.IsDone():return {"error":"intersection unresolved"}
        g=GProp_GProps()
        BRepGProp.VolumeProperties_s(op.Shape(),g)
        return {"common_mm3":g.Mass()}
