"""Receive grid result; qualify at most two shared-corridor proposals per gap.

No grid rerun or native mutation. Keep every fully checked positive route;
one current recovery receipt binds the immutable received grid evidence.
"""
import hashlib,json,subprocess,time
from pathlib import Path
import FreeCAD as A
import Part
from current_mixed_receiver_material import prepare,material
from plan_body36_receiver_space import P,C
from plan_axial_source_supports import arm_box
from parallel_core_candidates import proposals,west_north_return
from check_body_fanout_material import mate_names,terminal_trim
from csg_bore_clearance import prove
from positive_material_witness import witness


def run(resume_commit=None):
    tick=time.monotonic();basefile=P.OUT/'body36-current-layout.json';base=json.loads(basefile.read_text())
    assert not base['status'].startswith('PARTIAL_CURRENT_BODY36_MIDDLE_PLAN')
    assert not base['status'].startswith('PARTIAL_CURRENT_BODY36_EXACT_GATE')
    for n,h in base['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    targets,old,pins,grips=prepare();rows={r['wire']:r for r in base['rows']};analytic={};group_for={}
    for name,g in grips['groups'].items():
        p,components=material(g)
        group_for.update({w:name for w in g['wires']})
        for kind,s in components.items():
            key='Group_'+name+'/'+kind;targets[key]=s
            if g['kind']=='triple' and kind in ('body','cap'):analytic[key]=(p['recipe'],kind)
    rootfile=P.OUT/'body36-receiver-support-reservations.json';roots=json.loads(rootfile.read_text())
    for r in roots['groups']:
        for path in r['paths']:
            for i,(a,b) in enumerate(zip(path['points_mm'],path['points_mm'][1:])):
                targets['ReceiverRoot/'+r['name']+'/'+r['wire']+'/'+str(i)]=arm_box(a,b,r['arm_half_widths_world_mm'])
    for name in ('W013','W047','W069'):
        row=rows[name];old['fan/'+row['loom']+'/'+row['core']]=(P.wire(row['source_parts']),1)
    missing=set(base['route_failures'])|{q['wire'] for q in base['contacts']}|{q['wire'] for q in base['errors']}
    assert not (missing&set(base.get('replaced_wire_ids',[]))&set(base['routes'])-set(base['changed_wire_ids']))
    routes={n:r for n,r in base['routes'].items() if n not in missing}
    assert (set(routes)&set(base['changed_wire_ids']))<=set(base['completed_changed_routes']), 'Receive full exact gate before retaining positive grid routes'
    attempts=[];resumed=None
    if resume_commit:
        relative=(P.OUT/'body36-recovery-layout.json').relative_to(P.ROOT).as_posix()
        raw=subprocess.check_output(['git','show',resume_commit+':'+relative],cwd=P.ROOT)
        prior=json.loads(raw);script=Path(__file__).relative_to(P.ROOT).as_posix()
        oldcode=subprocess.check_output(['git','show',resume_commit+':'+script],cwd=P.ROOT)
        assert hashlib.sha256(oldcode).hexdigest()==prior['source_sha256'][script]
        for n,h in prior['source_sha256'].items():
            if n!=script:assert P.SHA(P.ROOT/n)==h,n
        routes=prior['routes'];attempts=prior['attempts'];missing=set(prior['remaining_wire_ids'])
        resumed=dict(commit=resume_commit,receipt_sha256=hashlib.sha256(raw).hexdigest(),
            old_script_sha256=prior['source_sha256'][script],scope='Prior exact candidates retained; negative short-circuit adds no acceptance shortcut.')
    for n in list(old):
        if n.startswith('body/'):old.pop(n)
    old.update({'body/'+n:(P.wire(r['parts']),1) for n,r in routes.items()})
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'body36-recovery-pairs.json',bounds.near)
    pairs=0;remaining=set(missing);sample_points={}
    files=[basefile,rootfile,P.OUT/'body36-exit-diagnosis.json',Path(__file__),Path(__file__).with_name('parallel_core_candidates.py'),Path(__file__).with_name('positive_material_witness.py')]
    exits=json.loads(files[2].read_text())
    pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files});pins.update(base['source_sha256'])
    def save():
        out=dict(status='CURRENT36_CURVES_AND_RECEIVER_GRIPS_EXACT_CLEAR_ROOT_ARMS_NATIVE_OPEN' if len(routes)==36 else 'PARTIAL_SHARED36_RECOVERY_OPEN',
            routes=routes,rows=list(rows.values()),remaining_wire_ids=sorted(remaining),attempts=attempts,
            contacts=[],errors=[],changed_pairs=pairs,source_sha256=pins,
            inherited_route_evidence=basefile.relative_to(P.ROOT).as_posix(),inherited_individually_exact_routes=sorted(set(routes)-missing),
            resumed_from=resumed,worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False)
        p=P.OUT/'body36-recovery-layout.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(out,indent=2)+'\n');tmp.replace(p);cache.save()
    for name in sorted(missing):
        row=rows[name];candidates=[]
        for donor,r in routes.items():
            if rows[donor]['loom']==row['loom'] and donor!=name:candidates.extend(proposals(row,rows[donor],r))
        if name=='W071':
            first=next(o['part'] for o in exits['exits'][name] if not o['contacts']);q=west_north_return(row,first)
            if q:candidates.append(q)
        candidates=sorted(candidates,key=lambda q:q['guide_mm'])[:2]
        tested={json.dumps(a['candidate'],sort_keys=True) for a in attempts if a.get('wire')==name and 'candidate' in a}
        for candidate in candidates:
            if json.dumps(candidate,sort_keys=True) in tested:continue
            contacts=[];errors=[];parts=candidate['parts'];whole=P.wire(parts);mouth=P.wire(terminal_trim(parts))
            source=row.get('source_parts',[row['source_land']]);after=P.wire(row.get('source_after_jacket_first5_mm',source[1:])+parts[len(source):])
            def check(s,target,t,rs=1.25,rt=0):
                nonlocal pairs
                if not bounds.near(s,t,rs+rt+.0001):return
                if target in analytic and prove(*analytic[target],s,rs):return
                pairs+=1
                try:
                    inside=witness(s,t,bounds,sample_points) if not rt else None
                    if inside is not None:
                        contacts.append(dict(target=target,gap_mm=0,required_mm=rs,positive_exact_solid_witness_mm=inside));return
                    gap,volume=cache.check(s,t,rs,rt)
                    if volume>1e-5 or gap<rs+rt-1e-6:contacts.append(dict(target=target,gap_mm=gap,required_mm=rs+rt,volume_mm3=volume))
                except (RuntimeError,AssertionError,ValueError) as e:errors.append(dict(target=target,error=str(e)))
            for target,t in targets.items():
                if contacts or errors:break
                if target.startswith('Group_'+group_for[name]+'/band'):
                    land=row['receiving_parts'][row['receiving_grip_part_index']]
                    check(P.wire([land]),target+'/land',t,1)
                    check(Part.makeCompound([P.wire([p]) for p in parts if p!=land]),target+'/rest',t)
                else:check(mouth if target.split('/')[0] in mate_names(row) else whole,target,t)
            for target,(t,r) in old.items():
                if contacts or errors:break
                if target=='fan/'+row['loom']+'/'+row['core']:continue
                own=target.startswith('leg/'+row['loom']+'/') or target.startswith('chosen/'+row['loom']+'/')
                check(after if own else whole,target,t,rt=r)
            attempts.append(dict(wire=name,candidate=candidate,contacts=contacts,errors=errors))
            if not contacts and not errors:
                routes[name]=candidate;old['body/'+name]=(whole,1);remaining.remove(name)
            save();print('shared recovery',name,'contacts',len(contacts),'errors',len(errors),'remaining',sorted(remaining),flush=True)
            if name not in remaining:break
        if not candidates:attempts.append(dict(wire=name,no_shared_candidate=True));save()
    save()


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--resume-commit');run(parser.parse_args().resume_commit)
