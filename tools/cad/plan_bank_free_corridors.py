"""Whole bank space allocation before detailing, not successive offset trials.

Map nominal installed parts AND outward ATO/jaw corridors together. Retain
purchased parts, moving geometry, P0 and current wire paths. Current printed
retention is recorded separately as redesign work, never silently erased from
an acceptance proof. This advisory is NOT native/service/W5 qualification.
"""
import json,math,time
from pathlib import Path
import FreeCAD as A
import Part
from remaining25_shared_context import load,P
from current_source_retention_context import C,same_parent
from plan_remaining25_restraint_space import profile
from plan_axial_source_supports import arm_box
from current_work_guard import check
from underdeck_bank_layout import layout
from current_bank_datums import bounds as shape_bounds


def run():
    check();tick=time.monotonic();targets,wires,pins,parents,grips=load()
    files=[P.OUT/(n+'.json') for n in ('body36-current-contract','remaining25-interface-allocation',
        'remaining25-restraint-space','remaining25-saddle-roots')]
    contract,allocation,saddles,roots=[json.loads(f.read_text()) for f in files]
    for receipt in (saddles,roots):
        for n,h in receipt['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    q=layout(targets,contract,allocation)
    ends={e['id'] for e in allocation['ends'] if e['wire'] in q['changed_wire_ids'] and e['role'].endswith('.in')}
    groups={g['id']:g for g in saddles['spatial_groups']}
    retired={gid for gid,g in groups.items() if any(e in ends for e in g['ends'])}
    assert len(retired)==12
    for gid,i in saddles['selected_options'].items():
        if gid in retired:continue
        rec=saddles['domains'][gid][i]['recipe'];s=profile(groups[gid],rec['normal'],rec['knot_sign'])
        assert s['recipe']==rec
        targets.update({'Remaining25/'+gid+'/'+k:s[k] for k in ('body','band')})
    for row in roots['groups']:
        if row['id'] in retired:continue
        for i,(a,b) in enumerate(zip(row['path'],row['path'][1:])):
            targets['CurrentSaddleRoot/'+row['owner']+'/'+row['id']+'/'+str(i)]=arm_box(a,b,roots['arm_half_widths_mm'])
    for n in q['retired_targets']:targets.pop(n)
    wires={n:v for n,v in wires.items() if n.rsplit('/',1)[-1] not in q['changed_wire_ids']}
    def redesignable(n):
        return n.startswith(('CurrentSaddleRoot/','Remaining25/','RetainedSourceLacing/')) or any(same_parent(o,n,grips) for o in parents)
    soft={n:s for n,s in targets.items() if redesignable(n)}
    hard={n:s for n,s in targets.items() if n not in soft and s.Solids}
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'bank-free-corridor-pairs.json',bounds.near)
    checks=0;rows=[];errors=[]
    for f in files+[Path(__file__),Path(__file__).with_name('underdeck_bank_layout.py')]:
        pins[f.relative_to(P.ROOT).as_posix()]=P.SHA(f)
    def save():
        data=dict(status='ADVISORY_SHARED_BANK_SPACE_MAP_NOT_SELECTION',candidates=rows,errors=errors,checks=checks,
            source_sha256=pins,worker_seconds=round(time.monotonic()-tick,3),
            retained_hard_targets=len(hard),redesignable_printed_targets=sorted(soft),
            superseded_wire_ids=sorted(q['changed_wire_ids']),superseded_saddle_ids=sorted(retired),
            basis='One dimensioned outward-side space map, Y80, X-90..150 step30, Z90/115/135. One actual four-part representative per side from the48part family,35mm ATO/projectjaw. All12 individual bindings and mutual slots remain OPEN; bbox only pair pruning. Printed retention contacts are explicit required redesign, not clearance.',
            open=['Select twelve noninterfering positions with full actual factory V length/radii and bank-input routes',
                  'Redesign each affected printed retention with intact load paths and existing supported interfaces',
                  'Panel/root/fastener/native/assembly/stock and physical delivered fit'],
            selected=False,W5_complete=False,M4_complete=False,physical_pass=False)
        out=P.OUT/'bank-free-corridors.json';tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(out);cache.save()
    def hit(a,b,r=0):
        nonlocal checks
        if not bounds.near(a,b,r+.0001):return None
        if r and not b.Solids and len(b.Edges)>1:
            return next((v for e in b.Edges if (v:=hit(a,e,r)) is not None),None)
        try:
            check();checks+=1
            gap,volume=cache.check(a,b,0,r)
        except (TimeoutError,AssertionError,RuntimeError,ValueError) as e:
            errors.append(str(e));save();raise
        if volume>1e-5 or (r and gap<r-1e-6):return dict(volume_mm3=volume,gap_mm=gap,required_mm=r)
        return None
    save()
    for side,sign in [('L',1),('R',-1)]:
        root='F_'+side+'1_CP2';old=next(r for r in q['records'] if r['id']==root)['new_flange_world_mm']
        local=[s for n,s in q['parts'].items() if n.startswith('UnderdeckBank/'+root+'/')]
        installed=Part.makeCompound(local)
        service=Part.makeCompound([q['sweeps'][root]]+[s for n,s in q['jaws'].items() if n.startswith(root+'/')])
        for z in (90.,115.,135.):
            for x in range(-90,151,30):
                row=dict(side=side,flange_mm=[x,sign*80,z],hard_witness=None,printed_redesign_contacts=[],necessary_factory_capacity_looms=[])
                rows.append(row);translation=A.Vector(x-old[0],sign*80-old[1],z-old[2])
                a=installed.copy();a.translate(translation);b=service.copy();b.translate(translation)
                row.update(installed_bounds_mm=shape_bounds(a),service_bounds_mm=shape_bounds(b))
                # Fail fast on a real immutable-material witness, not bbox.
                for kind,s in [('installed',a),('ATO_projectjaw',b)]:
                    for n,t in hard.items():
                        if (v:=hit(s,t)) is not None:row['hard_witness']=dict(kind=kind,obstacle=n,**v);break
                    if row['hard_witness']:break
                    for n,(w,r) in wires.items():
                        if (v:=hit(s,w,r+.25)) is not None:row['hard_witness']=dict(kind=kind,obstacle=n,**v);break
                    if row['hard_witness']:break
                if not row['hard_witness']:
                    for n,t in soft.items():
                        if not t.Solids:continue
                        for kind,s in [('installed',a),('ATO_projectjaw',b)]:
                            if (v:=hit(s,t)) is not None:row['printed_redesign_contacts'].append(dict(kind=kind,obstacle=n,**v))
                    for r in contract['rows']:
                        if r['core']!='V' or r['loom'][1]!=side:continue
                        # Necessary distance only; individual TE binding remains to be generated.
                        point=[x,sign*(80-50.598),z+7]
                        bound=math.dist(point,r['bundle_root_world_mm'])+r['terminal_allowance_project_mm']
                        if bound<=r['capacity_before_terminal_mm']:row['necessary_factory_capacity_looms'].append(r['loom'])
                save();print('corridor',row['flange_mm'],'hard',None if not row['hard_witness'] else row['hard_witness']['obstacle'],'soft',len(row['printed_redesign_contacts']),flush=True)
    save();print(json.dumps(dict(candidates=len(rows),hard_clear=sum(not r['hard_witness'] for r in rows),checks=checks,seconds=round(time.monotonic()-tick,3))),flush=True)


if __name__=='__main__':run()
