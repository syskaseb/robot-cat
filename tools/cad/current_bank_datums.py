"""Read bank world datums from the CURRENT placed solids, never old origins.

Housing/ATO solids are project nominal envelopes, not measured part profiles.
Their placement is nevertheless authoritative for their own assembly frame.
"""
import re
import json
import hashlib
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part


def bounds(shape):
    b=shape.BoundBox
    return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]


def datums(targets):
    slots={}
    for name,shape in targets.items():
        match=re.fullmatch(r'(F_([LR])([1-6])_CP2)_(Housing|ATO|IN|OUT)(?:/.*)?',name)
        if not match:continue
        key,side,index,kind=match.groups();slot=slots.setdefault(key,dict(id=key,side=side,index=int(index),parts={}))
        if kind in slot['parts']:
            assert slot['parts'][kind]['bounds_mm']==bounds(shape),('Inconsistent bank aliases',name)
        slot['parts'][kind]=dict(name=name,bounds_mm=bounds(shape))
    assert len(slots)==12,'Need all12 placed bank components'
    rows=[]
    for key,r in sorted(slots.items()):
        assert set(r['parts'])=={'Housing','ATO','IN','OUT'},key
        h=r['parts']['Housing']['bounds_mm'];a=r['parts']['ATO']['bounds_mm']
        centre=[(h[0]+h[3])/2,(h[1]+h[4])/2]
        assert abs((a[0]+a[3])/2-centre[0])<1e-6 and abs((a[1]+a[4])/2-centre[1])<1e-6
        assert abs(a[2]-h[5])<1e-6,'Nominal inserted fuse flange datum changed'
        r.update(centre_xy_mm=centre,flange_top_z_mm=h[5],
                 placement_basis='Current placed Housing/ATO world BReps; one placement only',
                 geometry_basis='Existing project nominal envelopes, not measured inserted fuse or holder taper',
                 previous_wrong_centre_y_mm=58 if r['side']=='L' else -58)
        rows.append(r)
    return rows


def nominal_sweep(row,travel_mm=35):
    assert travel_mm>0
    a=row['parts']['ATO']['bounds_mm'];x,y,z,X,Y,Z=a
    return Part.makeBox(X-x,Y-y,Z-z+travel_mm,A.Vector(x,y,z))


def run():
    # Read just48 bank solids, not all2665 objects or cached Boolean results.
    # Inputs to this placement proof must match the current pinned scene.
    from plan_current_harness_interfaces import ROOT,OUT,SHA
    tick=time.monotonic();source=OUT/'remaining25-space-context.zip';targets={}
    with zipfile.ZipFile(source) as z:
        index=json.loads(z.read('index.json'));pins=dict(index['source_sha256'])
        for name,digest in pins.items():assert SHA(ROOT/name)==digest,name
        for r in index['entries']:
            if r['kind']!='target' or not re.fullmatch(r'F_[LR][1-6]_CP2_(Housing|ATO|IN|OUT)(?:/.*)?',r['name']):continue
            s=Part.Shape();s.importBrepFromString(z.read(r['file']).decode());targets[r['name']]=s
    rows=datums(targets)
    pins.update({f.relative_to(ROOT).as_posix():SHA(f) for f in (source,Path(__file__))})
    result=dict(status='TWELVE_BANK_PLACED_WORLD_DATUMS_VERIFIED_NOT_RETENTION_OR_SERVICE',
        rows=rows,part_count=len(targets),source_sha256=pins,
        correction='Old fixture/service templates usedoriginY+/-58 instead of placedcentreY+/-62. No purchased part or wire moved.',
        invalidated_claim='6c20adb33-pair map is NOT installed fuse withdrawal proof.',
        open=['Correctly placed fixture and installed service material checks',
              'Actual delivered engagement/tool/force and print fit',
              'Native rooted bank/whole assembly/stock'],
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,M4_complete=False,physical_pass=False)
    (OUT/'bank-current-world-datums.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(holders=len(rows),parts=len(targets),
        centre_Y_mm=sorted({r['centre_xy_mm'][1] for r in rows}),worker_seconds=result['worker_seconds'])))


if __name__=='__main__':run()
