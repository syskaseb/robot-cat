"""Replace only W024 middle after the shared grip/prefix allocation.

Cheap mesh screening proposes a path; an exact changed-wire gate decides it.
The nineteen inherited routes are not rerouted or re-audited. Historical
body-fanout-layout and native models stay unchanged until whole selection.
"""
import argparse,copy,gc,json,math,time
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
import core_receiver_port as T
import check_near_axis_hip_sources as C
import plan_body_fanout_layout as R
from check_body_fanout_material import mate_names,terminal_trim
P=C.P


def run(shorter_departure=False):
    tick=time.monotonic();pf=P.OUT/'receiver-relief-approach-plan.json';bf=P.OUT/'body-fanout-layout.json';sf=P.OUT/'body-fanout-scene.json'
    prefix,prior,scene_receipt=[json.loads(f.read_text()) for f in (pf,bf,sf)]
    assert prefix['status']=='JOINT20_RECEIVER_GRIPS_AND_W024_PREFIX_CLEAR_MIDDLE_ROOT_ARMS_NATIVE_OPEN'
    for receipt in (prefix,scene_receipt):
        for n,h in receipt['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    oldgate=P.OUT/'independent-body-routes-material.json';inherited=json.loads(oldgate.read_text())
    assert not inherited['contacts'] and not inherited['errors'] and len(inherited['completed_routes'])==20
    assert inherited['source_sha256'][bf.relative_to(P.ROOT).as_posix()]==P.SHA(bf)
    profiles={}
    for name,q in prefix['grips'].items():
        profiles[name]=T.build(q['land'],q['normal'],q['offset'])
        goal=profiles[name]['arrival_world_mm'];profiles[name]['seed']=P.box([v-2 for v in goal]+[v+2 for v in goal])
    chosen=prefix['grips']['W024'];row=copy.deepcopy(chosen['row']);variant_index=None
    if shorter_departure:
        options=[(i,q) for i,q in enumerate(prefix['W024_options']) if
                 q['land']==chosen['land'] and q['normal']==chosen['normal'] and q['offset']==chosen['offset']]
        assert options,'No unchanged-grip alternate departure'
        variant_index,q=min(options,key=lambda iq:math.dist(iq[1]['row']['free_end'],row['free_start']))
        row=copy.deepcopy(q['row'])
        print('same20grips, changed departure',row['receiver_outward_axis'],row['free_end'],flush=True)
    known={tuple(np.round(p,7)) for part in [*row['receiving_parts'],row['source_land']] for p in R.part_points(part)}
    class GripScene(R.Scene):
        def __init__(self,data):super().__init__(data);self.grip_memo={}
        def clear(self,points,r):
            for p in points:
                key=tuple(np.round(p,7))
                if key in known:continue # Only the pinned exact prefix/source5mm samples.
                if not super().clear(np.asarray([p]),r):return False
                if key not in self.grip_memo:
                    okay=True
                    for name,profile in profiles.items():
                        for kind in ('body','band','seed'):
                            s=profile[kind];bb=s.BoundBox
                            if any(v<lo-1.25 or v>hi+1.25 for v,lo,hi in zip(p,(bb.XMin,bb.YMin,bb.ZMin),(bb.XMax,bb.YMax,bb.ZMax))):continue
                            if Part.Vertex(A.Vector(*p)).distToShape(s)[0]<1.25-1e-6:okay=False;break
                        if not okay:break
                    self.grip_memo[key]=okay
                if not self.grip_memo[key]:return False
            return True
    mesh=P.ROOT/scene_receipt['scene'];assert P.SHA(mesh)==scene_receipt['sha256']
    with np.load(mesh,allow_pickle=False) as archive:scene=GripScene(archive)
    for name,r in prior['routes'].items():
        if name!='W024':scene.add_points('new/'+name,np.concatenate([R.part_points(p) for p in r['parts']]))
    result,points=R.corridor(scene,row,backward=True)
    if points is None:result,points=R.corridor(scene,row,backward=False)
    print('receiver middle planning',bool(points is not None),result,flush=True)
    blocked=scene.blockers;del scene;gc.collect()
    candidate=copy.deepcopy(prior);candidate['routes']=dict(prior['routes'])
    candidate['rows']=[row if r['wire']=='W024' else r for r in prior['rows']]
    candidate.update(source_sha256={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in (pf,bf,sf,oldgate,Path(__file__),Path(T.__file__),Path(R.__file__))},
        inherited_routes=[n for n in prior['routes'] if n!='W024'],inherited_material_gate=oldgate.relative_to(P.ROOT).as_posix(),
        status='RECEIVER_MIDDLE_ROUTE_OPEN',qualified_prefix_variant_index=variant_index,
        printed20grip_geometry_unchanged=True,selected=False,W5_complete=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    out=P.OUT/'body-receiver-relief-layout.json'
    if points is None:
        candidate['routes'].pop('W024',None)
        candidate.update(route_failure=result,blocker_counts=blocked);out.write_text(json.dumps(candidate,indent=2)+'\n');return
    candidate['routes']['W024']=result
    out.write_text(json.dumps(candidate,indent=2)+'\n')
    targets,old,pins=C.load();rows={r['wire']:r for r in candidate['rows']}
    parts=result['parts'];whole=P.wire(parts);mouth=P.wire(terminal_trim(parts));after_source=P.wire(parts[1:]);mates=mate_names(row)
    for name,r in prior['routes'].items():
        if name!='W024':old['body/'+name]=(P.wire(r['parts']),1)
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'receiver-relief-middle-pairs.json',bounds.near)
    contacts=[];errors=[];checks=0
    def check(name,wire,target,rs=1.25,rt=0):
        nonlocal checks
        if not bounds.near(wire,target,rs+rt+.0001):return
        checks+=1
        try:
            gap,volume=cache.check(wire,target,rs,rt)
            if volume>1e-5 or gap<rs+rt-1e-6:contacts.append(dict(target=name,gap_mm=gap,required_mm=rs+rt))
        except (AssertionError,ValueError) as e:errors.append(dict(target=name,error=str(e)))
        if checks%50==0:cache.save()
    for name,s in targets.items():check(name,mouth if name.split('/')[0] in mates else whole,s)
    for name,(w,radius) in old.items():check(name,after_source if name.startswith('leg/'+row['loom']+'/') else whole,w,rt=radius)
    landpart=row['receiving_parts'][row['receiving_grip_part_index']]
    nonland=Part.makeCompound([P.wire([p]) for p in parts if p!=landpart])
    for name,profile in profiles.items():
        for kind in ('body','band','seed'):
            if name=='W024' and kind=='band':
                check(name+'/'+kind+'/ownland',P.wire([landpart]),profile[kind],1)
                check(name+'/'+kind+'/rest',nonland,profile[kind])
            else:check(name+'/'+kind,whole,profile[kind])
    candidate.update(status='BODY20_ROUTES_AND_RECEIVER_GRIPS_EXACT_CHANGED_WIRE_CLEAR_ROOT_ARMS_NATIVE_OPEN' if not contacts and not errors else 'REJECTED_RECEIVER_RELIEF_MIDDLE',
        contacts=contacts,errors=errors,changed_wire='W024',changed_pairs=checks,
        unchanged_routes_exact_material_reused=19,receiver_grips=20,
        worker_seconds=round(time.monotonic()-tick,3),
        source_sha256={**candidate['source_sha256'],**pins},
        scope='ChangedcompleteW024vsfullretainedmaterial/wires/19bodycurves/20jointgrips. Original19routesreusepinnedmaterialproof; all20gripsreusejointprefixproof. Whole4newHip1sources/rootarms/native/stockW5OPEN.')
    tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(candidate,indent=2)+'\n');tmp.replace(out);cache.save()
    print(json.dumps({k:candidate[k] for k in ('status','changed_pairs','worker_seconds','contacts','errors')}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--shorter-departure',action='store_true')
    run(parser.parse_args().shorter_departure)
