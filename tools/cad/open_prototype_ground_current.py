"""Current W001, independent of rejected lower-S1 family. Read-only gate.

Nominal BAT cup and WAGO entry remain project datums. No stock selection,
physical acceptance or claim that the four S1 feeds are complete.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math, sys, time
import open_prototype_source_group as B
import open_prototype_biarc as C
import open_prototype_rl_tail_group as T
from whole_cat_source_bay_plan import Route
from open_prototype_entry_chambers import CONTEXT, MOUNTS

OUT=T.OUT
PLAN=OUT/'ground-upstream-grip-plan.json'
PROOF=OUT/'ground-upstream-grip-radius.json'

def build():
    p=T.build()
    e=next(e for e in p['body_ends'] if e['wire']=='W001' and e['current_role']=='G1.1')
    start=[-73,-58.8,57];end=e['datum']['point_mm']
    assert end==[-93,-53,105] and e['datum']['departure']==B.SOUTH
    # Actual bank input and output occupy the old vertical column. F0 also
    # prevents moving that column EAST. Go NORTH before rising; return to
    # G1 through a complete upper/downward hairpin, not a shorter bend.
    route=Route('W001',start,B.EAST,3.1,12.4,19,[])
    route.line(9);route.turn(B.NORTH,12.4);route.turn(B.UP,12.4)
    route.line(end[2]+12.4-route.p[2]);route.turn(B.WEST,12.4)
    route.line(route.p[0]-(end[0]+12.4));route.turn(B.SOUTH,12.4)
    grip_start=route.p[:]
    route.line(route.p[1]-(end[1]-3))
    grip_end=route.p[:]
    route.turn(B.DOWN,12.4);route.turn(B.NORTH,12.4)
    # The independent9.6mm G1 grip is on the upper incoming straight.
    # The final3mm outside-WAGO straight is NOT used as a grip land.
    tip=B.add(route.p,B.mul(B.NORTH,3))
    route.row['segments'].append(dict(kind='line',start_mm=route.p,end_mm=tip,tangent=B.NORTH,length_mm=3))
    route.p=tip;route.finish(end,B.NORTH)
    parts=[dict(kind=s['kind'],start=s['start_mm'],end=s['end_mm'],
                **(dict(mid=s['mid_mm']) if s['kind']=='arc' else {}))
           for s in route.row['segments']]
    length=B.check_path(parts,start,end,12.4)
    assert B.segment_geometry(parts[0])[0]>=9-1e-7
    assert math.dist(grip_start,grip_end)>=9-1e-7
    return p,dict(wire='W001',net='G_SYS',ends=['BAT.minus','G1.1'],
        start_mm=start,end_mm=end,segments=parts,OD_mm=3.1,minimum_radius_mm=12.4,
        centreline_mm=length,termination_allowance_mm=19,
        nominal_fit_blank_mm=math.ceil(length+19),old150mm_blank_margin_mm=150-length-19,
        material='LAPP0107001',terminal_allowance_basis='14mm WAGO strip +5mm solder project allowance',
        datum_basis='Retained nominal robot XT60 negative cup; current G1.1 project entry, not supplier cavity measurement',
        grips=[dict(end='BAT.minus',insulation_axis_from_mm=parts[0]['start'],
                    insulation_axis_to_mm=parts[0]['end']),
               dict(end='G1.1',insulation_axis_from_mm=grip_start,
                    insulation_axis_to_mm=grip_end,
                    grip_is_before_hairpin_not_on_final3mm=True)],
        grip_mounts_and_assembly_access_open=True,selected=False,stage_completed=False,physical_pass=False)

def plan():
    tick=time.monotonic();p,row=build()
    files=[Path(__file__),Path(C.__file__),Path(T.__file__),CONTEXT,MOUNTS,
           OUT/'TailLocalCurrent.FCStd',OUT/'obstacle-map-current.json',OUT/'endpoint-plan.json']
    result=dict(status='CURRENT_GROUND_NOMINAL_PLAN_ONLY',row=row,
        source_sha256={f.relative_to(T.ROOT).as_posix():B.sha(f) for f in files},
        geometry_digest=__import__('hashlib').sha256(json.dumps(row,sort_keys=True).encode()).hexdigest(),
        selected=False,stage_completed=False,physical_pass=False,
        worker_seconds=time.monotonic()-tick)
    PLAN.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],length=row['centreline_mm'],blank=row['nominal_fit_blank_mm'])))

def gate():
    import FreeCAD as A
    import open_prototype_tail_clearance as H
    assert not PROOF.exists(),'Do not repeat unchanged geometry'
    tick=time.monotonic();p,row=build();saved=B.read(PLAN)
    assert row==saved['row']
    pins=saved['source_sha256']
    assert all(B.sha(T.ROOT/f)==v for f,v in pins.items())
    result=dict(status='PENDING',conflicts=[],outside=[],errors=[],tested_pairs=0,
        source_sha256=pins,selected=False,stage_completed=False,physical_pass=False,
        native_files_changed=0,grip_mounts_and_all_other_unfinished_routes_open=True)
    docs=[]
    def distance(n,s,t,r,basis):
        if not H.near(s,t,r):return
        assert s.isValid() and t.isValid(),n
        print(json.dumps(dict(pair=n,seconds=round(time.monotonic()-tick,2))),flush=True)
        d=s.distToShape(t)[0];result['tested_pairs']+=1
        assert math.isfinite(d)
        if d<r-1e-6:result['conflicts'].append(dict(target=n,distance_mm=d,required_mm=r,basis=basis))
    try:
        docs=[A.openDocument(str(f)) for f in (CONTEXT,MOUNTS,OUT/'TailLocalCurrent.FCStd')]
        ctx,mount,tail=docs;parts=row['segments'];s=H.wire(parts);radius=row['OD_mm']/2
        shell=ctx.TorsoEnvelope.Shape
        d=s.distToShape(shell.Shells[0])[0]
        if not shell.isInside(A.Vector(*parts[0]['start']),1e-7,True) or d<radius-1e-6:
            result['outside'].append(dict(distance_mm=d,required_mm=radius))
        for q in p['stations']+p['mta']+p['holders']:
            candidate=H.trim(parts,last=radius+1e-5) if q['role']=='G1' else s
            distance(q['role'],candidate,H.box(q['centre_mm'],q['size_mm']),radius,'Current nominal component reservation')
        for q in B.read(OUT/'obstacle-map-current.json')['objects']:
            n=q['name']
            if n.startswith('S1_'):
                if q['kind']=='service_budget':continue
                t=ctx.getObject(n).Shape.copy();spec=p['s1_module']
                t.rotate(A.Vector(*spec['pivot_mm']),A.Vector(1,0,0),spec['whole_rotation_deg'])
                t.translate(A.Vector(*spec['translation_mm']))
                if n.startswith('S1_ring_'):
                    ring=next(r for r in spec['rings'] if r['terminal']==int(n[-1]))
                    t.rotate(A.Vector(*ring['eye_mm']),A.Vector(0,0,1),ring['ring_rotation_z_deg'])
                basis='Retained transformed S1 material'
            elif q['kind'] in ('candidate_station','replaceable_support'):continue
            elif q['basis'].startswith('Canonical whole-component/reference envelope') or n=='U1UnknownModuleReservation':
                b=q['bounds_mm'];t=H.box([(b[i]+b[i+3])/2 for i in range(3)],[b[i+3]-b[i] for i in range(3)])
                basis='Whole-component reservation, not measured material'
            else:
                obj=tail.CurrentTailSupport if n=='CurrentTailSupport' else ctx.getObject(n) or mount.getObject(n)
                assert obj is not None and hasattr(obj,'Shape'),n
                t=obj.Shape;basis='Retained material'
            candidate=H.trim(parts,first=radius+1e-5) if n=='XT60_CP2' else s
            distance(n,candidate,t,radius,basis)
        for n,profile in H.profiles(p).items():
            distance(n,s,H.wire(profile[0]),radius+profile[1],'Independent current conductor reservation')
        for n in ('W075','W076_FACTORY','W076_EXTENSION'):
            distance(n,s,ctx.getObject(n+'_CP2').Shape,radius,'Retained insulated legacy source material')
        result['status']='REJECTED_CURRENT_GROUND' if result['conflicts'] or result['outside'] else 'CURRENT_GROUND_RADIUS_CLEAR_NATIVE_GRIPS_AND_SOURCE_BAY_OPEN'
    except Exception as exc:
        result['errors'].append(str(exc));result['status']='ERROR_NOT_CLEARANCE';raise
    finally:
        for doc in docs:A.closeDocument(doc.Name)
        if not all(B.sha(T.ROOT/f)==v for f,v in pins.items()):
            result['errors'].append('Sources changed during gate');result['status']='INVALID_PINS'
        result.update(worker_seconds=round(time.monotonic()-tick,3),finished_utc=datetime.now(timezone.utc).isoformat())
        PROOF.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(result),flush=True)

if __name__=='__main__':
    gate() if '--gate' in sys.argv else plan()
