"""One whole S1 terminal-plane alternative, before wire or bracket details.

Rotate the complete nominal source module, not the rings' bearing axis alone.
All four contacts, casing, actuator and tool reservations travel together.
No native sources are saved; clearance of this module is not full wiring.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,time,math
import FreeCAD as A
import Part
import open_prototype_source_group as B
import open_prototype_rr_receiving_branch as R
from open_prototype_entry_chambers import CONTEXT,MOUNTS

OUT=B.OUT;ROOT=B.ROOT;PROOF=OUT/'s1-terminal-plane-budget.json'

def main():
    assert not PROOF.exists(),'No unchanged repeat'
    tick=time.monotonic();p=R.build()
    paths=(CONTEXT,MOUNTS,OUT/'TailLocalCurrent.FCStd',OUT/'obstacle-map-current.json',
           OUT/'rr-receiving-branch-plan.json',Path(__file__),Path(R.__file__))
    pins={f.relative_to(ROOT).as_posix():B.sha(f) for f in paths}
    docs=[];result=dict(status='PENDING',source_sha256=pins,contacts=[],outside=[],errors=[],
        driver_obstructions=[],tested_pairs=0,selected=False,stage_completed=False,physical_pass=False,
        module_change='Entire S1 X+90deg about126.2,55.5,85 then translate0,-55.5,+22.5; terminal plane becomes Z85. No individual bearing-axis fiction.',
        invalidated=['S1 mounting/support','All four S1 routes and920mm historical blanks','S1 assembled driver access'],
        unchanged=['P0','bankR47','4MTA','MAIN46.52','15 drives','MG92B','Torso325x200x160'],
        next='Only consider this layout with complete four-exit routes, new retention and assembled installation/removal. Casing fit alone is not selection.')
    def box(c,size):return Part.makeBox(*size,A.Vector(*[v-d/2 for v,d in zip(c,size)]))
    try:
        docs=[A.openDocument(str(f)) for f in paths[:3]]
        ctx,mount,tail=docs;torso=ctx.TorsoEnvelope.Shape
        assert torso.isValid() and len(torso.Solids)==1
        scene=[(r['role'],box(r['centre_mm'],r['size_mm'])) for r in p['stations']+p['mta']+p['holders']]
        moved={};drivers={};records=B.read(OUT/'obstacle-map-current.json')['objects']
        for r in records:
            n=r['name']
            if not n.startswith('S1_'):continue
            source=ctx.getObject(n);assert source is not None and source.Shape.isValid()
            s=source.Shape.copy();s.rotate(A.Vector(126.2,55.5,85),A.Vector(1,0,0),90)
            s.translate(A.Vector(0,-55.5,22.5))
            if n.startswith('S1_ring_'):
                terminal=int(n[-1]);eye=A.Vector(120.2 if terminal in (2,3) else 132.2,0 if terminal in (2,5) else 12,85)
                # Upper contacts turn SOUTH, lower NORTH: do not cross
                # adjacent eyes. Rotation is in the new actual bearing plane.
                angle=90 if terminal in (2,6) else-90
                s.rotate(eye,A.Vector(0,0,1),angle)
            assert s.isValid() and s.Solids,n
            (drivers if r['kind']=='service_budget' else moved)[n]=s
        assert len(moved)==14 and len(drivers)==4
        for r in records:
            n=r['name']
            if n.startswith('S1_') or r['kind'] in ('candidate_station','replaceable_support'):continue
            if r['basis'].startswith('Canonical whole-component/reference envelope') or n=='U1UnknownModuleReservation':
                v=r['bounds_mm'];s=box([(v[i]+v[i+3])/2 for i in range(3)],[v[i+3]-v[i] for i in range(3)])
            else:
                obj=tail.CurrentTailSupport if n=='CurrentTailSupport' else ctx.getObject(n) or mount.getObject(n)
                assert obj is not None and hasattr(obj,'Shape'),n
                s=obj.Shape
            assert s.isValid() and s.Solids,n
            scene.append((n,s))
        def test(n,s,m,t,store):
            if not s.BoundBox.intersect(t.BoundBox):return
            h=s.common(t);assert h.isValid(),(n,m)
            result['tested_pairs']+=1
            if h.Volume>1e-6:store.append(dict(a=n,b=m,volume_mm3=round(h.Volume,6)))
        for n,s in moved.items():
            # Actuator may protrude for manual access. Report, don't hide it.
            if n in ('S1_body_CP2','S1_control_CP2'):
                out=s.cut(torso);assert out.isValid()
                if out.Volume>1e-6:result['outside'].append(dict(name=n,volume_mm3=round(out.Volume,6)))
            for m,t in scene:test(n,s,m,t,result['contacts'])
        rings=[(n,s) for n,s in moved.items() if n.startswith('S1_ring_')]
        for i,(n,s) in enumerate(rings):
            for m,t in rings[:i]:test(n,s,m,t,result['contacts'])
        for n,s in drivers.items():
            for m,t in scene:test(n,s,m,t,result['driver_obstructions'])
        result.update(status='REJECTED_SHARED_S1_SPACE_BUDGET' if result['contacts'] or result['outside']
            else 'MODULE_SPACE_ONLY_DRIVER_SEQUENCE_AND_ALL_ROUTES_OPEN',
            moved_parts=len(moved),driver_reservations=len(drivers),retained_and_candidate_targets=len(scene),
            bearing_plane='XY, normalZ after whole module rotation',
            barrel_mm={'2':[120.2,-22.123,85],'5':[132.2,-22.123,85],
                '3':[120.2,34.123,85],'6':[132.2,34.123,85]})
    except Exception as exc:
        result['errors'].append(str(exc));result['status']='ERROR_NOT_CLEARANCE';raise
    finally:
        for doc in docs:A.closeDocument(doc.Name)
        assert all(B.sha(ROOT/n)==h for n,h in pins.items()),'Changed source; no acceptance'
        result.update(worker_seconds=round(time.monotonic()-tick,3),finished_utc=datetime.now(timezone.utc).isoformat())
        PROOF.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:result[k] for k in ('status','contacts','outside','driver_obstructions','errors','tested_pairs','worker_seconds')}),flush=True)

if __name__=='__main__':main()
