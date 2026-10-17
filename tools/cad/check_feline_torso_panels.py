"""Actual new torso-wall interfaces, known wires and full sampled lying path.

First add the4 planned foot passages to the native dependency tree. Then
collect all actual wall contacts for one shared leg/control/access redesign.
No per-contact micro-notches, no physical/continuous/wiring-completeness PASS.
"""
import json,time
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT,STAGES
from check_feline_leg_body import placement
from check_feline_shared_space import tube_prefix


def main():
    tick=time.monotonic();reader=SavedShapes();mp=OUT/'torso-panels-native.json'
    m=json.loads(mp.read_text());native=ROOT/m['native'];before=sha(native)
    assert before==m['native_sha256'] and m['status']=='FOUR_EDITABLE_TORSO_PANEL_CANDIDATES_CHANGED_INTERFACES_OPEN'
    feet=json.loads((OUT/'belly-feet-native.json').read_text())
    assert feet['external_fit_complete']
    d=A.openDocument(str(native));doc_name=d.Name
    try:
        assert not d.getObject('FootPassages'),'Receive existing modified native before another cut'
        p=d.Parameters;p.set('A4','FootPassageRadius');p.set('B4','11 mm');p.setAlias('B4','FootPassageRadius')
        tools=[]
        for i,row in enumerate(feet['parts'],1):
            x,y,_=row['pad_center_mm'];ob=d.addObject('Part::Cylinder',f'FootPassage{i}')
            ob.Placement.Base=A.Vector(x,y,-50);ob.Height=7;ob.setExpression('Radius','Parameters.FootPassageRadius');tools.append(ob)
        union=d.addObject('Part::MultiFuse','FootPassages');union.Shapes=tools
        cut=d.addObject('Part::Cut','ShellWithFootPassages');cut.Base=d.ShellWall;cut.Tool=union
        for r in m['parts']:d.getObject(r['object']).Base=cut
        d.recompute();original={r['object']:d.getObject(r['object']).Shape.Volume for r in m['parts']}
        assert all(d.getObject(n).Shape.isValid() and len(d.getObject(n).Shape.Solids)==1 for n in original)
        p.set('B4','11.5 mm');d.recompute()
        assert all(d.getObject(n).Shape.Volume<v for n,v in original.items())
        p.set('B4','11 mm');d.recompute()
        assert all(abs(d.getObject(n).Shape.Volume-v)<1e-4 for n,v in original.items())
        d.save();m.update(native_sha256=sha(native),foot_passages=4,foot_hole_diameter_mm=22,
            foot_passage_radius_test_mm=[11,11.5,11],prior_native_sha256=before,
            passage_modifier=Path(__file__).relative_to(ROOT).as_posix())
        for r in m['parts']:r['volume_mm3']=original[r['object']]
        mp.write_text(json.dumps(m,indent=2)+'\n')
    finally:A.closeDocument(doc_name)
    interior=json.loads((OUT/'interior-native-checks.json').read_text());current=ROOT/interior['native']
    assert sha(current)==interior['native_sha256']
    plan=json.loads((OUT/'module-layout.json').read_text());motion=json.loads((OUT/'motion-layout.json').read_text())
    names=[n for g in plan['groups'] for n in g['objects']]
    names += [n for n in reader.doc(current) if n.startswith(('Print_P0_','Print_CP2_TailRiser','Battery','Ref_Material_P0_','Ref_Material_tail_','BellyFoot','FrameHardwareNew')) and n not in names]
    scene={n:reader.shape(current,n) for n in names}
    head=set(next(g['objects'] for g in plan['groups'] if g['role']=='HeadMechanism'))
    leg={n for g in motion['membership'].values() for ns in g.values() for n in ns};assert leg.issubset(scene)
    static={n:s for n,s in scene.items() if n not in leg and n not in head}
    panels={r['object']:reader.shape(native,r['object']) for r in m['parts']}
    report=dict(status='NEW_WALL_INTERFACES_RUNNING',selected=False,physical_pass=False,
        contacts=[],clearance_failures=[],errors=[],pairs=0,leg_poses=[],head_poses=[],
        native=native.relative_to(ROOT).as_posix(),native_sha256=sha(native),
        full_wiring_complete=False,continuous_motion=False,feet_passages=4,
        material_scope='All retained/current material,9conservative head poses,36legposes,8MTAfactorypieces and61endapproaches. Full new wiring/mounts/skin closures are OPEN.',
        source_sha256={current.relative_to(ROOT).as_posix():sha(current),
            (OUT/'module-layout.json').relative_to(ROOT).as_posix():sha(OUT/'module-layout.json'),
            (OUT/'motion-layout.json').relative_to(ROOT).as_posix():sha(OUT/'motion-layout.json'),
            mp.relative_to(ROOT).as_posix():sha(mp),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))})
    dest=OUT/'torso-panel-interfaces.json';bounds={n:s.BoundBox for n,s in {**panels,**scene}.items()}
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3);dest.write_text(json.dumps(report,indent=2)+'\n')
    def check(pn,p,n,s,scope,pose=None,gap=0,bs=None):
        ba=bounds[pn];bb=bounds[n] if bs is None else bs
        separation=sum(max(0,a-b,c-d)**2 for a,b,c,d in [(ba.XMin,bb.XMax,bb.XMin,ba.XMax),(ba.YMin,bb.YMax,bb.YMin,ba.YMax),(ba.ZMin,bb.ZMax,bb.ZMin,ba.ZMax)])
        if separation>gap*gap:return
        report['pairs']+=1
        try:
            c=p.common(s)
            if not c.isNull() and not c.isValid():raise ValueError('Invalid exact intersection')
            if c.Volume>1e-5:
                b=c.BoundBox;report['contacts'].append(dict(panel=pn,object=n,scope=scope,pose=pose,volume_mm3=c.Volume,
                    conservative_witness_box_for_design_only_mm=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]))
            elif gap:
                distance=p.distToShape(s)[0]
                if distance<gap-1e-5:report['clearance_failures'].append(dict(panel=pn,object=n,scope=scope,gap_mm=distance,required_mm=gap))
        except Exception as exc:report['errors'].append(dict(panel=pn,object=n,scope=scope,error=str(exc)))
    save()
    for pn,p in panels.items():
        for n,s in static.items():check(pn,p,n,s,'fixed_material')
        save();print('Panel fixed',pn,'hits',len(report['contacts']),flush=True)
    specs=json.loads((OUT/'prefix-allocation.json').read_text());factory=json.loads((OUT/'factory-routes.json').read_text())
    for receipt in (specs,factory):assert receipt['source_sha256'][(OUT/'module-layout.json').relative_to(ROOT).as_posix()]==sha(OUT/'module-layout.json')
    rows={r['id']:r for r in specs['specifications']};wires={}
    for key,k in specs['allocation'].items():
        r=rows[key];bend=next(c['bend'] for c in specs['domains'][key] if c['option']==k)
        wires[key]=tube_prefix(r['point'],r['direction'],r['radius'],bend,12.4)
    for row in factory['routes']:
        edges=[]
        for e in row['parts']:
            a,b=A.Vector(*e['start']),A.Vector(*e['end']);edges.append(Part.makeLine(a,b) if e['kind']=='line' else Part.Arc(a,A.Vector(*e['mid']),b).toShape())
        w=Part.Wire(edges);e=w.Edges[0];p=e.valueAt(e.FirstParameter);t=e.tangentAt(e.FirstParameter)
        wires['Factory:'+row['wire']]=w.makePipeShell([Part.Wire([Part.makeCircle(row['radius_mm'],p,t)])],True,False)
    for pn,p in panels.items():
        for n,s in wires.items():check(pn,p,n,s,'known_wire_scope',gap=1.25,bs=s.BoundBox)
    save();print('Panel known wires complete',flush=True)
    axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']
    for i,pose in enumerate(motion['poses'][:36]):
        count=report['pairs']
        for code,g in motion['membership'].items():
            aa=[next(a for a in axes if a['code']==code and a['stage']==stage) for stage in STAGES];tf=placement(aa,pose['legs'][code]['angles_delta_degrees'])
            for stage,ns in g.items():
                for n in ns:
                    s=scene[n].copy();s.Placement=tf[stage]*s.Placement;b=s.BoundBox
                    for pn,p in panels.items():check(pn,p,n,s,'leg_motion',i,bs=b)
        report['leg_poses'].append(dict(index=i,pairs=report['pairs']-count));save()
        print('Panel leg pose',i,'hits',len(report['contacts']),flush=True)
    for pitch in (-10,0,5):
        for yaw in (-15,0,15):
            for n in head:
                s=scene[n].copy()
                if pitch:s.rotate(A.Vector(*plan['head_pitch_axis_mm']),A.Vector(0,1,0),pitch)
                if yaw:s.rotate(A.Vector(*plan['head_yaw_axis_mm']),A.Vector(0,0,1),yaw)
                b=s.BoundBox
                for pn,p in panels.items():check(pn,p,n,s,'head_conservative_union',[pitch,yaw],bs=b)
            report['head_poses'].append([pitch,yaw]);save()
    report['source_sha256'].update(reader.hashes)
    report.update(status='NEW_WALL_CONTACTS_REQUIRE_SHARED_ACCESS_REDESIGN' if any(report[k] for k in ('contacts','clearance_failures','errors')) else 'SAMPLED_NEW_WALL_INTERFACES_CLEAR_MOUNTS_SERVICE_WIRING_OPEN')
    save();print(json.dumps({k:report[k] for k in ('status','pairs','worker_seconds')}),flush=True)


if __name__=='__main__':main()
