"""Receive a joint macro proposal against ALL current real material.

Positive sampled witnesses only reject. Every surviving edge uses the exact
distance gate. No native mutation; old positive routes remain pinned inputs.
"""
import json,time,math,hashlib,subprocess
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from current_mixed_receiver_material import prepare,material
from plan_body36_receiver_space import P,C
from plan_axial_source_supports import arm_box
from shared_body36_macro_routes import plan,CHANGED
from check_body_fanout_material import mate_names,terminal_trim
from positive_material_witness import witness
from csg_bore_clearance import prove
from current_work_guard import check as guard

def run(parent_commit=None,material_only=False):
    guard();tick=time.monotonic();basefile=P.OUT/'body36-recovery-layout.json';base=json.loads(basefile.read_text())
    for n,h in base['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    inherited=None;parent=None
    if parent_commit:
        path=(P.OUT/'body36-shared-macro-layout.json').relative_to(P.ROOT).as_posix()
        raw=subprocess.check_output(['git','show',parent_commit+':'+path],cwd=P.ROOT);parent=json.loads(raw)
        mutable={Path(__file__).relative_to(P.ROOT).as_posix(),Path(__file__).with_name('revise_shared_body36_routes.py').relative_to(P.ROOT).as_posix()}
        for n,h in parent['source_sha256'].items():
            actual=hashlib.sha256(subprocess.check_output(['git','show',parent_commit+':'+n],cwd=P.ROOT)).hexdigest() if n in mutable else P.SHA(P.ROOT/n)
            assert actual==h,('Inherited proof input changed',n)
        from revise_shared_body36_routes import plan as revise
        rows,candidates,failures=revise(parent,base,material_only=material_only)
        inherited=dict(git_commit=parent_commit,receipt=path,sha256=hashlib.sha256(raw).hexdigest(),
            source_pins_verified=True,qualified_routes=list(parent['qualified_changed_routes']))
    else:rows,candidates,failures=plan({r['wire']:r for r in base['rows']})
    targets,old,pins,grips=prepare();analytic={};group_for={}
    for name,g in grips['groups'].items():
        profile,components=material(g);group_for.update({w:name for w in g['wires']})
        for kind,s in components.items():
            key='Group_'+name+'/'+kind;targets[key]=s
            if g['kind']=='triple' and kind in ('body','cap'):analytic[key]=(profile['recipe'],kind)
    rf=P.OUT/'body36-receiver-support-reservations.json';roots=json.loads(rf.read_text())
    for n,h in roots['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    for r in roots['groups']:
        for path in r['paths']:
            for i,(a,b) in enumerate(zip(path['points_mm'],path['points_mm'][1:])):
                targets['ReceiverRoot/'+r['name']+'/'+r['wire']+'/'+str(i)]=arm_box(a,b,r['arm_half_widths_world_mm'])
    for n in list(old):
        if n.startswith('body/'):old.pop(n)
    retained={n:r for n,r in base['routes'].items() if n not in CHANGED}
    received=parent['qualified_changed_routes'] if parent else {}
    old.update({'body/'+n:(P.wire(r['parts']),1) for n,r in retained.items()})
    old.update({'body/'+n:(P.wire(r['parts']),1) for n,r in received.items()})
    for n in ('W013','W047','W069'):
        row=rows[n];old['fan/'+row['loom']+'/'+row['core']]=(P.wire(row['source_parts']),1)
    files=[basefile,rf,Path(__file__),Path(__file__).with_name('shared_body36_macro_routes.py'),Path(__file__).with_name('positive_material_witness.py')]
    if parent:files.append(Path(__file__).with_name('revise_shared_body36_routes.py'))
    if material_only:files.append(Path(__file__).with_name('received_curve_splice.py'))
    pins.update(base['source_sha256']);pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files})
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'body36-shared-macro-pairs.json',bounds.near)
    points={};edge_cache={};checks=0;completed=dict(received);attempts=[];last=time.monotonic()
    def save():
        out=dict(status='PARTIAL_SHARED_MACRO_ARCHITECTURE_NOT_SELECTED',changed_rows=[rows[n] for n in CHANGED],
            inherited_receipt=basefile.relative_to(P.ROOT).as_posix(),
            inherited_qualified_receipt=inherited,
            proposed_routes=candidates,math_failures=failures,retained_route_ids=sorted(retained),qualified_changed_routes=completed,
            attempts=attempts,remaining_wire_ids=sorted(set(rows)-set(retained)-set(completed)),changed_pairs=checks,
            source_sha256=pins,worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False,
            scope='JointFL1+FR1replace3oldpositivecores explicitly;27otherwholecurves retained. Allcurrent36/19guides/receiverroots/sourcearms/motionincluded. No native change or phasepoint.')
        f=P.OUT/'body36-shared-macro-layout.json';tmp=f.with_suffix('.tmp');tmp.write_text(json.dumps(out,indent=2)+'\n');tmp.replace(f);cache.save()
    def samples(s):
        if id(s) not in points:points[id(s)]=np.asarray([list(v) for e in s.Edges for v in e.discretize(Distance=.75)])
        return points[id(s)]
    save()
    for name,q in candidates.items():
        guard();row=rows[name];parts=q['parts'];whole=P.wire(parts);mouth=P.wire(terminal_trim(parts))
        source=row.get('source_parts',[row['source_land']]);after=P.wire(row.get('source_after_jacket_first5_mm',source[1:])+parts[len(source):])
        contacts=[];errors=[]
        def hit(s,target,t,rs=1.25,rt=0):
            nonlocal checks,last
            if not bounds.near(s,t,rs+rt+.0001):return False
            if target in analytic and not rt and prove(*analytic[target],s,rs):return False
            checks+=1
            try:
                if rt:
                    a,b=samples(s),samples(t)
                    for p in a:
                        ix=np.all(np.abs(b-p)<rs+rt,axis=1)
                        if ix.any():
                            ds=np.linalg.norm(b[ix]-p,axis=1);j=int(np.argmin(ds))
                            if ds[j]<rs+rt-1e-6:
                                contacts.append(dict(target=target,gap_upper_bound_mm=float(ds[j]),required_mm=rs+rt,positive_exact_curve_points_mm=[p.tolist(),b[ix][j].tolist()]));return True
                else:
                    inside=witness(s,t,bounds,points)
                    if inside is not None:
                        contacts.append(dict(target=target,gap_mm=0,required_mm=rs,positive_exact_solid_witness_mm=inside));return True
                # Distance to a union of actual edges is exactly their minimum;
                # splitting avoids a pathological whole-compound OCC solve.
                left=list(s.Edges);right=list(t.Edges) if rt else [t]
                for a in left:
                    for b in right:
                        if not bounds.near(a,b,rs+rt+.0001):continue
                        gap,volume=cache.check(a,b,rs,rt)
                        if volume>1e-5 or gap<rs+rt-1e-6:
                            contacts.append(dict(target=target,gap_mm=gap,required_mm=rs+rt,volume_mm3=volume));return True
            except (RuntimeError,AssertionError,ValueError) as e:errors.append(dict(target=target,error=str(e)));return True
            if time.monotonic()-last>20:save();guard();last=time.monotonic()
            return False
        # Reject actual wire crossings cheaply before any expensive solid solve.
        for target,(t,r) in old.items():
            if target=='fan/'+row['loom']+'/'+row['core']:continue
            own=target.startswith('leg/'+row['loom']+'/') or target.startswith('chosen/'+row['loom']+'/')
            if hit(after if own else whole,target,t,rt=r):break
        if not contacts and not errors:
            for target,t in targets.items():
                if target.startswith('Group_'+group_for[name]+'/band'):
                    land=row['receiving_parts'][row['receiving_grip_part_index']]
                    if hit(P.wire([land]),target+'/land',t,1):break
                    other=Part.makeCompound([P.wire([p]) for p in parts if p!=land])
                    if hit(other,target+'/rest',t):break
                elif hit(mouth if target.split('/')[0] in mate_names(row) else whole,target,t):break
        attempts.append(dict(wire=name,architecture=q['architecture'],contacts=contacts,errors=errors))
        if not contacts and not errors:completed[name]=q;old['body/'+name]=(whole,1)
        save();print('shared macro',name,'qualified',name in completed,'first',contacts[:1],errors[:1],flush=True)
    save()

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--resume-commit');p.add_argument('--material-only',action='store_true');a=p.parse_args();run(a.resume_commit,a.material_only)
