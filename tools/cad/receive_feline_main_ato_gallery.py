"""Whole MAIN fan across the measured gap BETWEEN two ATO tool corridors.

Rigidly retain the locally accepted PCB/M2/insulation/grip kit. Rebuild only
its common root, outside the tie hoop, with a below-ATO foot to the same bed.
"""
import gzip,hashlib,json,os,sys,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from receive_feline_rrp_shared_height import load
from receive_feline_main_supported_unit import intrinsic,local_inputs,cylinder,BOARD,BED
from feline_channelled_foundation import bearing_area
from feline_solid_distance import bbox_lower_bound
from feline_fore_power_pair import SolidQueries
from receive_feline_underplate_return_gallery import minimum_for
from feline_atomic_save import save_json


def selected(file,field,wanted,prefix=''):
    d=json.loads(file.read_text());arc=ROOT/d['bundle'];assert sha(arc)==d['bundle_sha256'];parts={};rows={}
    with zipfile.ZipFile(arc) as z:
        for r in d[field]:
            n=prefix+r['name']
            if not wanted(n):continue
            raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());assert s.isValid() and s.Solids
            parts[n]=s;rows[n]=r
    return parts,rows,{p.relative_to(ROOT).as_posix():sha(p) for p in (file,arc)}


def proposal():
    f=OUT/'n01-MAIN-supported-unit.json';parent=json.loads(f.read_text())
    assert parent['status']=='MAIN_WHOLE_UNIT_HOLDS' and len(parent['failures'])==16
    for p,h in parent['source_sha256'].items():assert sha(ROOT/p)==h,p
    actors=load(parent);kinds={r['name']:r for r in parent['geometry']}
    origin=A.Vector(-20,-76,0);centre=A.Vector(-28.549,-78.9,0);rot=A.Rotation(A.Vector(0,0,1),90)
    tf=A.Placement(centre-rot.multVec(origin),rot)
    oldroot=actors.pop('MainSupported:root')
    upper=oldroot.common(Part.makeBox(100,100,30,A.Vector(-70,-120,91.15)))
    assert upper.isValid() and len(upper.Solids)==1
    upper.Placement=tf*upper.Placement
    for s in actors.values():s.Placement=tf*s.Placement
    post=[-23,-93,95.25];foot=[-23,-93,53.5];bed=[-23,-78.5,53.5]
    root=upper.fuse(cylinder(foot,post,2)).fuse(cylinder(foot,bed,1.5))
    target=tf.multVec(A.Vector(-29.271,-72.25,95.25));start=A.Vector(*post)
    root=root.fuse(cylinder(start,target,1.5)).fuse(Part.makeSphere(1.5,target))
    z=min(s.BoundBox.ZMin for n,s in actors.items() if n.endswith(':jacket'))
    tip=[-24.5,-86.4,z+8]
    root=root.fuse(cylinder([-23,-93,z+8],tip,1.25)).fuse(Part.makeSphere(1.25,A.Vector(*tip))).removeSplitter()
    assert root.isValid() and len(root.Solids)==1
    actors['MainSupported:root']=root
    assert root.common(actors['MainSupported:comb']).Volume>1
    original,pins=local_inputs();assert root.common(original[BED]).Volume>10
    recipes={}
    for e,r in parent['recipes'].items():
        q=dict(r)
        for key in ('source_pad_mm','jacket_start_mm','routing_exit_mm'):q[key]=list(tf.multVec(A.Vector(*r[key])))
        q['routing_exit_axis']=list(tf.Rotation.multVec(A.Vector(*r['routing_exit_axis'])))
        q['source_neck_parts']=[dict(p,**{k:list(tf.multVec(A.Vector(*p[k]))) for k in ('start','mid','end') if k in p}) for p in r['source_neck_parts']]
        recipes[e]=q
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (f,ROOT/parent['bundle'],Path(__file__))})
    return actors,kinds,recipes,parent,original,pins


def main():
    tick=time.monotonic();actors,kinds,recipes,parent,original,pins=proposal()
    checks=intrinsic(actors,original,kinds);root=actors['MainSupported:root']
    for i in (0,1):
        w=actors[f'Ref_Material_MAIN_{i}_lower_washer_0_0'];area=bearing_area(root,w,91.25)
        checks['fork_washer_bearing:'+str(i)]=dict(ok=area>10,area_mm2=area)
    area=bearing_area(root,actors[BOARD],99.25);checks['fork_PCB_bearing']=dict(ok=area>20,area_mm2=area)
    checks['root_to_bed']=dict(ok=root.common(original[BED]).Volume>10,positive_union_mm3=root.common(original[BED]).Volume)
    neighbours={};meta={}
    for file,field,want,prefix in [
        ('n01-full-material-scene.json','parts',lambda n:n.startswith('Ref_Material_F_R') and ('_ATO_' in n or '_Housing_' in n),''),
        ('n01-shared54-current.json','parts',lambda n:n.startswith('Service:Ref_Material_F_R'),''),
        ('n01-shared-Pi-carrier-r3-core-received.json','geometry',lambda n:n=='SharedPi:Carrier','')]:
        p,r,pp=selected(OUT/file,field,want,prefix);neighbours.update(p);meta.update(r);pins.update(pp)
    query=SolidQueries()
    for n,s in actors.items():
        for m,t in neighbours.items():
            gap=minimum_for(n,kinds[n],m,meta[m])
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=gap:continue
            d=query.distance(s,t);checks[n+'|'+m]=dict(ok=d>=gap-1e-6,gap_mm=d,minimum_mm=gap)
    stem=OUT/'n01-MAIN-ATO-gallery-local';arc=stem.with_suffix('.breps.zip');pf=stem.with_suffix('.pairs.json.gz')
    geometry=[]
    with zipfile.ZipFile(arc,'w',zipfile.ZIP_DEFLATED) as z:
        for i,(n,s) in enumerate(actors.items()):
            raw=s.exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw)
            geometry.append(dict(kinds[n],name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
    r=dict(status='MAIN_ATO_GALLERY_LOCAL_HOLDS' if any(not v['ok'] for v in checks.values()) else 'MAIN_ATO_GALLERY_LOCAL_RECEIVED_WORLD_OPEN',
        source_sha256=pins,geometry=geometry,bundle=arc.relative_to(ROOT).as_posix(),bundle_sha256=sha(arc),
        pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf),checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],
        recipes=recipes,retired=parent['retired'],measured_ATO_tool_gap_X_mm=[-29,-17],full_band_width_mm=8.3,
        selected_full_band_X_mm=[-27.15,-18.85],tool_to_band_lower_bound_mm=1.85,below_ATO_foot_axis_Z_mm=53.5,
        worker_seconds=round(time.monotonic()-tick,3),N01_complete=False,physical_pass=False,native_changed=False)
    save_json(stem.with_suffix('.json'),r);print(r['status'],r['worker_seconds'],len(r['failures']),flush=True)
    print(json.dumps({k:v for k,v in checks.items() if not v['ok']},indent=2),flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
