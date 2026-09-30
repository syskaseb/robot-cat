"""One stationary yaw-servo feed, retained factory lead and integral JR seat.

Factory dimensions remain delivery assumptions, not fabricated measurements.
Save native source before changed interfaces are intersected.
"""
import sys,json,math
from pathlib import Path
import xb11_upstream_route as R
import head_complete_yaw_transitions_r1 as B
sys.path.insert(0,str(R.ROOT/'tools/cad'))
import head_jr_support_r5 as CAD
from check_main_p0_placement import SavedShapes,prop
A,Part,ROOT=R.A,R.Part,R.ROOT
OUT=ROOT/'hardware/cad/studies/head-fixed-yaw-feed-r1'
SOURCE=ROOT/'hardware/cad/studies/head-p7/yaw-r1/YawCarrier.FCStd'
FACTORY_ROUTE_LENGTH=220
EXTRA_ADDS=[]
EXTRA_CUTS=[]
def dump(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def tube(edge,r=math.hypot(1.75,.9)):
    s=Part.Wire([edge]).makePipeShell([Part.Wire([Part.makeCircle(r,edge.valueAt(edge.FirstParameter),edge.tangentAt(edge.FirstParameter))])],True,False)
    assert s.isValid() and len(s.Solids)==1
    return s
def main():
    OUT.mkdir(exist_ok=True);assert not (OUT/'checks.json').exists()
    D=(FACTORY_ROUTE_LENGTH+112.2+135-math.pi*22)/2
    plan=dict(status='SOURCE_BEFORE_COMPLETE_STATIONARY_JR_FEED',source_sha256=R.sha(SOURCE),
      factory_length_mm=250,reserved_centerline_length_mm=FACTORY_ROUTE_LENGTH,uncut_fit_budget_mm=250-FACTORY_ROUTE_LENGTH,factory_flat_profile_mm=[1.8,3.5],factory_route_radius_mm=22,
      start_mm=[-112.2,-12.8,60.2],end_mm=[-135,-56.8,60.2],U_turn_x_mm=-D,
      factory_basis='250mm manufacturer nominal lead length, flat3.5x1.8 and takeoff position provisional from saved servo/Carrier CAD. Reserve220mm centerline plus30mm end/slack budget; not factory fit or exact connector-end length claim.',
      JR_bbox_mm=[-135,-62.8,55.2,-105,-50.8,65.2],JR_basis='Same30x12x10 provisional mating-pair reservation as selected pitch; permanent yaw frame, not rotating horn.',
      wires=['XB12 F_HY.out -> C_HY.V+ redHELU23302 0.5 AUX6', 'XB13 G_AUX.3 -> C_HY.GND blackHELU23301 0.5 power return','XS13 U1/R1.2 -> C_HY.PWM yellowHELU23308 0.5 PWM5'],
      additions_mm=[[-123,-18,49,-119,-14,55.2],[-123,-50,52.2,-119,-14,55.2],[-143,-68,52.2,-97,-45.6,55.2],[-149,-61.8,55.2,-139,-51.8,57.5]]+EXTRA_ADDS,
      cuts_mm=[[x-1,y-2,51.5,x+1,y+2,56] for x in (-130,-108) for y in (-66,-47.6)]+EXTRA_CUTS,
      assembly=['Install modified Carrier on existing yaw base before head/body closure.','Slide servo from -X with lead lying through existing side-open channel; do not force plug through thin channel.','Lay factory250mm in the specified stationary U before fitting JR pair into integral seat.','Label GND/center6V/PWM and verify delivered pinout unpowered. Retain JR housing with two T18I through paired holes; do not crush contacts.','Keep all later extension-tail splices on rigid insulation supports, never factory lead cutting.'],
      service='Disconnect JR and cut replaceable housing ties before side-removing servo; unchanged M2/M3 recipe. Check whole route and hand access after delivery.',
      print='One replacementYawCarrier x1 PETG, foot on bed, brim5. No net part increase/new screws. Native nominal geometry not strength qualification.',
      new_ties=2,new_stls=1,physical_pass=False,phase1_complete=False,
      risk='Long stationary factory U extends forwards beyond head silhouette; verify floor/leg/snags unpowered. Not autonomous/home-tested.')
    dump('plan.json',plan)
    d=A.openDocument(str(SOURCE));base=d.getObject('Carrier').Shape.copy();servo=d.getObject('ServoReference').Shape.copy();A.closeDocument(d.Name)
    CAD.OUT=OUT
    carrier,geometry=CAD.build('YawCarrierJRSeat',base,plan['additions_mm'],plan['cuts_mm'])
    dump('native-geometry.json',geometry)
    edges=[Part.makeLine(A.Vector(-126,-12.8,60.2),A.Vector(-D,-12.8,60.2)),B.arc([-D,-34.8,60.2],[-D,-12.8,60.2],[-D-22,-34.8,60.2]),B.arc([-D,-34.8,60.2],[-D-22,-34.8,60.2],[-D,-56.8,60.2]),Part.makeLine(A.Vector(-D,-56.8,60.2),A.Vector(-135,-56.8,60.2))]
    segments=[('factory_exit_flat',R.box([-126,-13.7,58.45,-112.2,-11.9,61.95]))]+[('factory_U'+str(i),tube(e)) for i,e in enumerate(edges)]
    jr=R.box(plan['JR_bbox_mm']);added=carrier.cut(base)
    assert abs(sum(e.Length for e in edges)+13.8-FACTORY_ROUTE_LENGTH)<1e-6
    for n,s in segments:s.exportBrep(str(OUT/(n+'.brep')))
    rows=[]
    def check(name,s,owner,obstacle):
        for i,t in enumerate(obstacle.Solids):
            bounded=not R.overlap(s.BoundBox,t.BoundBox);v=0 if bounded else R.volume(s.common(t))
            rows.append(dict(segment=name,owner=owner,solid=i,bounded_bbox=bounded,hit_mm3=v))
    for n,s in segments:
        check(n,s,'complete_new_carrier',carrier);check(n,s,'complete_servo',servo)
    check('JR_pair',jr,'new_carrier',carrier);check('added_cradle',added,'servo',servo)
    # Fixed parts and selected revised shells, not old stock electronics Deck.
    C=B.CACHE
    fixed={'Deck':B.load(C/'Deck_REST.brep'),'Cover':B.load(ROOT/'hardware/cad/studies/head-yaw-end-restraints-r1/CoverYawEndSeat.brep')}
    for owner,t in fixed.items():
        for n,s in segments+[('JR_pair',jr),('added_cradle',added)]:check(n,s,owner,t)
    # Physical E6 wrappers streamed once, only intersecting bounding boxes.
    reader=SavedShapes();p=ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd';objects=reader.doc(p)
    assembly=objects['RobotCatAssembly24'];assert reader.placement(assembly).isIdentity()
    wrappers=[x.get('value') for x in prop(assembly,'Group').findall('.//Link') if x.get('value').startswith('Rigid_')]
    candidate=segments+[('JR_pair',jr),('added_cradle',added)]
    # Old Head/neck/Deck/electronics are replaced by selected studies, not obstacles.
    excluded=[];tested=[]
    for w in wrappers:
        n=prop(objects[w],'Group')[0][0].get('value')
        if n.startswith(('EarL','EarR','EarBolt','EarNut')) or any(word in n.lower() for word in ('head','nose','neck','shell','deck','power','pca','pololu','aux','servoyaw','servopitch')):excluded.append(n);continue
        t=reader.shape(p,n)
        if not any(R.overlap(s.BoundBox,t.BoundBox) for _,s in candidate):continue
        tested.append(n)
        for name,s in candidate:check(name,s,'E6/'+n,t)
    hits=[x for x in rows if x['hit_mm3']>1e-5]
    dump('checks.json',dict(status='REJECTED' if hits else 'STATIONARY_YAW_FEED_CANDIDATE',geometry=geometry,rows=rows,hits=hits,
      factory_length_mm=250,reserved_centerline_length_mm=FACTORY_ROUTE_LENGTH,fixture_complete=True,whole_electrical_feed_complete=False,
      original_e6_scope=dict(excluded_replaced_parts=excluded,checked_intersecting_parts=tested),
      input_sha256={SOURCE.relative_to(ROOT).as_posix():R.sha(SOURCE),**reader.hashes},
      new_stls=1,selected=False,physical_pass=False,phase1_complete=False,
      remaining=['RigidJR-tail splice seat and central F_HY/G_AUX/U1 feeds','Complete current head moving-part poses against fixed cradle/factoryU','Actual lead/pinout/flex/retention after delivery']))
    print(json.dumps(dict(hits=hits,rows=len(rows),E6_tested=tested)),flush=True)
if __name__=='__main__':main()
