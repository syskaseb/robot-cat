"""Shared changed-source gate. Exact retained subsets, never whole-owner hiding.

Checks all four new factory approaches/flexes/eight seats and bands together
against full retained material, other eight source families and twenty body
routes. Root arms, breakouts, native/stock and continuous sweeps remain OPEN.
"""
import copy,json,time,zipfile,hashlib,inspect
from pathlib import Path
import FreeCAD as A
import Part
import current_body_fanout_material as M
import build_complete_source_carriers as B
import build_remaining_loom_supports as G
from whole_current_body_material import load
from compact_loom_land_port import build as port_build
from build_front_fixed_port_clearance import placement
from diagnose_remaining_support_endpoints import transform,moved
from check_low_hip_shared_space import ownership,AtomicMaterial,same_leg_pose
from immutable_bounds import ImmutableBounds
from plan_continuous_joint_family import self_screen
P=M.P
ANGLES=(-15,0,15)


def retained_hip_parents(targets,family,roots):
    """Reconstruct retained original recipes, removing ONLY Hip1-owned branches."""
    names=[r['physical_leg']+'HipExtension' for r in family['hips'] if r['loom'].endswith('1')]
    inputs=[P.OUT/n for n in ('complete-source-carriers-plan.json','source-carrier-port-bridges-material.json','front-fixed-port-clearance.json','remaining-support-shared-material.json','leg-source-near-member-plan.json')]
    inputs += [Path(B.__file__),Path(G.__file__),Path(__file__).with_name('loom_land_port.py'),Path(__file__).with_name('compact_loom_land_port.py'),Path(__file__).with_name('support_entry_port.py')]
    contract=dict(inputs={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in inputs},
        parents={name:hashlib.sha256(targets[name+'/0/0'].exportBrepToString().encode()).hexdigest() for name in names},
        helper_sha256=hashlib.sha256(inspect.getsource(retained_hip_parents).encode()).hexdigest())
    key=hashlib.sha256(json.dumps(contract,sort_keys=True).encode()).hexdigest()
    folder=P.OUT/'near-axis-retained-cache'/key;folder.mkdir(parents=True,exist_ok=True)
    manifest=folder/'manifest.json';saved=json.loads(manifest.read_text()) if manifest.exists() else dict(contract=contract,parts={})
    assert saved['contract']==contract
    cached={};receipts=[]
    for name,row in saved['parts'].items():
        file=folder/row['file'];assert P.SHA(file)==row['sha256']
        s=Part.Shape();s.read(str(file));assert s.isValid() and len(s.Solids)==1,name
        cached[name]=s;receipts.append(row['receipt'])
    if set(cached)==set(names):
        print('received cached exact retained Hip subsets4',flush=True)
        return cached,receipts,inputs+[manifest,*[folder/r['file'] for r in saved['parts'].values()]]
    pf=P.OUT/'complete-source-carriers-plan.json';plan=json.loads(pf.read_text())
    original_plan=copy.deepcopy(plan)
    plan=copy.deepcopy(plan);kept_family=copy.deepcopy(family)
    kept_family['hips']=[r for r in kept_family['hips'] if not r['loom'].endswith('1')]
    for root in plan['roots']:root['paths']=[p for p in root['paths'] if not p['loom'].endswith('1')]
    nominal={n.split('/')[0]:s for n,s in targets.items() if n.endswith('/0/0') or n.endswith('/0/0/0')}
    zf=P.ROOT/'hardware/simulation/v35/inputs.zip'
    with zipfile.ZipFile(zf) as z:members=json.loads(z.read('geometry.json'))['components']
    shapes,_,_,_=B.allocation(plan,kept_family,nominal,members)
    bridge_file=P.OUT/'source-carrier-port-bridges-material.json'
    bridge=json.loads(bridge_file.read_text())
    # These are the ACTUAL later below-band bridges, not the obsolete first
    # carrier allocation. Omitting sibling bridges invalidates preservation.
    for name,recipe in bridge['recipes'].items():
        for pad in recipe['pads']:
            if 'BelowBandBridge' in pad['name'] and not pad['name'].split('BelowBandBridge')[0].endswith('1'):
                shapes[name]=shapes[name].fuse(P.box(pad['bounds_mm'])).removeSplitter()
        for cut in recipe['cuts']:shapes[name]=shapes[name].cut(P.box(cut)).removeSplitter()
        for ring in recipe['ring_cuts']:
            shapes[name]=shapes[name].cut(P.box(ring['outer']).cut(P.box(ring['inner']))).removeSplitter()
    cf=P.OUT/'front-fixed-port-clearance.json';cuts=json.loads(cf.read_text())
    for row in cuts['rows']:
        for cut in row['cutters']:
            tool=P.box(cut['world_fixed_box_mm']);tool.Placement=placement(cut['fixed_to_owner'])*tool.Placement
            shapes[row['part']]=shapes[row['part']].cut(tool).removeSplitter()
    ef=P.OUT/'remaining-support-shared-material.json';extra=json.loads(ef.read_text())
    kept=dict(cached)
    for row in family['hips']:
        if not row['loom'].endswith('1'):continue
        owner=row['physical_leg']+'HipExtension';recipe=extra['recipes'][owner]
        if owner in cached:continue
        s=shapes[recipe['preserved_owner']].copy()
        for pad in recipe['pads']:s=s.fuse(G.oriented(pad['bounds_mm'],pad.get('placement'))).removeSplitter()
        for cut in recipe['cuts']:s=s.cut(G.oriented(cut['bounds_mm'],cut.get('placement'))).removeSplitter()
        assert s.isValid() and len(s.Solids)==1 and not s.check(True),owner
        previous=targets[owner+'/0/0']
        raw_outside=s.cut(previous).Volume
        # The saved native has additional inherited reliefs. Intersect the
        # recipe subset with that exact native, then prove every removed bit
        # belongs to the obsolete Hip1 branch/post. No sibling material waiver.
        s=previous.common(s).removeSplitter()
        root=next(r for r in original_plan['roots'] if r['leg']==row['physical_leg'])
        path=next(p for p in root['paths'] if p['loom']==row['loom'])
        owned=[]
        for a,b in zip(path['points_mm'],path['points_mm'][1:]):
            owned.append(P.box([min(a[j],b[j])-h for j,h in enumerate((2,3,2))]+[max(a[j],b[j])+h for j,h in enumerate((2,3,2))]))
        xx,yy,zz=row['moving_anchor_rest_world_mm'];sign=-1 if row['physical_leg'].startswith('Front') else 1
        x,X=sorted((xx+sign*4,xx+sign*8));owned.append(P.box([x,yy-3,zz-9,X,yy+3,zz]))
        for pad in bridge['recipes'][row['physical_leg']+'SourceCarrier']['pads']:
            if pad['name'].startswith(row['loom']+'BelowBandBridge'):owned.append(P.box(pad['bounds_mm']))
        removal=Part.makeCompound(owned)
        lost=previous.cut(s)
        unrelated=lost.cut(removal).Volume
        assert unrelated<1e-5,(owner,'Would remove unrelated retained material',unrelated)
        assert s.isValid() and len(s.Solids)==1 and not s.check(True),owner
        outside=s.cut(previous).Volume
        assert outside<1e-5,(owner,'Retained geometry exceeds original',outside)
        kept[owner]=s;receipts.append(dict(owner=owner,outside_original_mm3=outside,
            inherited_reliefs_reapplied_mm3=raw_outside,removed_outside_owned_Hip1_mm3=unrelated,
            retained='CaseCap/other2sourcebranches/posts andbothKneeFixedbranches; onlyHip1branch/post removed'))
        file=folder/(owner+'.brep');s.exportBrep(str(file))
        saved['parts'][owner]=dict(file=file.name,sha256=P.SHA(file),receipt=receipts[-1])
        tmp=manifest.with_suffix('.tmp');tmp.write_text(json.dumps(saved,indent=2)+'\n');tmp.replace(manifest)
        print('checkpoint retained Hip subset',owner,'parts',len(saved['parts']),flush=True)
    return kept,receipts,inputs+[manifest,*[folder/r['file'] for r in saved['parts'].values()]]


def run(math_name='body-near-axis-hip-plan.json',report_name='body-near-axis-source-space.json'):
    assert Path(math_name).name==math_name and Path(report_name).name==report_name
    tick=time.monotonic();mf=P.OUT/math_name;plan=json.loads(mf.read_text())
    assert not plan['rejected'] and len(plan['hips'])==4
    for n,h in plan['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    targets,old,pins=load();ff=P.OUT/'leg-source-near-member-plan.json';family=json.loads(ff.read_text())
    rf=P.OUT/'remaining-loom-roots-plan.json';roots=json.loads(rf.read_text())
    af=P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(af.read_text())['axes']
    kept,subset_receipts,files=retained_hip_parents(targets,family,roots)
    for row in plan['hips']:
        owner=row['physical_leg']+'HipExtension'
        for h in ANGLES:targets[owner+f'/{h}/0']=moved(kept[owner],transform(axes,row['cad_code'],h,0,'Hip'))
        for n in list(targets):
            if n.startswith(row['loom']+'IndependentBand/'):targets.pop(n)
        old={n:s for n,s in old.items() if not n.startswith('leg/'+row['loom']+'/')}
    # Received fixed-frame subsets preserve both sibling port/arm recipes.
    sf=P.OUT/'body-low-hip-retention-plan.json';fixed=json.loads(sf.read_text());archive=P.ROOT/fixed['archive']
    assert P.SHA(archive)==fixed['archive_sha256']
    with zipfile.ZipFile(archive) as z:
        index=json.loads(z.read('index.json'))
        for row in fixed['retained']:
            item=next(r for r in index if r['name']=='Retained_'+row['owner'])
            s=Part.Shape();s.importBrepFromString(z.read(item['file']).decode())
            assert s.cut(targets[row['owner']+'/0/0']).Volume<1e-5,row['owner']
            targets[row['owner']+'/0/0']=s
    for row in plan['hips']:assert targets.pop('Band_'+row['loom']+'/Hip/Fixed/0/0') is not None
    own,bare=ownership(targets,family,roots)
    bf=P.OUT/'body-fanout-layout.json'
    for n,r in json.loads(bf.read_text())['routes'].items():old['body/'+n]=(P.wire(r['parts']),1)
    new={};new_owners={};curve_info={};curves={};ground=[];contacts=[];errors=[];completed=[];pairs=0
    for row in plan['hips']:
        loom=row['loom'];code=row['cad_code'];normal=[1,0,0] if row['physical_leg'].startswith('Front') else [-1,0,0]
        for moving_flag,key in ((False,'fixed_lands'),(True,'moving_lands')):
            part=row[key][0]['parts'][0];axis=[(b-a)/9 for a,b in zip(part['start'],part['end'])]
            land=dict(start_world_mm=part['start'],end_world_mm=part['end'],centre_world_mm=[(a+b)/2 for a,b in zip(part['start'],part['end'])],axis=axis,length_mm=9)
            port=port_build(land,normal)
            for kind in ('body','band'):
                for h in ANGLES if moving_flag else (0,):
                    n=f'{loom}/{"Moving" if moving_flag else "Fixed"}/{kind}/{h}'
                    new[n]=moved(port[kind],transform(axes,code,h,0,'Hip')) if moving_flag else port[kind]
                    new_owners[n]=(code,h) if moving_flag else None
        for pose in row['poses']:
            parts=pose['parts']+B.moved_parts(row['source_parts'],row['source'],pose['angle'],0,axes)
            witness=self_screen(parts)
            if witness:contacts.append(dict(a=loom+'/'+str(pose['angle']),b='ownnonlocalwire',witness=witness))
            curve=P.wire(parts);gap=curve.BoundBox.ZMin-3-(-168.319012764516)
            ground.append(dict(loom=loom,angle=pose['angle'],nominal_ground_gap_mm=gap))
            if pose['angle'] in ANGLES:
                n=loom+'/'+str(pose['angle']);curves[n]=curve;curve_info[n]=(code,pose['angle'],loom)
    bounds=ImmutableBounds();cache=AtomicMaterial(P.OUT/'near-axis-source-pairs.json',bounds.near);last_save=time.monotonic()
    def save():
        status='REJECTED_NEAR_AXIS_SHARED_SOURCE' if contacts or errors or min(r['nominal_ground_gap_mm'] for r in ground)<0 else 'NEAR_AXIS_SOURCE_SAMPLED_CLEAR_ARMS_BREAKOUTS_NATIVE_OPEN'
        result=dict(status=status,pairs=pairs,contacts=contacts,errors=errors,completed=completed,
            retained_subset_receipts=subset_receipts,ground=ground,material_instances=len(targets),
            changed_source_curves=len(curves),changed_port_pose_shapes=len(new),body_routes=20,
            scope='Four complete new factoryapproach+Hip1flex families,8seats/bands; fullretainedassembly/other8families/20bodyroutes. CoupledHip samples-15/0/+15,124ground/selfchecks. Arms/corebreakouts/native/stock/continuoussweep OPEN.',
            source_sha256={**pins,**{f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in [mf,ff,rf,af,bf,sf,archive,*files,Path(__file__)]}},
            computed_pairs=cache.computed,reused_pairs=cache.reused,worker_seconds=round(time.monotonic()-tick,3),
            selected=False,W5_complete=False,physical_pass=False)
        out=P.OUT/report_name;tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(out);cache.save();return result
    def check(n,s,m,t,rs=0,rt=0):
        nonlocal pairs,last_save
        if not bounds.near(s,t,rs+rt+.0001):return
        pairs+=1
        try:
            gap,vol=cache.check(s,t,rs,rt)
            if vol>1e-5 or ((rs or rt) and gap<rs+rt-1e-6):contacts.append(dict(a=n,b=m,gap_mm=gap,required_mm=rs+rt,volume_mm3=vol))
        except (AssertionError,ValueError) as e:errors.append(dict(a=n,b=m,error=str(e)))
        if time.monotonic()-last_save>20:
            save();last_save=time.monotonic();print('nearaxis gate',n,'pairs',pairs,'contacts',len(contacts),flush=True)
    for n,curve in curves.items():
        code,h,loom=curve_info[n]
        for m,s in targets.items():
            if same_leg_pose(own.get(m),code,h):check(n,curve,m,s,3.25)
        for m,(wire,radius) in old.items():
            if m.startswith('leg/'):
                _,ol,oh,*_=m.split('/')
                oc=next(r['cad_code'] for r in family['hips'] if r['loom']==ol)
                if code==oc and int(oh)!=h:continue
            check(n,curve,m,wire,3.25,radius)
        for m,s in new.items():
            if same_leg_pose(new_owners[m],code,h):check(n,curve,m,s,3 if m.startswith(loom+'/') and '/band/' in m else 3.25)
        for m,wire in curves.items():
            if curve_info[m][2]!=loom and m<n:check(n,curve,m,wire,3.25,3)
        completed.append(n);save();print('received whole nearaxis',n,'pairs',pairs,'contacts',len(contacts),flush=True)
    names=list(new)
    for i,n in enumerate(names):
        code,h=new_owners[n] or (None,0)
        for m,s in targets.items():
            if code is None or same_leg_pose(own.get(m),code,h):check(n,new[n],m,s)
        for m,(wire,radius) in old.items():
            if m.startswith('leg/') and code:
                _,ol,oh,*_=m.split('/')
                oc=next(r['cad_code'] for r in family['hips'] if r['loom']==ol)
                if code==oc and int(oh)!=h:continue
            check(n,new[n],m,wire,0,radius+.25)
        for m in names[:i]:
            if code is None or same_leg_pose(new_owners[m],code,h):check(n,new[n],m,new[m])
        completed.append(n);save()
    result=save();print(json.dumps({k:result[k] for k in ('status','pairs','worker_seconds','computed_pairs','reused_pairs')}),flush=True)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--plan',default='body-near-axis-hip-plan.json')
    parser.add_argument('--output',default='body-near-axis-source-space.json');args=parser.parse_args()
    run(args.plan,args.output)
