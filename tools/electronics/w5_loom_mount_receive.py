"""Resolve the complete received mounting receipt without moving any cable.

Only subtract front belt/head passages and cut captive pockets through the
whole Deck union. Reuse the already checked external pairs. Installed-bank
key obstruction is an assembly prerequisite, NOT waived final service access.
"""
from datetime import datetime, timezone
import json, math
from servo_fuse_inputs_r1 import save, sha
import w5_loom_mount_hardware as M

ROOT=M.ROOT; OUT=M.BASE/'w5-loom-mount-hardware-r2'


def main():
    import FreeCAD as A, Part
    start=datetime.now(timezone.utc)
    assert not (OUT/'checks.json').exists()
    read=lambda p:json.loads(p.read_text(encoding='utf-8'))
    r=read(M.OUT/'checks.json');bp=read(M.OUT/'native-blueprint.json')
    assert len(r['hits'])==20 and not r['errors']
    pins=[M.OUT/'checks.json',M.OUT/'native-blueprint.json',ROOT/'tools/electronics/w5_loom_mount_hardware.py',__file__]
    for rel,digest in {**r['source_sha256'],**r['files']}.items():
        assert sha(ROOT/rel)==digest,rel
    original=dict(zip(bp['roles'],Part.read(str(M.OUT/'MOUNT_AND_STRAPS_PROPOSED_WORLD.brep')).childShapes()))
    def box(b):return Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3]))
    def ring(x,y,ri,ro,z,h):
        return Part.makeCylinder(ro,h,A.Vector(x,y,z)).cut(Part.makeCylinder(ri,h+.2,A.Vector(x,y,z-.1)))
    def hexagon(x,y,af,z,h):
        rr=af/math.sqrt(3);v=[A.Vector(x+rr*math.cos(k*math.pi/3),y+rr*math.sin(k*math.pi/3),z) for k in range(6)]
        return Part.Face(Part.makePolygon(v+[v[0]])).extrude(A.Vector(0,0,h))
    OUT.mkdir(parents=True,exist_ok=True)
    frames={};newtools={};channels=[];hits=[];pairs=[];bearing=[]
    for leg,group in bp['groups'].items():
        cutters=[];back=1 if leg.startswith('F') else -1
        for row in group['tie_slot_and_belt_recipes']:
            x,y,_=row['axis_mm'];z=row['belt_station_z_mm']-1.5
            ann=ring(x,y,2.5,4.2,z,3)
            half=[x-4.3 if back>0 else x,y-4.3,z-.1,x if back>0 else x+4.3,y+4.3,z+3.1]
            cutters.append(ann.common(box(half)))
            hb=row['head_box_mm'];headslot=[hb[i]-.25 for i in range(3)]+[hb[i]+.25 for i in range(3,6)]
            cutters.append(box(headslot))
            channels.append(dict(loom=row['loom'],front_channel=dict(center_xy_mm=[x,y],inner_radius_mm=2.5,
                outer_radius_mm=4.2,z_mm=z,height_mm=3,half_box_mm=half),head_slot_mm=headslot,
                minimum_local_beam_below_head_slot_mm=headslot[2]-84.2,
                prototype_retention_load_and_creep_unverified=True))
        k=leg+'FixedFrame';s=original[k].cut(Part.makeCompound(cutters))
        assert s.isValid() and len(s.Solids)==1,k
        assert not (s.check(True) or []),k
        frames[k]=s;newtools[k]=cutters
        print('MOUNT_RECEIVED',k,'single_solid_BOP0',flush=True)
    deck_path=ROOT/'hardware/cad/studies/w5-central-retention-native-r1/CentralRetentionDeck_CANDIDATE_WORLD.brep'
    deck=Part.read(str(deck_path));pins.append(deck_path)
    pads=[original[k] for k in bp['roles'] if k.endswith('DeckLanding')]
    union=deck.multiFuse(pads)
    assert union.isValid() and len(union.Solids)==1,'Deck union'
    decktools=[];pocketrecipes=[]
    for row in bp['axes']:
        x,y=row['axis_mm']
        decktools.extend([Part.makeCylinder(1.7,18,A.Vector(x,y,94)),hexagon(x,y,5.9,106.3,23.2)])
        pocketrecipes.append(dict(axis_xy_mm=[x,y],AF_mm=5.9,z_mm=106.3,height_mm=23.2,
                                  applied_to_whole_union=True,top_drop_clearance_included=True))
    finaldeck=union.cut(Part.makeCompound(decktools))
    assert finaldeck.isValid() and len(finaldeck.Solids)==1,'Deck cut'
    assert not (finaldeck.check(True) or []),'Deck BOP'
    def check(label,s,owner,t):
        c=s.common(t);v=c.Volume
        pairs.append(dict(part=label,owner=owner,common_mm3=v))
        if v>1e-6:hits.append(pairs[-1])
    for row in bp['grips']:
        for tail in ('Belt','Head'):
            label=row['loom']+tail;check(label,original[label],row['owner'],frames[row['owner']])
    for row in bp['axes']:
        leg=row['leg'];x,y=row['axis_mm'];label=leg+('_Inner' if abs(y)==104 else '_Outer')
        for tail in ('Bolt','Nut','NutDrop'):
            check(label+tail,original[label+tail],'CompleteDeck',finaldeck)
        for role,target,probe in (
            ('head',frames[leg+'FixedFrame'],ring(x,y,1.7,2.75,95,.01)),
            ('nut_floor',finaldeck,hexagon(x,y,5.5,106.29,.01).cut(Part.makeCylinder(1.7,.03,A.Vector(x,y,106.28))))):
            material=probe.common(target).Volume
            bearing.append(dict(axis=label,role=role,nominal_area_mm2=probe.Volume/.01,
                                supported_area_mm2=material/.01,supported_fraction=material/probe.Volume))
            assert abs(material-probe.Volume)<max(1e-6,probe.Volume*1e-5),(label,role,material,probe.Volume)
    for i,a in enumerate(bp['grips']):
        for b in bp['grips'][i+1:]:
            for sa in ('Belt','Head'):
                for sb in ('Belt','Head'):
                    aa=a['loom']+sa;bb=b['loom']+sb
                    if original[aa].BoundBox.intersect(original[bb].BoundBox):check(aa,original[aa],bb,original[bb])
    assert not hits,hits
    rolemap={**frames,'CompleteDeck':finaldeck}
    geometry=OUT/'FRAMES_AND_COMPLETE_DECK_RECEIVED_WORLD.brep'
    Part.makeCompound(list(rolemap.values())).exportBrep(str(geometry))
    assembly=[
        'With power absent, keep the Deck on a bench BEFORE fitting the bank and its12TE-IN wire ends/straps.',
        'Drop8DIN934M3 nuts from above into pockets. Fit4fixedframes with8M3x16 from below using AF2.5 key; do this before W027/W038 input obstructions exist.',
        'Fit the assembled Deck, then assemble bank and all input ends/straps according to the frozen bank recipe. Lay continuous looms sideways and thread12T18I bands in the planned passages.',
        'InnerFL/FR frame screw service on a completed robot REQUIRES first removing the bank input obstructions. R1 proves the key cannot pass the installed W027/W038 ends. Shared bank/Deck removal sequence still pending.',
        'No claim of all-installed tool access, dynamic motion, pullout strength, PETG torque or production fit. Hand-adjust prototype; coupon and actual tool/hardware fit in phase2.'
    ]
    bp.update(correction_channels=channels,whole_deck_pockets=pocketrecipes,assembly=assembly,
              assembly_input_prerequisites=['InputR4/release_0.0_W027_DESIGN','InputR4/release_0.0_W038_DESIGN'],
              current_roles=list(rolemap),geometry=geometry.relative_to(ROOT).as_posix(),
              fixed_mount_static_received=True,all_installed_service_access=False,native_complete=False)
    save(OUT/'native-blueprint.json',bp)
    finish=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='FIXED_FRAME_MOUNT_BELTS_RECEIVED_NATIVE_PENDING',hits=hits,errors=[],
        changed_pairs=pairs,bearing_surfaces=bearing,frame_single_solids=4,Deck_single_solids=1,BOP_errors=0,
        reused_external_clear_pairs_from_R1=True,removed_material_only=True,
        installed_key_obstructions=[h for h in r['hits'] if 'LowerKeyAccess' in h['part']],
        qualified_key_state='BENCH_PRE_BANK_ONLY',all_installed_service_access=False,
        all_static_material_pairs_clear=True,native_complete=False,selected=False,W1_complete=False,W5_complete=False,
        physical_pass=False,started_utc=start.isoformat(),finished_utc=finish.isoformat(),
        worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={__import__('pathlib').Path(p).relative_to(ROOT).as_posix():sha(p) for p in pins},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in [geometry,OUT/'native-blueprint.json']}))


if __name__=='__main__':main()
