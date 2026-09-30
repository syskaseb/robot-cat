"""Complete rigid yaw JR/insulation/splice support, selected-pose interfaces."""
import json,sys
from pathlib import Path
import head_fixed_yaw_feed_r1 as F
from head_external_yaw_loop_r1 import mv
F.OUT=F.ROOT/'hardware/cad/studies/head-fixed-yaw-feed-r2'
F.EXTRA_ADDS=[[-107,-66,52.2,-65,-47.6,56.2],[-75,-61,56.2,-65,-52.6,57.2]]
F.EXTRA_CUTS=[[-145,-66,51.5,-143,-62,58],[-145,-51.6,51.5,-143,-47.6,58],[-71,-65,51.5,-69,-61,58],[-71,-51,51.5,-69,-47,58]]
def main():
    F.main()
    out=F.OUT;checks=json.loads((out/'checks.json').read_text());plan=json.loads((out/'plan.json').read_text())
    plan.update(new_ties=4,splices=dict(centerline_start_mm=[-104,-56.8,60.2],length_mm=28,max_bundle_OD_mm=7,three_staggered_lap_joints_x_mm=[-100,-92,-84],each_insulated_joint_max_length_mm=8,description='Separate insulated 22AWGJR extension-tail to0.5 SiF transitions; never cut factory lead. Rigid seat, not free cable span.'),
      tie_stations='Two JR housing ties atX-130/-108, independent factory-insulation tieX-144, SiF-insulation tieX-70;4T18I from existingbag100.',
      existing_slots='Original Carrier base and ear fastener geometry retained. Nativeaddition outside original servo path; opening both small end restraints avoids clamping joints.',
      remaining=['CentralF_HY/G_AUX/U1 feed ends from(-70,-56.8,60.2)','Actual factory slack/insulation/pinout/holding after delivery'])
    F.dump('plan.json',plan)
    carrier=F.B.load(out/'YawCarrierJRSeat.brep')
    segments=[(p.stem,F.B.load(p)) for p in out.glob('factory*.brep')]
    splice=F.Part.makeCylinder(3.5,28,F.A.Vector(-104,-56.8,60.2),F.A.Vector(1,0,0));splice.exportBrep(str(out/'RigidSpliceReservation.brep'))
    jr=F.R.box(plan['JR_bbox_mm']);adds=F.R.box([-107,-66,52.2,-65,-47.6,56.2]).fuse(F.R.box([-75,-61,56.2,-65,-52.6,57.2]))
    rows=checks['rows']
    def check(name,s,owner,t):
        for i,solid in enumerate(t.Solids):
            separated=not F.R.overlap(s.BoundBox,solid.BoundBox)
            rows.append(dict(segment=name,owner=owner,solid=i,bounded_bbox=separated,hit_mm3=0 if separated else F.R.volume(s.common(solid))))
    check('rigid_splices',splice,'complete_new_carrier',carrier)
    # Explicit retained stationary neck pieces, not omission via old E6 head exclusion.
    reader=F.SavedShapes()
    all_added=carrier.cut(reader.shape(F.SOURCE,'Carrier'))
    # Find exact saved file/object names from the selected directories if necessary.
    for folder,name in [('head-p7/yaw-support-r1','Foundation'),('head-p7/retainer-nut-seats-work','Retainer'),('head-p8/head-yaw-open-key-r1/bridge-passage-r5','Bridge')]:
        files=list((F.ROOT/'hardware/cad/studies'/folder).glob('*.FCStd'));found=[]
        for p in files:
            names=reader.doc(p)
            if name in names:found.append((p,name))
        assert len(found)==1,(folder,found)
        p,n=found[0];t=reader.shape(p,n)
        for label,s in segments+[('rigid_splices',splice),('JR_pair',jr),('complete_new_carrier',carrier)]:
            # The parent carrier/foundation contact is not a changed pair.
            if label=='complete_new_carrier':s=all_added
            check(label,s,'stationary/'+name,t)
    cache=F.B.CACHE
    shells={n:F.B.load(cache/(n+'_REST.brep')) for n in ('FrontLeft','Rear','Nose','EarL','EarR','CageBase','CageRetainerLeft','CageRetainerRight')}
    shells['FrontRight']=F.B.load(F.ROOT/'hardware/cad/studies/head-external-wire-support-r1/FrontRightWirePassage.brep')
    yawparts={'Fork':F.B.load(F.ROOT/'hardware/cad/studies/head-yaw-end-restraints-r2/ForkYawEndSeatSplices.brep'),'PitchCarrier':F.B.load(F.ROOT/'hardware/cad/studies/head-jr-support-r5/PitchCarrierThroughLeadExit.brep'),'PitchRetainer':F.B.load(cache/'PitchRetainer_REST.brep')}
    for yaw in (-15,0,15):
        for owner,t in yawparts.items():
            t=mv(t,yaw)
            for label,s in segments+[('rigid_splices',splice),('JR_pair',jr),('complete_new_carrier',carrier)]:check(label,s,owner+'/yaw'+str(yaw),t)
        for pitch in (-10,0,5):
            for owner,t in shells.items():
                t=mv(t,yaw,pitch)
                for label,s in segments+[('rigid_splices',splice),('JR_pair',jr),('complete_new_carrier',carrier)]:check(label,s,owner+'/yaw'+str(yaw)+'/pitch'+str(pitch),t)
    # Reuse actual saved remaining E6 geometry for the newly extended splice seat.
    p=F.ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd';objects=reader.doc(p)
    for w in [x.get('value') for x in F.prop(objects['RobotCatAssembly24'],'Group').findall('.//Link') if x.get('value').startswith('Rigid_')]:
        n=F.prop(objects[w],'Group')[0][0].get('value')
        if n in checks['original_e6_scope']['excluded_replaced_parts']:continue
        t=reader.shape(p,n)
        for label,s in [('rigid_splices',splice),('new_splice_seat',adds)]:
            if F.R.overlap(s.BoundBox,t.BoundBox):check(label,s,'E6/'+n,t)
    hits=[r for r in rows if r['hit_mm3']>1e-5]
    checks.update(rows=rows,hits=hits,status='REJECTED' if hits else 'COMPLETE_FIXED_JR_FACTORY_SUPPORT_CANDIDATE',script_sha256=F.R.sha(Path(__file__)),additional_source_sha256=reader.hashes,new_ties=4,
      stationary_geometry_scope='Only added attachment material versus fixedneck, sampled movinghead versus complete newCarrier/route. Central supply feeds not yet constructed.')
    F.dump('checks.json',checks);print(json.dumps(dict(rows=len(rows),hits=hits)),flush=True)
if __name__=='__main__':main()
