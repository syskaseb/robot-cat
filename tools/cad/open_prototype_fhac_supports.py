"""One shared five-holder fixture candidate, with current input/load/access space.

Keep historical input and Pi evidence immutable. Only HP changes its allocation.
Commercial body/lid, cable OD, bent ties and pull/creep remain delivery gates.
"""
import copy
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from open_prototype_wiring_endpoints import ROOT, BASE, read, sha, bounds

OUT = BASE/'wiring-checkpoint'
SOURCE = OUT/'PiWireSupportAssembly.FCStd'
MODEL = OUT/'SourceFixturesAssembly.FCStd'
PLAN = OUT/'fhac-mount-plan.json'
PROOF = OUT/'fhac-mount-checks.json'
TIE = ROOT/'hardware/reference/hellermann-11102370-2026-10-04/dimensions.json'


def build_plan():
    previous = read(OUT/'source-layout-plan.json')
    rows = copy.deepcopy(previous['source_plan'])
    hp = next(r for r in rows if r['holder']=='F_HP')
    # Move across the inlet, not a scalar clearance search: clear front MTA's
    # vertical ATO access while preserving port, curve radius and cut length.
    hp.update(input_exit_mm=[17,-31.25,99.99], output_exit_mm=[68,-31.25,99.99],
        input_departure=[-1,0,0], output_departure=[1,0,0],
        proposed_body_bounds_mm=[17,-41.375,89.99,68,-21.125,111.99])
    tie = read(TIE)
    assert tie['length_mm']==145 and tie['maximum_bundle_diameter_mm']==35
    return dict(status='FIVE_HOLDER_SHARED_FIXTURE_PLAN_NOT_SELECTED',
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in
            (SOURCE, OUT/'source-layout-plan.json', TIE, Path(__file__))},
        source_plan=rows, superseded_interface='Historical HP allocation/input fit only',
        reused_unchanged_interfaces=['PI input/output/saddle','AUX input','HY input','TY input'],
        input_wire_OD_mm=4, quarter_radius_mm=6,
        independent_left_inputs=dict(holders=['F_PI','F_AUX'],
            seat_y_mm=[62.75,71.75], seat_top_z_mm=98.99, seat_length_mm=9),
        independent_right_inputs=dict(holders=['F_HY','F_HP','F_TY'],
            seat_y_mm=[-74.725,-65.725], seat_top_z_mm=97.99, seat_length_mm=9,
            strap_centres_y_mm=[-72.7,-69.3],
            load_path='Shared three-wire intact-insulation comb; separate from WAGO adhesive/holder',
            casing_gap_TY_mm=.525, delivered_casing_and_wire_tolerance_gate=True),
        fixture_anchors=dict(left=[-70,45],right=[-40,90]),
        rail_slots_world_abs_y_mm=[71.55,73.25],
        tie_sku=tie['sku'], tie_dimensions_source=TIE.relative_to(ROOT).as_posix(),
        local_added_ties=dict(holder=10, input=4, rail_attachment=4, total=18),
        retained_Pi_wire_ties=2, removed_Pi_rail_ties=2, total_this_source_scope_ties=20,
        local_added_screws=0, electrical_connectors_added=0,
        assembly=['Fit left/right PETG carriers to retained rail lips with4 replaceable ties',
            'Seat5 bought bodies and loosely fit2 T18I per holder below delivered lid fit gate',
            'Route5 inputs; secure2 left wires individually and3 right wires with2 comb straps',
            'Pi joint moves outside ATO opening, its2 wire seats become integral with left carrier; other4 loads OPEN',
            'ATO service: power isolated; cut ONLY2 ties on affected holder; leave input relief and all WAGO connected',
            'Support holder by hand, open delivered lid/remove fuse from above; refit2 new ties'],
        access_basis='22x10x35mm vertical tool budget from CLOSED body budget; NOT supplier lid trajectory',
        superseded_Pi_interface='Old over-holder output and separate saddle blocked ATO; preserved as historical evidence, not current service approval',
        rejected_first_fixture=['Old Pi output/joint/saddle over the ATO opening',
            'TY outer-Y and HY outer-Y tie heads occupied WAGO/rail-post space; put these heads inward-Y'],
        rejected_second_fixture=['Direct Pi descent atY74.25 crossed lower-row FL_P/FL_G; turn inward above upper row BEFORE descending',
            'Pi support beam over body tie return; put beam behind complete body/strap budget atY69..73'],
        physical_gates=['Delivered closed holder/lid/strap contact surfaces and ATO motion',
            'OD/R6/casing gap and no-crush/pull test, including each of3 comb wires',
            'PETG layer strength/creep and wire tension must not load holder',
            'Remaining4 outputs, all body/leg/local circuits, source920mm and common stock'],
        selected=False, physical_pass=False, stage_completed=False)


def targets(A, Part, plan):
    from open_prototype_wiring_source_fit import input_path
    objects = {}
    for r in plan['source_plan']:
        box=r['proposed_body_bounds_mm']; n=r['holder']
        objects[n+'_body_budget']=Part.makeBox(*(box[i+3]-box[i] for i in range(3)),A.Vector(*box[:3]))
        objects[n+'_input']=input_path(A,Part,r,2)[0]
    return objects


def ring(A, Part, axis, span, box, head_box):
    """Rectangular bent-band reservation, not a measured manufactured bend."""
    lo,hi=box[:3],box[3:]
    s=Part.makeBox(*(hi[i]-lo[i] for i in range(3)),A.Vector(*lo))
    q=list(lo);size=[hi[i]-lo[i] for i in range(3)]
    for i in range(3):
        if i!=axis:q[i]+=1.2;size[i]-=2.4
    q[axis]-=.1;size[axis]+=.2
    s=s.cut(Part.makeBox(*size,A.Vector(*q)))
    h=Part.makeBox(*(head_box[i+3]-head_box[i] for i in range(3)),A.Vector(*head_box[:3]))
    return s.fuse(h).removeSplitter()


def tie_shapes(A, Part, plan):
    result={}
    for row in plan['source_plan']:
        n=row['holder'];b=row['proposed_body_bounds_mm'];cx=(b[0]+b[3])/2
        for i,x in enumerate((cx-12,cx+12)):
            # Band follows lower seat -> body top. Cut these2 ties for ATO,
            # not the independent input relief or any electrical connection.
            box=[x-1.25,b[1]-1.2,b[2]-3.2,x+1.25,b[4]+1.2,b[5]+1.2]
            head=([x-2.4,b[4]+1.2,b[2]+3,x+2.4,b[4]+5.7,b[2]+6.5]
                if n in ('F_HY','F_TY') else
                [x-2.4,b[1]-5.7,b[2]+3,x+2.4,b[1]-1.2,b[2]+6.5])
            result[n+'_body_tie'+str(i)]=ring(A,Part,0,2.5,box,head)
    for n,x in [('PI',-82.5),('AUX',1.5)]:
        y=67.25
        result[n+'_input_tie']=ring(A,Part,1,2.5,
            [x-6.2,y-1.25,95.79,x+6.2,y+1.25,104.19],
            [x-11,y-2.25,99.49,x-6.2,y+2.25,102.99])
    for i,y in enumerate(plan['independent_right_inputs']['strap_centres_y_mm']):
        head = ([-7.75,y-2.25,98.49,-2.95,y+2.25,101.99] if i==0 else
            [-2.95,y-2.25,103.19,1.85,y+2.25,106.69])
        result['right_comb_tie'+str(i)]=ring(A,Part,1,2.5,
            [-2.95,y-1.25,94.79,23.7,y+1.25,103.19],
            head)
    for side,sign in [('left',1),('right',-1)]:
        for i,x in enumerate(plan['fixture_anchors'][side]):
            box=[x-1.25,67.6,88.8,x+1.25,73,96.2]
            head=[x-2.4,69,96.2,x+2.4,73.5,99.7]
            if sign<0:
                box[1],box[4]=-box[4],-box[1]
                head[1],head[4]=-head[4],-head[1]
            result[side+'_rail_tie'+str(i)]=ring(A,Part,0,2.5,box,head)
    # Same2 splice insulation straps; no separate Pi saddle/rail straps.
    for n,x,top in [('W077',-32.68,117.99),('W078',-61.68,117.29)]:
        result[n+'_splice_tie']=ring(A,Part,0,2.5,
            [x-1.25,69.8,110.79,x+1.25,79.1,top+1.2],
            [x-2.4,79.1,top-2.3,x+2.4,83.6,top+1.2])
    return result


def main():
    if '--plan' in sys.argv:
        plan=build_plan();PLAN.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print('One5-holder plan: HP across inlet,2 carriers/18 additional ties/0 screws, no stock selection',flush=True)
        return
    import FreeCAD as A
    import Part
    import MeshPart
    from open_deck_p0_supports import sketch, feature
    from open_deck_p0_plate import rect
    tick=time.monotonic();plan=read(PLAN)
    for path,h in plan['source_sha256'].items():assert sha(ROOT/path)==h,path
    preflight=read(OUT/'fhac-space-preflight.json')
    assert preflight['status']=='CHANGED_PI_SERVICE_CORRIDOR_PREFLIGHT_CHECKED'
    for path,h in preflight['source_sha256'].items():assert sha(ROOT/path)==h,path
    assert not MODEL.exists(),'Receive current worker/result before another build'
    if PROOF.exists():assert read(PROOF)['status']=='SHARED_FIXTURES_REQUIRE_CHANGE'
    d=A.openDocument(str(SOURCE));ctx=A.openDocument(str(BASE/'OpenPrototypePlan.FCStd'))
    # Replace only own previous candidate's Pi saddle/route references, never
    # the saved source. Integration avoids another rail attachment dependency.
    old=d.PiSpliceInsulationSaddle
    for ob in reversed(list(old.Group)):d.removeObject(ob.Name)
    d.removeObject(old.Name)
    for n in ('W077_RouteReference','W078_RouteReference','PiJointShrinkAllowance_RouteReference'):
        d.removeObject(n)
    p=d.Parameters
    p.addProperty('App::PropertyLength','SourceFixtureSlotWidth');p.SourceFixtureSlotWidth=3.5
    p.addProperty('App::PropertyLength','SourceFixtureThickness');p.SourceFixtureThickness=2
    rail=d.SideDistributionRail
    sk=sketch(rail,'SourceRailTiePlan','Parameters.SideRailRise+Parameters.SideRailThickness')
    for x in sorted({x for a in plan['fixture_anchors'].values() for x in a}):
        rect(sk,x-1.75,-13.2,3.5,1.7,'Parameters.SourceFixtureSlotWidth')
    rail.Tip=feature(rail,'Pocket','SourceRailTieSlots',sk,'Parameters.SideRailThickness')
    bodies=[]
    for side,sign,names,zbase,xlimits in [('Left',1,['F_PI','F_AUX'],88.99,[-87.5,65.5]),
            ('Right',-1,['F_HY','F_HP','F_TY'],87.99,[-58.75,94])]:
        b=d.addObject('PartDesign::Body','Source'+side+'Carrier');bodies.append(b)
        b.addProperty('App::PropertyString','Qualification');b.Qualification='Replaceable prototype PETG fixture; delivery fit/force/creep OPEN'
        rows=[r for r in plan['source_plan'] if r['holder'] in names]
        zexpr=f'{zbase+2} mm - Parameters.SourceFixtureThickness'
        sk=sketch(b,side+'BeamPlan',zexpr)
        rect(sk,xlimits[0],65 if sign>0 else -69,xlimits[1]-xlimits[0],4)
        b.Tip=feature(b,'Pad',side+'Beam',sk,'Parameters.SourceFixtureThickness')
        sk=sketch(b,side+'ArmsPlan',zexpr)
        for r in rows:
            q=r['proposed_body_bounds_mm'];cx=(q[0]+q[3])/2
            for x in (cx-15,cx+15):
                y0,y1=(60,69) if sign>0 else (-69,q[1]+3)
                rect(sk,x-2,y0,4,y1-y0)
        b.Tip=feature(b,'Pad',side+'Arms',sk,'Parameters.SourceFixtureThickness')
        sk=sketch(b,side+'HolderSeatsPlan',zexpr)
        for r in rows:
            q=r['proposed_body_bounds_mm'];rect(sk,q[0]-2,q[1]-2,q[3]-q[0]+4,q[4]-q[1]+4)
        b.Tip=feature(b,'Pad',side+'HolderSeats',sk,'Parameters.SourceFixtureThickness')
        sk=sketch(b,side+'RailPostPlan',zbase+2)
        for x in plan['fixture_anchors'][side.lower()]:rect(sk,x-4,67 if sign>0 else -69,8,2)
        b.Tip=feature(b,'Pad',side+'RailPosts',sk,95-(zbase+2))
        sk=sketch(b,side+'FootPlan',93)
        for x in plan['fixture_anchors'][side.lower()]:rect(sk,x-4,69 if sign>0 else -73,8,4)
        b.Tip=feature(b,'Pad',side+'RailFeet',sk,2)
        sk=sketch(b,side+'FrontTiePassPlan',95)
        for x in plan['fixture_anchors'][side.lower()]:
            rect(sk,x-1.75,67.5 if sign>0 else -69,3.5,1.5,'Parameters.SourceFixtureSlotWidth')
        b.Tip=feature(b,'Pocket',side+'FrontTiePass',sk,95-(zbase-.2))
        sk=sketch(b,side+'FootTiePassPlan',95)
        for x in plan['fixture_anchors'][side.lower()]:
            rect(sk,x-1.75,71.55 if sign>0 else -73.25,3.5,1.7,'Parameters.SourceFixtureSlotWidth')
        b.Tip=feature(b,'Pocket',side+'FootTiePass',sk,2)
        # Body tie notches sit outside bought-body budgets; slots through
        # actual supporting seat thickness, not pretend floating tie heads.
        sk=sketch(b,side+'BodyTiePassPlan',zbase+2)
        for r in rows:
            q=r['proposed_body_bounds_mm'];cx=(q[0]+q[3])/2
            for x in (cx-12,cx+12):
                for y in (q[1]-1.7,q[4]-.1):rect(sk,x-1.75,y,3.5,1.8,'Parameters.SourceFixtureSlotWidth')
        b.Tip=feature(b,'Pocket',side+'BodyTiePass',sk,'Parameters.SourceFixtureThickness')
        sk=sketch(b,side+'InputRiserPlan',zbase+2)
        if sign>0:
            for x in (-82.5,1.5):rect(sk,x-2,63.5,4,2)
            riser_top=96.99
        else:
            for x in (3.25,17.5):rect(sk,x-2,-67.75,4,2)
            riser_top=95.99
        b.Tip=feature(b,'Pad',side+'InputRisers',sk,riser_top-(zbase+2))
        sk=sketch(b,side+'InputSeatsPlan',riser_top)
        if sign>0:
            for x in (-82.5,1.5):rect(sk,x-5,62.75,10,9)
        else:rect(sk,-1.75,-74.725,24.25,9)
        b.Tip=feature(b,'Pad',side+'InputSeats',sk,2)
        if sign>0:
            sk=sketch(b,side+'InputTiePassPlan',98.99)
            for x in (-82.5,1.5):
                for q in (x-5,x+3.5):rect(sk,q,65.5,1.5,3.5)
            b.Tip=feature(b,'Pocket',side+'InputTiePass',sk,2)
            sk=sketch(b,'CurrentPiBridgePostPlan',zbase+2)
            for x in (-55,31):rect(sk,x-2,67,4,2)
            b.Tip=feature(b,'Pad','CurrentPiBridgePosts',sk,95-(zbase+2))
            sk=sketch(b,'CurrentPiBridgePlan',93)
            for x in (-55,31):rect(sk,x-2,67,4,6)
            b.Tip=feature(b,'Pad','CurrentPiBridges',sk,2)
            sk=sketch(b,'CurrentPiPostPlan',95)
            for x in (-55,31):rect(sk,x-2,69,4,4)
            b.Tip=feature(b,'Pad','CurrentPiPosts',sk,111.99-95)
            sk=sketch(b,'CurrentPiBeamPlan',111.99);rect(sk,-67,69,100,4)
            b.Tip=feature(b,'Pad','CurrentPiBeam',sk,2)
            sk=sketch(b,'CurrentPiSeatsPlan',111.99)
            for x in (-32.68,-61.68):rect(sk,x-4.5,71,9,15.5)
            b.Tip=feature(b,'Pad','CurrentPiSeats',sk,2)
            sk=sketch(b,'CurrentPiSmallSeatPlan',113.99);rect(sk,-66.18,71,9,6.5)
            b.Tip=feature(b,'Pad','CurrentPiSmallSeat',sk,.7)
            sk=sketch(b,'CurrentPiTiePassPlan',114.69)
            for x in (-32.68,-61.68):
                for y in (69.3,77.6):rect(sk,x-1.75,y,3.5,1.7,'Parameters.SourceFixtureSlotWidth')
            b.Tip=feature(b,'Pocket','CurrentPiTiePass',sk,2.7)
    def native():
        d.recompute();result={}
        for b in [rail]+bodies:
            assert b.Shape.isValid() and len(b.Shape.Solids)==1 and not b.Shape.check(True),b.Name
            assert all('Invalid' not in o.State and 'Touched' not in o.State for o in b.Group),b.Name
            assert all(s.FullyConstrained and s.solve()==0 for s in b.Group if s.TypeId=='Sketcher::SketchObject'),b.Name
            result[b.Name]=dict(volume_mm3=b.Shape.Volume,tip=b.Tip.Name,bounds_mm=bounds(b.Shape))
        return result
    initial=native();p.SourceFixtureThickness=2.5;changed=native()
    assert all(changed[b.Name]['volume_mm3']>initial[b.Name]['volume_mm3'] for b in bodies)
    p.SourceFixtureThickness=2;restored=native()
    assert all(abs(restored[n]['volume_mm3']-r['volume_mm3'])<1e-5 for n,r in initial.items())
    material={};reservations={}
    for doc in (d,ctx):
        for ob in doc.Objects:
            if 'Shape' not in ob.PropertiesList or ob.Shape.isNull():continue
            if doc is d and ob in [rail]+bodies:continue
            if doc is d and (ob.TypeId in ('PartDesign::Body','App::Link') or ob.Name.endswith('NominalPCB') or ob.Name.startswith('BUSsupplier')):
                material[doc.Name+'/'+ob.Name]=ob.Shape
            elif doc is ctx and (ob.Name.startswith(('P0_','S1_ring_','S1_screw_')) or ob.Name in ('LeftRiserWithMain','RightRiser','MainSupplierFamily')):
                material[doc.Name+'/'+ob.Name]=ob.Shape
            elif ob.Name.endswith('_CP2') and ob.Name!='MAIN4853_CP2' and not ob.Name.startswith(('W0','F_PI_','F_AUX_','F_HP_','F_HY_','F_TY_','Access_','Corridor_')):
                if doc is ctx and d.getObject(ob.Name) is not None:continue
                s=ob.Shape.copy()
                if doc is ctx and ob.Name in ('Pi4_CP2','BUS_CP2','PWM9685_CP2','AUX4092_CP2','PWM1608_CP2'):
                    s.translate(A.Vector(0,0,5.72 if ob.Name in ('Pi4_CP2','BUS_CP2') else 4.72))
                reservations[doc.Name+'/'+ob.Name]=s
    for group in (d.NominalMountHardware,d.SideMountHardware,d.U1NominalMountHardware):
        for ob in group.Group:material['hardware/'+ob.Name]=ob.Shape
    neighbours=targets(A,Part,plan)
    from open_prototype_source_service import pi_service_route
    pi_objects,pi_route=pi_service_route(A,Part);neighbours.update(pi_objects)
    (OUT/'source-service-route.json').write_text(json.dumps(pi_route,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    ties=tie_shapes(A,Part,plan)
    new={b.Name:b.Shape for b in bodies};new.update(ties)
    accesses={}
    for r in plan['source_plan']:
        q=r['proposed_body_bounds_mm'];cx=(q[0]+q[3])/2;cy=(q[1]+q[4])/2
        accesses[r['holder']+'_ATO_tool_budget']=Part.makeBox(22,10,35,A.Vector(cx-11,cy-5,q[5]))
    contacts=[];errors=[];pairs=0
    def check(name,s,others):
        nonlocal pairs
        for n,t in others.items():
            if not s.BoundBox.intersect(t.BoundBox):continue
            pairs+=1
            try:
                assert s.isValid() and t.isValid();hit=s.common(t);assert hit.isValid()
                if hit.Volume>1e-5:contacts.append(dict(a=name,b=n,volume_mm3=hit.Volume,bounds_mm=bounds(hit)))
            except Exception as e:errors.append(dict(a=name,b=n,error=str(e)))
    for name,s in new.items():
        check(name,s,dict(material,**reservations,**neighbours))
    for i,(name,s) in enumerate(new.items()):
        check(name,s,{n:t for j,(n,t) in enumerate(new.items()) if j>i})
    # Nominal ATO budget is checked after CUTTING only the body's2 ties;
    # no claim that this is the actual unknown lid trajectory.
    for name,s in accesses.items():
        check(name,s,dict(material,**reservations,**neighbours,
            **{n:t for n,t in new.items() if not n.startswith(name.split('_ATO')[0]+'_body_tie')}))
    # Include current changed HP against retained inputs/Pi; no repeated
    # historical4-input audit against unrelated whole-robot geometry.
    for name in ('F_HP_body_budget','F_HP_input'):
        check(name,neighbours[name],dict(material,**reservations,
            **{n:t for n,t in neighbours.items() if n!=name}))
    for name,s in pi_objects.items():
        # Intentional sleeve overlap only its2 insulation intervals, as in
        # retained joint recipe. Do not waive any mount/other-wire contacts.
        check(name,s,dict(material,**reservations,
            **{n:t for n,t in neighbours.items() if n not in pi_objects}))
    for n,s in dict(neighbours,**ties,**accesses).items():
        if d.getObject(n+'_CurrentReference'):raise AssertionError('Duplicate reference')
        ob=d.addObject('Part::Feature',n+'_CurrentReference');ob.Shape=s
        ob.addProperty('App::PropertyString','Qualification');ob.Qualification='Read-only budget/sweep; supplier lid, wire OD and bent ties not physical validation'
    bearing=[]
    for side,sign in [('left',1),('right',-1)]:
        link=d.SideRail1 if sign>0 else d.SideRail2
        for x in plan['fixture_anchors'][side]:
            probe=Part.makeBox(8,4,.05,A.Vector(x-4,69 if sign>0 else -73,92.95))
            hit=probe.common(link.Shape);assert hit.isValid() and hit.Volume>.25
            bearing.append(dict(side=side,x_mm=x,area_mm2=hit.Volume/.05))
    exports={}
    if not (contacts or errors):
        for b in [rail]+bodies:
            mesh=MeshPart.meshFromShape(Shape=b.Shape,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
            assert mesh.isSolid() and not mesh.hasNonManifolds()
            bb=b.Shape.BoundBox;assert max(bb.XLength,bb.YLength,bb.ZLength)+10<256
            dest=OUT/(b.Name+'.stl');mesh.write(str(dest));exports[dest.name]=sha(dest)
        d.saveAs(str(MODEL))
    result=dict(status='FIVE_HOLDER_FIXTURES_NOMINAL_PREPARATION_CHECKED' if not(contacts or errors) else 'SHARED_FIXTURES_REQUIRE_CHANGE',
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (PLAN,SOURCE,Path(__file__),
            ROOT/'tools/cad/open_prototype_source_service.py',OUT/'source-service-route.json')},
        native_sha256=sha(MODEL) if MODEL.exists() else None,native_bodies=restored,
        contacts=contacts,errors=errors,tested_pairs=pairs,bearing=bearing,exports=exports,
        parameter_trial='SourceFixtureThickness2->2.5->2 changes both carriers; datum/restoration checked',
        two_native_carriers=True,five_body_budgets_not_measured=True,ATO_tool_budgets_not_lid_motion=True,
        additional_ties=18,retained_Pi_wire_ties=2,removed_Pi_rail_ties=2,
        this_source_scope_ties=20,local_added_screws=0,whole_stage_completed=False,
        access_reservations_not_solid_parts=True,
        access_sharing='ATO tools used sequentially; inherited Access_/Corridor_ budgets are not material',
        selected=False,stage_completed=False,physical_pass=False,
        worker_wall_seconds=time.monotonic()-tick,finished_utc=datetime.now(timezone.utc).isoformat())
    PROOF.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','contacts','errors','bearing','worker_wall_seconds')}),flush=True)
    A.closeDocument(ctx.Name);A.closeDocument(d.Name)


if __name__=='__main__':main()
