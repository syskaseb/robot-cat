"""Only two NEW design-wire solids against saved E6; no previous box rerun."""
import hashlib,json
from pathlib import Path
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/aux-splice-shelf-r2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def overlaps(a,b):return a.XMax>b.XMin and b.XMax>a.XMin and a.YMax>b.YMin and b.YMax>a.YMin and a.ZMax>b.ZMin and b.ZMax>a.ZMin
def main():
    targets={}
    files={}
    for name in ('factory16AWG_DESIGN','HELU23502_DESIGN'):
        p=OUT/(name+'.brep');s=Part.Shape();s.read(str(p));assert s.isValid() and len(s.Solids)==1
        targets[name]=s;files[name]=sha(p)
    assembly=ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd'
    d=A.openDocument(str(assembly));hits={}
    try:
        for name,s in targets.items():
            hits[name]=[]
            for o in d.Objects:
                if not hasattr(o,'Shape') or o.Shape.isNull() or not overlaps(o.Shape.BoundBox,s.BoundBox):continue
                for i,solid in enumerate(o.Shape.Solids):
                    if not overlaps(solid.BoundBox,s.BoundBox):continue
                    v=sum(q.Volume for q in solid.common(s).Solids)
                    if v>1e-5:hits[name].append({'object':o.Name,'solid':i,'mm3':v})
            print(name,len(hits[name]),flush=True)
    finally:A.closeDocument(d.Name)
    result={'assembly_sha256':sha(assembly),'design_brep_sha256':files,'positive_hits':hits,
            'nominal_clear':all(not v for v in hits.values()),'physical_pass':False,
            'scope':'two exact S-bend design pipes, assumed factory exit/OD; no actual pin or full upstream route qualification'}
    (OUT/'wire-e6.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
