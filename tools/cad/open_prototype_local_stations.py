"""Two integral three-wire seats and current fixed pitch transition.

Replace the same source carriers, not add more brackets. The pitch moving loop,
tail continuations and upstream fanouts remain separate unfinished interfaces.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import math
import shutil
import tempfile
import time
from open_prototype_wiring_endpoints import ROOT, BASE, read, sha, bounds
import open_prototype_bundle_spines as B

OUT=BASE/'wiring-checkpoint'
SOURCE=OUT/'BundleSpinesPreflight.FCStd'
MODEL=OUT/'LocalStationsAssembly.FCStd'


def pitch_parts():
    r=B.RADIUS;q=math.sqrt(.5);straight=(17-2*r*(1-q))/q
    p0=[-52,74,166]
    p1=B.add(p0,[0,-r*q,-r*(1-q)])
    p2=B.add(p1,[0,-straight*q,-straight*q])
    p3=B.add(p2,[0,-r*q,-r*(1-q)])
    v=[0,-q,-q];u=[0,-1,0];axis=[1,0,0]
    def arc(a,c,b,t0,t1):
        return dict(kind='arc',start=a,mid=B.add(c,B.rotate(B.sub(a,c),axis,math.pi/8)),
                    end=b,t0=t0,t1=t1,axis=axis,angle=math.pi/4)
    # The second bend rotates back to horizontal; opposite signed axis.
    c0=B.add(p0,[0,0,-r]);c1=B.add(p3,[0,0,r])
    forward=[dict(kind='line',start=[-52,86,166],end=p0,t0=u,t1=u),arc(p0,c0,p1,u,v),
             dict(kind='line',start=p1,end=p2,t0=v,t1=v),
             dict(kind='arc',start=p2,mid=B.add(c1,B.rotate(B.sub(p2,c1),[-1,0,0],math.pi/8)),
                  end=p3,t0=v,t1=u,axis=[-1,0,0],angle=math.pi/4),
             dict(kind='line',start=p3,end=[-52,26,149],t0=u,t1=u)]
    reverse=[]
    for e in reversed(forward):
        row=dict(kind=e['kind'],start=e['end'],end=e['start'],t0=B.mul(e['t1'],-1),t1=B.mul(e['t0'],-1))
        if e['kind']=='arc':row.update(mid=e['mid'],axis=B.mul(e['axis'],-1),angle=e['angle'])
        reverse.append(row)
    return reverse


def build_plan():
    proof=read(OUT/'bundle-spines-checks.json')
    assert proof['status']=='SHARED_TRUNKS_STATICALLY_CLEAR_SOURCE_FANOUTS_AND_MOUNTS_OPEN'
    assert sha(SOURCE)==proof['preview_sha256']
    pitch_floor=166-B.N-1.05;tail_floor=118-2*B.N-1.05
    return dict(status='CURRENT_TWO_INTEGRAL_SEATS_AND_PITCH_TRANSITION_PLAN',
        stations=[dict(name='PitchFixed',owner='SourceLeftCarrier',floor_z_mm=pitch_floor,
            base_z_mm=90.99,post_xywh_mm=[-54,68,4,4],bridge_xywh_mm=[-60,70,16,19],
            seat_xywh_mm=[-60,77,16,9],
            slot_centres_mm=[[-56.3,81.5],[-47.7,81.5]],tie_axis=1,tie_centre_mm=-52,
            strap_structure_depth_mm=4,
            straight_insulation_length_mm=9,wire_names=['XB22','XB23','XS23']),
          dict(name='TailFixed',owner='SourceRightCarrier',floor_z_mm=tail_floor,
            base_z_mm=89.99,post_xywh_mm=[64,-43.375,4,2],seat_xywh_mm=[47.5,-51,20.5,13],
            grip_region_x_mm=[47.5,56.5],strap_plane_x_mm=51.5,
            slot_centres_mm=[[51.5,-49.3],[51.5,-40.7]],tie_axis=0,tie_centre_mm=-45,
            strap_structure_depth_mm=2,
            straight_insulation_length_mm=9,wire_names=['XB32','XB33','XS33'])],
        pitch_parts=pitch_parts(),replaces_same_two_carriers=True,
        added_print_parts=0,added_screws_connectors=0,added_T18I=2,
        source_fixture_ties_subtotal=26,tail_local_existing_ties=5,whole_stock_open=True,
        changed_cause_after_failed_seats='Pitch seat occupies last9mm straight with stepped structural bridge; strap must wrap the complete4mm structure, NOT the2mm seat alone. Tail strap has freeX51.5 bay and outward-facing head between the two ATO access lanes, not inward into HP tool. Wire paths/ends unchanged.',
        previous_failed_gates=[
            dict(rows=7,pairs=44,errors=0,seconds=139.765,cause='Full/addition duplicates included: pitch flat arm under curved wires; tail return in old holder strap plane/under upright.'),
            dict(rows=3,pairs=45,errors=0,seconds=142.844,cause='Duplicated pitch-band contact: assumed2mm wrap under4mm stepped structure; tail inward head blocksHPATO tool.')],
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (SOURCE,OUT/'bundle-spines-checks.json',
                         OUT/'TailLocalCurrent.FCStd',BASE/'OpenPrototypePlan.FCStd',Path(__file__),Path(B.__file__))},
        assembly=['Install same source carriers before routing; integral posts are not detachable extra brackets.',
            'Lay three pitch wires on fixed9mm seat Y77..86, continuous insulation and one replaceable strap.',
            'Lay three tail wires on straight grip region X47.5..56.5, continuous insulation; strap planeX51.5 is independent of existing holder straps.',
            'Do not transfer strain to WAGO adhesive, factory holder leads or PCB solder joints.',
            'Pitch strap goes through4mm structure and returns below low bridge, not between bridge and seat; tail head faces outward in gap between HP and TY ATO lanes.',
            'Pitch moving loop, tail local continuations, full fanouts and common removal recipe remain OPEN.'],
        delivery_gates=['T18I bend/fit and no-crush/pull/creep of each wire',
                        'PETG upright stiffness and print support coupon, not structural approval'],
        selected=False,stage_completed=False,physical_pass=False)


def main():
    import FreeCAD as A
    import Part
    import MeshPart
    from open_deck_p0_supports import sketch,feature
    from open_deck_p0_plate import rect
    from open_prototype_fhac_supports import ring
    tick=time.monotonic();plan=build_plan()
    (OUT/'local-stations-plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    d=A.openDocument(str(SOURCE));ctx=A.openDocument(str(BASE/'OpenPrototypePlan.FCStd'));tail=A.openDocument(str(OUT/'TailLocalCurrent.FCStd'))
    names=[o.Name for o in (d,ctx,tail)]
    result=dict(status='PENDING',contacts=[],errors=[],tested_pairs=0,source_sha256=plan['source_sha256'],
                selected=False,stage_completed=False,physical_pass=False)
    try:
        p=d.Parameters;p.addProperty('App::PropertyLength','LocalSeatSlotWidth');p.LocalSeatSlotWidth=3.5
        previous={};changed=[];ties={}
        for r in plan['stations']:
            b=d.getObject(r['owner']);previous[b.Name]=b.Shape.copy();changed.append(b)
            sk=sketch(b,r['name']+'PostPlan',r['base_z_mm']);rect(sk,*r['post_xywh_mm'])
            bridge=r.get('bridge_xywh_mm')
            b.Tip=feature(b,'Pad',r['name']+'Upright',sk,r['floor_z_mm']-(4 if bridge else 2)-r['base_z_mm'])
            if bridge:
                sk=sketch(b,r['name']+'LowBridgePlan',r['floor_z_mm']-4);rect(sk,*bridge)
                b.Tip=feature(b,'Pad',r['name']+'LowBridge',sk,2)
            sk=sketch(b,r['name']+'SeatPlan',r['floor_z_mm']-2);rect(sk,*r['seat_xywh_mm'])
            b.Tip=feature(b,'Pad',r['name']+'Seat',sk,2)
            sk=sketch(b,r['name']+'StrapPlan',r['floor_z_mm'])
            for x,y in r['slot_centres_mm']:
                if r['tie_axis']==1:
                    rect(sk,x-.85,y-1.75,1.7,3.5)
                    sk.setExpression(f'Constraints[{sk.ConstraintCount-1}]','Parameters.LocalSeatSlotWidth')
                else:rect(sk,x-1.75,y-.85,3.5,1.7,'Parameters.LocalSeatSlotWidth')
            # Tail outer strap slot straddles the upright edge by0.175mm:
            # continue below the2mm seat, rather than claiming a blind slot
            # is through. No shift of wires, holders or previous fixtures.
            b.Tip=feature(b,'Pocket',r['name']+'StrapThrough',sk,4)
            z=r['floor_z_mm'];top=z+3.919615242270663+1.2
            if r['tie_axis']==1:
                box=[-57.15,80.25,z-r['strap_structure_depth_mm']-1.2,-46.85,82.75,top]
                head=[-61.65,79.25,z+.5,-57.15,83.75,z+4]
            else:
                cx=r['strap_plane_x_mm']
                box=[cx-1.25,-50.15,z-r['strap_structure_depth_mm']-1.2,cx+1.25,-39.85,top]
                head=[cx-2.25,-54.15,z+.5,cx+2.25,-49.65,z+4]
            ties[r['name']+'_Tie']=ring(A,Part,r['tie_axis'],2.5,box,head)
        def native():
            d.recompute();v={}
            for b in changed:
                assert b.Shape.isValid() and len(b.Shape.Solids)==1 and not b.Shape.check(True),b.Name
                assert all('Invalid' not in o.State and 'Touched' not in o.State for o in b.Group),b.Name
                assert all(s.FullyConstrained and s.solve()==0 for s in b.Group if s.TypeId=='Sketcher::SketchObject')
                v[b.Name]=b.Shape.Volume
            return v
        original=native();p.LocalSeatSlotWidth=3.2;trial=native()
        assert all(trial[n]>v for n,v in original.items())
        p.LocalSeatSlotWidth=3.5;restored=native()
        assert all(abs(restored[n]-v)<1e-5 for n,v in original.items())
        transition={};rows=[]
        for wire,s,n in [('XB22',-1.05,-B.N),('XB23',1.05,-B.N),('XS23',0,2*B.N)]:
            edges=[]
            for e in B.offsets(plan['pitch_parts'],[1,0,0],s,n):
                edge=Part.makeLine(A.Vector(*e['start']),A.Vector(*e['end'])) if e['kind']=='line' else Part.Arc(A.Vector(*e['start']),A.Vector(*e['mid']),A.Vector(*e['end'])).toShape()
                if e['kind']=='arc':assert edge.Curve.Radius>=12.6
                edges.append(edge)
            for a,b in zip(edges,edges[1:]):
                assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length<1e-7
                assert a.tangentAt(a.LastParameter).dot(b.tangentAt(b.FirstParameter))>1-1e-7
            path=Part.Wire(edges);e=edges[0]
            profile=Part.Wire([Part.makeCircle(1.05,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])
            shape=path.makePipeShell([profile],True,False);assert shape.isValid() and len(shape.Solids)==1
            transition[wire+'_PitchTransition']=shape
            row=next(x for x in read(OUT/'bundle-spines-checks.json')['wire_rows'] if x['wire']==wire)
            assert (e.valueAt(e.FirstParameter)-A.Vector(*row['end_mm'])).Length<1e-7
            rows.append(dict(wire=wire,fixed_transition_length_mm=path.Length,fixed_anchor_mm=list(edges[-1].valueAt(edges[-1].LastParameter))))
        targets={}
        for o in d.Objects:
            if 'Shape' not in o.PropertiesList or o.Shape.isNull() or o in changed or o.Name=='BUS_CP2':continue
            if o.TypeId in ('PartDesign::Body','App::Link') or o.Name.endswith(('_CurrentReference','NominalPCB','_CP2','_SharedTrunkReservation')) or o.Name.startswith('BUSsupplier'):
                targets['mount/'+o.Name]=o.Shape
        for o in ctx.Objects:
            if 'Shape' in o.PropertiesList and not o.Shape.isNull() and o.Name.startswith(('P0_','Head_','TailBridge')) and o.Name!='P0_MG92BMount29':targets['context/'+o.Name]=o.Shape
        targets['tail/CurrentTailSupport']=tail.CurrentTailSupport.Shape
        def check(n,s,m,t):
            if not s.BoundBox.intersect(t.BoundBox):return
            result['tested_pairs']+=1
            try:
                assert s.isValid() and t.isValid()
                hit=s.common(t);assert hit.isValid()
                if hit.Volume>1e-5:result['contacts'].append(dict(a=n,b=m,volume_mm3=hit.Volume,bounds_mm=bounds(hit)))
            except Exception as exc:result['errors'].append(dict(a=n,b=m,error=str(exc)))
        additions={b.Name+'_Added':b.Shape.cut(previous[b.Name]) for b in changed}
        new=dict(additions,**ties,**transition)
        for n,s in new.items():
            for m,t in targets.items():check(n,s,m,t)
        for i,(n,s) in enumerate(new.items()):
            for m,t in list(new.items())[i+1:]:check(n,s,m,t)
        # Full changed bodies against their wire/tie mating references, not just added material.
        for b in changed:
            for n,s in dict(ties,**transition).items():check(b.Name,b.Shape,n,s)
        slot_checks=[]
        for r in plan['stations']:
            for x,y in r['slot_centres_mm']:
                size=(1.5,3.3) if r['tie_axis']==1 else (3.3,1.5)
                probe=Part.makeBox(*size,2.2,A.Vector(x-size[0]/2,y-size[1]/2,r['floor_z_mm']-2.1))
                h=probe.common(d.getObject(r['owner']).Shape)
                assert h.isValid(),'Invalid slot Boolean'
                clear_slot=h.Volume<1e-6
                slot_checks.append(dict(station=r['name'],centre_mm=[x,y],full_depth_clear=clear_slot,remaining_mm3=h.Volume))
                if not clear_slot:result['contacts'].append(dict(a=r['name']+'_SlotProbe',b=r['owner'],volume_mm3=h.Volume,bounds_mm=bounds(h)))
        clear=not result['contacts'] and not result['errors']
        result.update(status='TWO_INTEGRAL_LOCAL_SEATS_FIXED_PITCH_PREPARED' if clear else 'LOCAL_STATIONS_REQUIRE_SHARED_CHANGE',
                      pitch_transition=rows,slot_checks=slot_checks,new_T18I=2,new_print_parts_screws_connectors=0,
                      parameter_trial='LocalSeatSlotWidth3.5->3.2->3.5, both native seats restored',
                      moving_pitch_tail_continuations_fanouts_and_stock_open=True)
        if clear:
            for n,s in dict(ties,**transition).items():
                o=d.addObject('Part::Feature',n+'_CurrentReference');o.Shape=s
                o.addProperty('App::PropertyString','Qualification');o.Qualification='Fixed transition or nominal bent strap, not moving-loop/strength approval'
            exports={}
            for b in changed:
                mesh=MeshPart.meshFromShape(Shape=b.Shape,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
                assert mesh.isSolid() and not mesh.hasNonManifolds()
                assert max(mesh.BoundBox.XLength,mesh.BoundBox.YLength,mesh.BoundBox.ZLength)+10<256
                dest=OUT/('Station'+b.Name+'.stl');mesh.write(str(dest));exports[dest.name]=sha(dest)
            d.saveAs(str(MODEL));A.closeDocument(d.Name)
            with tempfile.TemporaryDirectory(prefix='robot-cat-stations-reopen-') as td:
                dest=Path(td)/MODEL.name;shutil.copy2(MODEL,dest);q=A.openDocument(str(dest));q.recompute()
                for n,v in original.items():assert q.getObject(n).Shape.isValid() and abs(q.getObject(n).Shape.Volume-v)<1e-5
                A.closeDocument(q.Name)
            result.update(native_sha256=sha(MODEL),exports=exports,relocated_reopen=True)
    finally:
        for n in names:
            if n in A.listDocuments():A.closeDocument(n)
    result.update(worker_wall_seconds=time.monotonic()-tick,finished_utc=datetime.now(timezone.utc).isoformat())
    (OUT/'local-stations-checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()
