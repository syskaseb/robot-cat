"""Finish both insulation restraints and the JR-to-silicone splice reservation.

Only the demonstrated new rigid splice pocket changes the R3 Fork. Saved
R3 route rows are inherited by exact material-subset proof, not rerun.
"""
import sys,json
from pathlib import Path
import head_complete_yaw_transitions_r1 as B
sys.path.insert(0,str(B.ROOT/'tools/cad'))
import head_jr_support_r5 as CAD
P=B.ROOT/'hardware/cad/studies/head-yaw-end-restraints-r1'
OUT=B.ROOT/'hardware/cad/studies/head-yaw-end-restraints-r2'
ROUTE=B.ROOT/'hardware/electronics/full-cat/head-complete-yaw-transitions-r3'
FACTORY=B.ROOT/'hardware/electronics/full-cat/head-factory-lead-storage-r3'

def main():
    OUT.mkdir(exist_ok=True); assert not (OUT/'checks.json').exists();CAD.OUT=OUT
    parent=json.loads((ROUTE/'checks.json').read_text());assert not parent['hits'] and parent['moving_radius_sample_bound_met']
    old=B.load(P/'ForkYawEndSeat.brep')
    pocket=[-181.5,95.5,137,-172.9,123.5,139]
    plan=dict(status='SOURCE_BEFORE_RIGID_SPLICE_POCKET',pocket_mm=pocket,
      reservation='Three staggered individually insulated lap splices, centersY100/108/116 on rigid yaw arm; joint/sleeve length reservation<=8mm each and assembled bundleOD<=7mm. No solder joint in the260mm flex zone or under ties.',
      JR_extension='Retain one Kamami586761 mating end. Cut only extension tails after dry-fit; factory servo250mm remains intact. Factory crimp to rigid anchor budget about100mm; splice takeoffs staggered before that anchor.',
      ends=['JR pin1 GND -> HELU23301 black0.5mm2','JR center pin2 AUX6V -> HELU23302 red0.5mm2','JR pin3 PWM -> silicone0.12mm2 candidate'],
      insulation='Existing P0 heatshrink assortment; choose loose bore that slides over actual lap joint and recovered bore that grips insulation. Exact contents/SKU unresolved in complete-phase1 ledger; no new purchase or manufactured sleeve assumed.',
      assembly=['Fit cover and Fork unpowered with head open.','Lay JR extension around two rigid R12.6 arcs, then over rigid arm.','Stagger solder jointsY100/108/116; heatshrink each separately, no common sleeve adding unknown diameter.','One ordinary T18I holds moving insulation atY130 and another holds fixed insulation atY136. Cut ties and unplug JR before cover removal.','Deburr slots and pocket0.5mm; route flexible zone outside all shells; no journal/bearing cable.','Preserve260mm free moving length plus fit allowance; do not pull taut.'],
      source_sha256={p.relative_to(B.ROOT).as_posix():B.R.sha(p) for p in (P/'ForkYawEndSeat.brep',P/'CoverYawEndSeat.brep',ROUTE/'checks.json')},
      new_stls=1,replacement_only=True,physical_pass=False,phase1_complete=False)
    CAD.dump('plan.json',plan)
    fork,geom=CAD.build('ForkYawEndSeatSplices',old,[],[pocket])
    assert B.R.volume(fork.cut(old))<1e-5
    # A conservative whole-splice envelope includes staggered joints and sleeves.
    splice=B.Part.makeCylinder(3.5,28,B.vec([-177.2,95.5,141]),B.vec([0,1,0]))
    before=B.R.volume(splice.common(old));after=B.R.volume(splice.common(fork))
    assert before>0 and after<1e-5
    rows=[dict(target='splice',owner='new_fork',hit_mm3=after)]
    added=fork.cut(B.load(B.ROOT/'hardware/cad/studies/head-jr-support-r5/ForkJRHolder.brep'))
    # Only the newly constructed outer arm and fixed cover-seat material.
    cover=B.load(P/'CoverYawEndSeat.brep');cover_add=cover.cut(B.load(B.ROOT/'hardware/cad/studies/head-external-wire-support-r1/CoverHeadWirePassage.brep'))
    for i in range(8):
        factory=B.load(FACTORY/f'LeadEnvelope{i}.brep')
        for target,s in [('new_arm',added),('splice',splice)]:
            separated=not B.R.overlap(s.BoundBox,factory.BoundBox)
            rows.append(dict(target=target,owner='factory_lead'+str(i),hit_mm3=0 if separated else B.R.volume(s.common(factory)),bounded_bbox=separated))
        for yaw in (-15,0,15):
            f=B.mv(factory,yaw);separated=not B.R.overlap(cover_add.BoundBox,f.BoundBox)
            rows.append(dict(target='cover_seat',yaw=yaw,owner='factory_lead'+str(i),hit_mm3=0 if separated else B.R.volume(cover_add.common(f)),bounded_bbox=separated))
    for pitch in (-10,0,5):
        for name in ('FrontLeft','Rear','Nose','EarL','EarR','CageBase','CageRetainerLeft','CageRetainerRight'):
            s=B.mv(B.load(B.CACHE/(name+'_REST.brep')),0,pitch)
            for target,part in [('new_arm',added),('splice',splice)]:
                for i,solid in enumerate(s.Solids):
                    separate=not B.R.overlap(part.BoundBox,solid.BoundBox)
                    rows.append(dict(target=target,owner=name,pitch=pitch,solid=i,hit_mm3=0 if separate else B.R.volume(part.common(solid)),bounded_bbox=separate))
    hits=[x for x in rows if x['hit_mm3']>1e-5]
    CAD.dump('checks.json',dict(status='END_TRANSITIONS_AND_SPLICES_CANDIDATE' if not hits else 'REJECTED',
      geometry=geom,added_to_previous_fork_mm3=B.R.volume(fork.cut(old)),
      inherited_route_rows=len(parent['rows']),route_parent_sha256=B.R.sha(ROUTE/'checks.json'),
      before_pocket_splice_hit_mm3=before,rows=rows,hits=hits,new_stls=1,physical_pass=False,phase1_complete=False,
      remaining=['Central feeds to fixed end and fixed yaw-servo feed','Exact heatshrink contents and moving-PWM SKU in whole phase1 ledger','Actual delivered joints, wire flexibility and PETG load/fit in phase2']))
    print(json.dumps(dict(hits=hits,checks=len(rows),inherited_route_rows=len(parent['rows']))),flush=True)
if __name__=='__main__': main()
