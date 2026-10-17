"""Only new foot/root/hardware interfaces; reuse unchanged36pose column proof."""
import json,time,subprocess
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import MODEL,BASE,OUT,STAGES
from build_feline_interior_candidate import transform
from check_feline_leg_body import placement
from check_feline_shared_space import tube_prefix


def main():
    tick=time.monotonic();reader=SavedShapes()
    manifestfile=OUT/'belly-feet-native.json';m=json.loads(manifestfile.read_text());native=ROOT/m['native']
    assert m['status']=='FOUR_EDITABLE_FEET_NATIVE_SHARED_FIT_OPEN' and sha(native)==m['native_sha256']
    plan=json.loads((OUT/'module-layout.json').read_text());motion=json.loads((OUT/'motion-layout.json').read_text())
    oldproof=OUT/'leg-body-path.json';old=json.loads(oldproof.read_text())
    assert old['status']=='SAMPLED_EXTERNAL_LEG_PAD_PATH_CLEAR_SUPPLIER_JOINTS_WIRING_SHELL_OPEN'
    reusefile=OUT/'motion-pad-reuse.json';reuse=json.loads(reusefile.read_text())
    padrel=(OUT/'FelineLayoutEnvelope.FCStd').relative_to(ROOT).as_posix()
    assert reuse['status']=='UNCHANGED_FOUR_PAD_BREPS_PROVE_REUSE_OF_SAMPLED_LEG_P0_PAD_RESULT'
    assert reuse['original_native_sha256']==old['source_sha256'][padrel]
    assert reuse['updated_native_sha256']==sha(ROOT/padrel)
    assert reuse['motion_report_sha256']==sha(oldproof)
    for n,h in old['source_sha256'].items():
        if n!=padrel:assert sha(ROOT/n)==h,n
    oldmotion=json.loads(subprocess.run(['git','show','1621e77:'+(OUT/'motion-layout.json').relative_to(ROOT).as_posix()],cwd=ROOT,check=True,capture_output=True).stdout)
    assert oldmotion==motion,'Do not reuse a different lying trajectory'
    changes={};added={};report=dict(status='FEET_SHARED_FIT_RUNNING',selected=False,physical_pass=False,
        contacts=[],errors=[],wire_clearance=[],seat_contacts=[],poses=[],pairs=0,
        reused_old_leg_pad_pairs=old['pairs'],reused_old_poses=len(old['poses']),
        reused_scope='Unchanged old cylindrical column occupied material and old8hardware; only positive added roots/hardware rechecked across all36poses',
        continuous_motion=False,load_qualified=False,closed_skin_tool_path_qualified=False)
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3)
        report['source_sha256']={**reader.hashes,**{p.relative_to(ROOT).as_posix():sha(p) for p in
            (manifestfile,oldproof,reusefile,OUT/'motion-layout.json',OUT/'module-layout.json',OUT/'prefix-allocation.json',OUT/'factory-routes.json',Path(__file__))}}
        (OUT/'belly-feet-fit.json').write_text(json.dumps(report,indent=2)+'\n')
    for i,row in enumerate(m['parts'],1):
        name=row['object'];s=reader.shape(native,name);oldpad=reader.shape(OUT/'FelineLayoutEnvelope.FCStd','BellyPadReservation'+str(i))
        changes[name]=s;added[name]=s.cut(oldpad)
        assert added[name].isValid() and abs(added[name].Volume+s.common(oldpad).Volume-s.Volume)<1e-4
    replaced={r['replaces'] for r in m['hardware']}
    for row in m['hardware']:
        n=row['object'];s=reader.shape(native,n);previous=reader.shape(MODEL,row['replaces']);changes[n]=s;added[n]=s.cut(previous)
        assert added[n].isValid()
    scene={}
    for g in plan['groups']:
        t=transform(g)
        for n in g['objects']:
            substitute=plan['reference_substitutions'].get(n)
            if substitute:
                s=reader.shape(ROOT/substitute['source'],substitute['object']);s.translate(A.Vector(*substitute['world_shift_before_head_drop_mm']))
            else:s=reader.shape(MODEL,n)
            override=plan.get('part_pose_overrides',{}).get(n)
            if override:s.Placement=transform(override)*s.Placement
            if not t.isIdentity():
                if t.Rotation.isIdentity():s.translate(t.Base)
                else:s.Placement=t*s.Placement
            scene[n]=s
    moving={n for g in motion['membership'].values() for ns in g.values() for n in ns}
    for r in motion['inventory']:
        n=r['object']
        if n in moving or n in scene or n in replaced or r['kind']!='surface':continue
        if r['label'].startswith(('P0_','tail/')) or n.startswith(('Print_P0_','Print_CP2_TailRiser','Battery')):scene[n]=reader.shape(MODEL,n)
    bounds_cache={n:s.BoundBox for n,s in {**scene,**changes}.items()}
    added_bounds={n:s.BoundBox for n,s in added.items()}
    def shape_bounds(name,s):
        if name not in bounds_cache:bounds_cache[name]=s.BoundBox
        return bounds_cache[name]
    def check(an,a,bn,b,scope,gap=0,ba=None,bb=None):
        if ba is None:ba=shape_bounds(an,a)
        if bb is None:bb=shape_bounds(bn,b)
        separation=sum(max(0,x-y,z-w)**2 for x,y,z,w in [(ba.XMin,bb.XMax,bb.XMin,ba.XMax),
            (ba.YMin,bb.YMax,bb.YMin,ba.YMax),(ba.ZMin,bb.ZMax,bb.ZMin,ba.ZMax)])
        if separation>gap*gap:return
        report['pairs']+=1
        try:
            c=a.common(b)
            if not c.isNull() and not c.isValid():raise ValueError('Invalid intersection')
            if c.Volume>1e-5:report['contacts'].append(dict(a=an,b=bn,scope=scope,volume_mm3=c.Volume))
            elif gap and a.distToShape(b)[0]<gap-1e-5:report['wire_clearance'].append(dict(a=an,b=bn,scope=scope,required_mm=gap))
        except Exception as e:report['errors'].append(dict(a=an,b=bn,scope=scope,error=str(e)))
    save()
    for n,s in changes.items():
        for bn,b in scene.items():check(n,s,bn,b,'fixed_material')
        for bn,b in changes.items():
            if bn>n:check(n,s,bn,b,'new_assembly')
    # Real frame seat area, not a bounding-box or assumed load path.
    for row in m['parts']:
        x,y,_=row['pad_center_mm'];seat=Part.makeBox(18,22,.05,A.Vector(x-9,27 if y>0 else -49,-2));contacts=[]
        for n,s in scene.items():
            if 'P0_Side' not in n or not seat.BoundBox.intersect(s.BoundBox):continue
            c=seat.common(s);assert c.isNull() or c.isValid()
            if c.Volume>1e-5:contacts.append(dict(frame=n,nominal_contact_area_mm2=c.Volume/.05))
        report['seat_contacts'].append(dict(foot=row['object'],frames=contacts))
        if not contacts:report['errors'].append(dict(foot=row['object'],error='No actual frame seat material witnessed'))
    # Actual chosen61 approach pipes and8 full factory pipes.
    prefixes=json.loads((OUT/'prefix-allocation.json').read_text());factory=json.loads((OUT/'factory-routes.json').read_text())
    assert prefixes['status']=='COUPLED_KNOWN_PREFIXES_CLEAR_FULL_WIRING_OPEN'
    for receipt in (prefixes,factory):
        assert receipt['source_sha256'][(OUT/'module-layout.json').relative_to(ROOT).as_posix()]==sha(OUT/'module-layout.json')
    specs={r['id']:r for r in prefixes['specifications']};wires={}
    for key,k in prefixes['allocation'].items():
        r=specs[key];bend=next(c['bend'] for c in prefixes['domains'][key] if c['option']==k)
        wires[key]=tube_prefix(r['point'],r['direction'],r['radius'],bend,12.4)
    for row in factory['routes']:
        edges=[]
        for p in row['parts']:
            a,b=A.Vector(*p['start']),A.Vector(*p['end'])
            edges.append(Part.makeLine(a,b) if p['kind']=='line' else Part.Arc(a,A.Vector(*p['mid']),b).toShape())
        w=Part.Wire(edges);e=w.Edges[0];p=e.valueAt(e.FirstParameter);d=e.tangentAt(e.FirstParameter)
        wires['Factory:'+row['wire']]=w.makePipeShell([Part.Wire([Part.makeCircle(row['radius_mm'],p,d)])],True,False)
    for n,s in changes.items():
        for wn,w in wires.items():check(n,s,wn,w,'known_wire_scope',1.25)
    axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']
    sources={n:reader.shape(MODEL,n) for n in moving}
    for index,pose in enumerate(motion['poses'][:36]):
        before=report['pairs']
        for code,g in motion['membership'].items():
            aa=[next(a for a in axes if a['code']==code and a['stage']==stage) for stage in STAGES]
            tf=placement(aa,pose['legs'][code]['angles_delta_degrees'])
            for stage,names in g.items():
                for n in names:
                    s=sources[n].copy();s.Placement=tf[stage]*s.Placement;posed_bound=s.BoundBox
                    for cn,c in added.items():check(cn,c,n,s,'added_material_pose'+str(index),ba=added_bounds[cn],bb=posed_bound)
        report['poses'].append(dict(index=index,pairs=report['pairs']-before));save()
        print('Added feet pose',index,'contacts',len(report['contacts']),flush=True)
    report['status']='FOUR_FEET_SHARED_FIT_CLEAR_LOAD_PRINT_SKIN_OPEN' if not any(report[k] for k in ('contacts','errors','wire_clearance')) else 'FEET_SHARED_FIT_REJECTED'
    save();print(json.dumps({k:report[k] for k in ('status','pairs','contacts','errors','wire_clearance','worker_seconds')}),flush=True)


if __name__=='__main__':main()
