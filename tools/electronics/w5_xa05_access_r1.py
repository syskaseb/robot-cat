"""Changed XA05: two actual supports and a bare-Deck terminal sequence.

Lever/finger dimensions are explicit project allowances, NOT catalogue
measurements. Assemble before Carrier/Cover; no in-situ service claim under
Pi. The two new fixed insulation grips supersede R20's three ambiguous
interlinked XA05 ties, not three additional invisible ties.
"""
from datetime import datetime,timezone
from pathlib import Path
import sys,json,math
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/w5-xa05-access-r1'
FIT=ROOT/'hardware/electronics/full-cat/w5-xa05-native-r1/checks.json'


def main():
    import FreeCAD as A
    import Part
    from w5_r53_owners import installed
    start=datetime.now(timezone.utc)
    fit=json.loads(FIT.read_text(encoding='utf-8'))
    assert fit['status']=='XA05_NATIVE_STATIC_COMPLETE_UNSELECTED'
    assert not fit['hits'] and not fit['errors']
    assert all(sha(ROOT/k)==v for k,v in {**fit['source_sha256'],**fit['files']}.items())
    assert not (OUT/'checks.json').exists();OUT.mkdir(parents=True,exist_ok=True)
    owners,pins,omitted=installed(A,Part)
    owners.pop('CandidateDeck');owners.pop('hardware/electronics/full-cat/xa05-main-aux-return-r2/XA05_DESIGN.brep')
    cad=ROOT/'hardware/cad/studies/w5-xa05-native-r1'
    for n in ('Deck','Outrigger'):
        owners['Native'+n]=Part.read(str(cad/(n+'_WORLD.brep')))
    raw=ROOT/'hardware/electronics/full-cat/w5-xa05-outer-support-r5'
    owners['XA05']=Part.read(str(raw/'XA05_WORLD.brep'))
    children=Part.read(str(raw/'ADDITIONS_WORLD.brep')).childShapes()
    for n,s in zip(('InnerTie','OuterTie','Bolt0','Washers0','Nut0','Bolt1','Washers1','Nut1'),children[2:]):owners[n]=s
    # Explicit assembly phase: not yet fitting the Cover or removable Carrier.
    removed={k:owners.pop(k) for k in list(owners) if k=='Cover' or k=='hardware/cad/studies/pi-complete-native-r2/Carrier_WORLD.brep'}
    assert len(removed)==2,removed.keys()
    assumptions=dict(pivot_inside_mouth_mm=4,pivot_z_mm=117.2,radius_mm=14,
        width_mm=5,angle_deg=110,finger_diameter_mm=6,finger_approach_top_z_mm=138,
        basis='Project allowance from existing WAGO family installation direction; no measured hinge or finger qualification')
    hits=[];errors=[];pairs=0;files=[]
    def check(label,s,excluded):
        nonlocal pairs
        for key,t in owners.items():
            if key==excluded or not s.BoundBox.intersect(t.BoundBox):continue
            pairs+=1
            try:
                common=s.common(t)
                if common.Volume>1e-5:
                    b=common.BoundBox
                    hits.append(dict(action=label,owner=key,mm3=common.Volume,
                        bounds_mm=[getattr(b,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
            except Exception as exc:errors.append(dict(action=label,owner=key,error=str(exc)))
    for label,body,pivot,axis,side in [
        ('P0G2.5','G2_design',[120.5,5.5,117.2],[1,0,0],[0,1,0]),
        ('G_AUX.1','G_AUX_design',[114.5,-59.5,117.2],[0,1,0],[-1,0,0])]:
        p=A.Vector(*pivot);u=A.Vector(*side)
        def pt(angle):return p+u*(14*math.cos(angle))+A.Vector(0,0,14*math.sin(angle))
        a,m,b=pt(0),pt(math.radians(55)),pt(math.radians(110))
        sector=Part.Face(Part.Wire([Part.makeLine(p,a),Part.Arc(a,m,b).toShape(),Part.makeLine(b,p)])).extrude(A.Vector(*axis)*5)
        assert sector.isValid();check(label+'_continuous_lever_allowance',sector,body)
        # Above the highest lever position, before upper Carrier placement.
        center=p+u*4+A.Vector(*axis)*2.5
        finger=Part.makeCylinder(3,6.8,A.Vector(center.x,center.y,131.2))
        check(label+'_above_lever_approach',finger,body)
        for tag,s in [('LEVER_ALLOWANCE',sector),('FINGER_ALLOWANCE',finger)]:
            q=OUT/(label.replace('.','_')+'_'+tag+'.brep');s.exportBrep(str(q));files.append(q)
    intent=dict(endpoints=['P0G2.5','G_AUX.1'],net='power ground, never Pi signal-only return',
        continuous_wire='HELU23501 black1mm2 OD2.5,Rfixed15',centreline_mm=227.345310129943,
        nominal_trial_blank_mm=310,actual_cut_mm=None,strip_mm_each=11,
        supports=[dict(name='OuterTie',role='G2-side insulation retention',centre_mm=[153,-14,121]),
                  dict(name='InnerTie',role='G_AUX-side insulation retention',centre_mm=[134,-33,121])],
        historical_XA05_ties_superseded=3,new_XA05_installed_ties=2,net_installed_tie_change=-1,
        no_separate_unmodelled_endpoint_ties=True,
        assembly=['Disconnect battery/USB; assemble on bare Deck before upper Carrier/Cover.',
            'Bolt separate outrigger on Deck:2M3x12,2M3nuts,4washers; nominal stack/clearance proved by native receipt.',
            'Thread twoT18I through the actual native tunnels. Leave loose during fit.',
            'Open only P0G2.5 andG_AUX.1. Dry-fit310mm continuous black blank and mark final ends; do not stuff82mm reserve into this route.',
            'Final cut after delivery trial. Strip11mm per end, fully seat both ends, close levers, then retain insulation with OuterTie/InnerTie.',
            'Fit upper Carrier and Cover only after all lower fixed connections; wiring of other circuits remainsW5.'],
        disassembly=['Disconnect battery andUSB. Remove Cover, then the upper Carrier assembly by its existing procedure before terminal access.',
            'Support XA05, cut/release both insulation straps without nicking the wire, open the same two levers and withdraw the ends.',
            'If delivering an upper assembly cannot be removed as prescribed, keep this service claim open; no pull-through under installed Pi.'],
        phase2=['Actual WAGO mouth/lever, usable blank, tie gripping pressure and printed rail stiffness.',
            'Unpowered tug, insulation clearance and continuity; no energizing beforeE3 and fullassembly checks.'],
        actual_lever_measurements_verified=False,in_situ_under_Carrier_access_claimed=False,
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False)
    save(OUT/'interface.json',intent);files.append(OUT/'interface.json')
    pins+=[FIT,Path(__file__),raw/'checks.json',ROOT/'hardware/manufacturing/one-batch-prototype-r20/fixed-aux-interface.json']
    finish=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='XA05_LOCAL_ASSEMBLY_ACCESS_REJECTED' if hits or errors else 'XA05_NOMINAL_BARE_DECK_SEQUENCE_CLEAR',
        hits=hits,errors=errors,pairs=pairs,assumptions=assumptions,
        omitted_for_documented_assembly_phase=list(removed),not_an_installed_obstacle_waiver=True,
        inherited_other_scope='Only changed XA05 terminal actions; not qualification of all Carrier removal/wholeW5.',
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in pins},files={q.relative_to(ROOT).as_posix():sha(q) for q in files},
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds()))
    print('XA05_ACCESS',pairs,len(hits),len(errors),flush=True)


if __name__=='__main__':main()
