"""Resolve four changed S1 source interfaces before whole service relocation.

Reads only named saved S1 BReps, not whole CAD/leg clouds. A guide endpoint
is not promoted to a manufacturer datum. No old placement checks rerun.
"""
import hashlib
import json
import math
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT


def plane_receipts(shapes,q,d):
    found=[]
    for name,s in shapes.items():
        assert s.isValid() and s.Solids
        for i,f in enumerate(s.Faces,1):
            if type(f.Surface).__name__!='Plane':continue
            normal=f.normalAt(0,0);normal.normalize()
            alignment=abs(normal.dot(d))
            if alignment<1-1e-6:continue
            c=f.CenterOfMass
            found.append(dict(part=name,face=i,centre_mm=list(c),normal=list(normal),
                centre_distance_mm=(c-q).Length,axis_alignment=alignment,area_mm2=f.Area))
    return sorted(found,key=lambda r:r['centre_distance_mm'])


def mouth_receipts(shapes,q,d):
    # Split annular mould-end faces have off-axis area centroids. The actual
    # criteria are plane coincidence AND a coaxial cylindrical source bore.
    planes=plane_receipts(shapes,q,d);axes={}
    for name,s in shapes.items():
        for i,f in enumerate(s.Faces,1):
            surface=f.Surface
            if type(surface).__name__!='Cylinder':continue
            direction=surface.Axis;direction.normalize()
            centre=surface.Center
            error=(q-centre).cross(direction).Length
            if abs(direction.dot(d))>=1-1e-6 and error<1e-4:
                axes.setdefault(name,[]).append(dict(face=i,radius_mm=surface.Radius,axis_error_mm=error))
    matches=[]
    for p in planes:
        error=abs((q-A.Vector(*p['centre_mm'])).dot(d))
        if error<1e-4 and p['part'] in axes:matches.append(dict(p,plane_offset_mm=error,coaxial_cylinder_faces=axes[p['part']]))
    return matches,planes


def main():
    tick=time.monotonic();files=[OUT/n for n in ('n01-full-material-scene.json','n01-lower-bay-world-probe.json',
        'n01-common-restraint-world-probe.json','n01-remaining-selected-inventory.json')]
    packet=OUT/'n01-current-endpoint-packet-r3.json';data=json.loads(packet.read_text());pins={p.relative_to(ROOT).as_posix():sha(p) for p in (*files,packet,Path(__file__))}
    records={}
    for p in files:
        doc=json.loads(p.read_text());bundle=ROOT/doc['bundle'];assert sha(bundle)==doc['bundle_sha256']
        pins[bundle.relative_to(ROOT).as_posix()]=sha(bundle)
        for r in doc['parts']:
            if r.get('role')=='S1' or 'current_S1_' in r['name']:records[r['name']]=(bundle,r)
    shapes={};source_rows=[]
    for name,(bundle,row) in records.items():
        with zipfile.ZipFile(bundle) as z:raw=z.read(row['entry'])
        assert hashlib.sha256(raw).hexdigest()==row['sha256']
        s=Part.Shape();s.importBrepFromString(raw.decode('utf-8'));assert s.isValid() and s.Solids
        shapes[name]=s;source_rows.append(dict(name=name,sha256=row['sha256'],world_bounds_mm=[[s.BoundBox.XMin,s.BoundBox.YMin,s.BoundBox.ZMin],[s.BoundBox.XMax,s.BoundBox.YMax,s.BoundBox.ZMax]]))
    assert shapes
    rings={n:s for n,s in shapes.items() if '_ring_' in n.lower()}
    ends=[e for e in data['endpoints'] if e['group']=='S1'];assert len(ends)==4
    receipts=[]
    for e in ends:
        q=A.Vector(*e['point_mm']);d=A.Vector(*e['departure_axis']);d.normalize()
        matches,planes=mouth_receipts(rings,q,d)
        receipts.append(dict(endpoint=e['id'],source_point_mm=list(q),source_departure=list(d),
            inherited_basis=e['basis'],inherited_actual_port_verified=e['actual_port_verified'],
            matching_nominal_source_planes=matches,nearest_aligned_ring_planes=planes[:4],
            status='SAVED_RING_END_PLANE_CONSISTENT_NOT_VENDOR_FIT' if matches else 'GUIDE_TO_SOURCE_RING_DATUM_HOLD'))
    result=dict(status='S1_SOURCE_DATUM_RECEIVED_BEFORE_WHOLE_RELOCATION',source_sha256=pins,source_parts=source_rows,
        receipts=receipts,nominal_source_matches=sum(bool(r['matching_nominal_source_planes']) for r in receipts),
        selected=False,N01_complete=False,physical_pass=False,supplier_mating_or_delivered_crimp_not_qualified=True,
        method='Coaxial cylindrical axis plus coincident axial end planes; split-face centroid is NOT the mouth',
        geometry_or_native_files_changed=False,worker_seconds=round(time.monotonic()-tick,3))
    dest=OUT/'n01-s1-current-source-datums.json'
    if dest.exists():
        old=json.loads(dest.read_text());assert old['nominal_source_matches']==0 and 'method' not in old
        result['superseded_nonbinding_centroid_method']=dict(old_matches=0,reason='Area centroid of split annular face need not lie on bore axis; no geometry changed')
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:result[k] for k in ('status','nominal_source_matches','worker_seconds')}),flush=True)


if __name__=='__main__':main()
