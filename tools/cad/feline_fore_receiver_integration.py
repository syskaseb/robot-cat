"""One coupled receiver/deck revision; no moved electrical terminal/SKU.

FR moves an accounting/routing boundary20mm into the inner gallery, retaining
its original frame root. FL stays fixed; its tie head faces inward. The F_HY
custom saddle faces outward. Trim the entire unused deck overhang, not a
notch through a purchased component. Full routing/stock remain later gates.
"""
import hashlib
import math
import json
import sys
import time
import zipfile
from pathlib import Path
from types import SimpleNamespace
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_central_pi_wedge import packed
from feline_s1_flexible_fans import saddle_shapes
from feline_fore_power_pair import SolidQueries,all_current_blockers


NAMES={'BundleCuff:FR','BundleTie:FR','BundleTie:FRHead','BundleTie:FL','BundleTie:FLHead',
       'StructureReserve:BankBed-1','StructureReserve:Post-69_-1','Ref_Material_F_R1_CP2_Housing_0_0'}
NAMES.add('Ref_Material_P0_MountFrontR_0_0')


def box(lo,hi):return Part.makeBox(*(b-a for a,b in zip(lo,hi)),A.Vector(*lo))


def inputs():
    parts={};meta={};pins={}
    for filename in ('n01-full-material-scene.json','n01-lower-bay-world-probe.json',
                     'n01-common-restraint-world-probe.json','n01-remaining-selected-inventory.json'):
        path=OUT/filename;doc=json.loads(path.read_text());bundle=ROOT/doc['bundle']
        assert sha(bundle)==doc['bundle_sha256'];pins[path.relative_to(ROOT).as_posix()]=sha(path)
        with zipfile.ZipFile(bundle) as z:
            for r in doc['parts']:
                if r['name'] not in NAMES:continue
                blob=z.read(r['entry']);assert hashlib.sha256(blob).hexdigest()==r['sha256']
                s=Part.Shape();s.importBrepFromString(blob.decode());parts[r['name']]=s;meta[r['name']]=r
    assert set(parts)==NAMES,(NAMES-set(parts))
    return SimpleNamespace(parts=parts,meta=meta,pins=pins)


def proposal(world,supported_root=False):
    src=OUT/('n01-fore-receivers-integrated.json' if supported_root else 'n01-supported-fore-layout.json');parent,parts,records=packed(src)
    assert parent['PWM_root_ownership_reconciliation']['all37_added_material_checks']
    groups={n:r['group'] for n,r in records.items()};kinds={n:r['kind'] for n,r in records.items()}
    retire=set(parent['retired_whole_owners']);changes=[];endchanges=[];relations=[]
    def put(n,s,group,kind):
        assert s.isValid() and s.Solids,n
        parts[n]=s;groups[n]=group;kinds[n]=kind;retire.add(n);changes.append(n)
    # Keep full support under the first actual housing; remove the ENTIRE
    # unnecessary fore overhang which was occupying the switch's key bay.
    name='StructureReserve:BankBed-1';old=world.parts[name];bb=old.optimalBoundingBox()
    fore=world.parts['Ref_Material_F_R1_CP2_Housing_0_0'].optimalBoundingBox().XMin-1.25
    deck=box([fore,bb.YMin,bb.ZMin],[bb.XMax,bb.YMax,bb.ZMax])
    assert deck.cut(old).Volume<1e-5
    if not supported_root:put(name,deck,'NegativeBankDeck','rectangular_reservation')
    for i in range(1,7):relations.append(dict(part=name,other=f'Ref_Material_F_R{i}_CP2_Housing_0_0',
        kind='ZERO_PENETRATION_BOTTOM_BEARING',plane_Z_mm=bb.ZMax))
    # Nine MAX-OD3.1 jackets at unchanged3.6mm pitch. This routing cuff does
    # not replace the independent individual termination relief at WAGO.
    path=OUT/'n01-current-endpoint-packet-r3.json';packet=json.loads(path.read_text())
    ends=[r for r in packet['endpoints'] if r['group']=='NineWireCuffFR'];assert len(ends)==9
    x0=-75.5;x1=x0+9;y=-30.;z=70.
    if supported_root:
        # Whole routing station above the complete fixed mount AND its tie,
        # with a nominal3mm handling clear-zone, not a sub-mm witness nudge.
        z=math.ceil(world.parts['Ref_Material_P0_MountFrontR_0_0'].optimalBoundingBox().ZMax+3+8.6)
    cavity=box([x0-1,y-5.35,z-5.35],[x1+1,y+5.35,z+9])
    cuff=box([x0,y-7.35,z-7.35],[x1,y+7.35,z+7.35]).cut(cavity)
    oldc=world.parts['BundleCuff:FR'];b=oldc.optimalBoundingBox()
    retained=oldc.cut(box([b.XMin-1,b.YMin-1,b.ZMin-1],[b.XMax+1,y-7.35,b.ZMax+1])).cut(cavity)
    bond=None
    if supported_root:
        post=world.parts['StructureReserve:Post-69_-1'];pb=post.optimalBoundingBox()
        oldbond=oldc.common(post);assert oldbond.isValid() and oldbond.Volume>0
        bottom=oldbond.optimalBoundingBox().ZMin
        # Full6x9mm side face on the UNCHANGED post, rather than the earlier
        # .35mm sliver. Keep all new material at least1.5mm above P0 top.
        lo=[pb.XMin,pb.YMax-1.55,bottom];hi=[pb.XMax,pb.YMax,bottom+9]
        side=box([pb.XMin,pb.YMax-1.55,bottom],[x1+.5,y-5.35,bottom+9])
        retained=retained.fuse(side).cut(cavity)
        bond=dict(part='BundleCuff:FR',other='StructureReserve:Post-69_-1',kind='NAMED_POST_SIDE_BOND',
            intersection_bounds_mm=[lo,hi],expected_union_mm3=(pb.XLength*1.55*9),
            side_face_area_mm2=pb.XLength*9,old_union_mm3=oldbond.Volume,post_unchanged=True,
            strength_and_native_connection_NOT_physical_PASS=True)
    slot=box([(x0+x1)/2-1.45,y-9,z+5.15],[(x0+x1)/2+1.45,y+9,z+6.35])
    cuff=cuff.cut(slot).fuse(retained).removeSplitter()
    assert cuff.isValid() and len(cuff.Solids)==1,('FR cuff/root disconnected',len(cuff.Solids))
    put('BundleCuff:FR',cuff,'FRBodyReceiver','frame_reservation')
    band=world.parts['BundleTie:FR'].copy();band.translate(A.Vector(0,20,0))
    if supported_root:band.translate(A.Vector(0,0,z-70))
    put('BundleTie:FR',band,'FRBodyReceiver','project_stock_reservation')
    head=world.parts['BundleTie:FRHead'].copy()
    target_y=y+10.65;head.translate(A.Vector(0,target_y-head.BoundBox.Center.y,z-70))
    put('BundleTie:FRHead',head,'FRBodyReceiver','project_stock_reservation')
    relations.extend([dict(part='BundleTie:FR',other='BundleTie:FRHead',kind='SAME_NAMED_TIE_BUDGET'),
        bond or dict(part='BundleCuff:FR',other='StructureReserve:Post-69_-1',kind='RETAINED_ROOT_SUBSET',
             old_cuff_source='n01-common-restraint-world-probe.json')])
    for e in ends:
        q=A.Vector(*e['point_mm'])+A.Vector(0,20,z-70);d=A.Vector(*e['departure_axis'])
        name='End:'+e['id'];put(name,Part.makeCylinder(1.55,9,q,d),'FRBodyReceiver','proposal_wire')
        endchanges.append(dict(id=e['id'],wire=e['wire'],point_mm=list(q),departure_axis=list(d),
            complete9mm_routing_land=True,jacket_radius_space_budget_mm=1.55,
            maximum_OD_budget_is_not_new_SKU=True,delta_mm=[0,20,z-70],
            matching_moving_boundary_must_use_same_point=True,new_connector_or_splice=False))
    # FL electrical interfaces and cuff stay fixed. Change WHOLE strap-head
    # side; its body already has both complete axial strap clearances.
    name='BundleTie:FLHead';head=world.parts[name].copy()
    if supported_root:
        centre=head.BoundBox.Center;rot=A.Rotation(A.Vector(1,0,0),90)
        head.Placement=A.Placement(centre-rot.multVec(centre),rot)*head.Placement
        target=A.Vector(centre.x,50,world.parts['BundleTie:FL'].BoundBox.ZMax+2.5-.2)
        head.translate(target-head.BoundBox.Center)
    else:head.translate(A.Vector(0,-21.3,0))
    put(name,head,'FLBodyTie','project_stock_reservation')
    relations.append(dict(part=name,other='BundleTie:FL',kind='SAME_NAMED_TIE_BUDGET'))
    # F_HY's custom jacket/loop stays byte-identical; face the full saddle,
    # strap and head away from the FL routing cuff, not into its sidewall.
    e=next(r for r in parent['shared_fore_units']['F_HY_full_factory_ports'] if r['side']=='out')
    start,end=(A.Vector(*p) for p in e['custom_grip9_mm']);axis=end-start;axis.normalize()
    row=dict(grip_start_mm=list(start),grip_axis=list(axis),jacket_radius_mm=1.55)
    if not supported_root:
        for kind,s in saddle_shapes(row,270,270).items():
            put('ForeFHAC:out:custom:'+kind,s,'ForeFHAC',
                'proposal_material' if kind=='saddle' else 'project_stock_reservation')
    return parts,groups,kinds,dict(status='COUPLED_FORE_RECEIVER_DECK_PROPOSAL',selected=False,N01_complete=False,physical_pass=False,
        reuse_original_S1_pose=False,retired_whole_owners=sorted(retire),changed_parts=changes,
        equivalent_prior_packet=src.relative_to(ROOT).as_posix(),equivalent_prior_packet_sha256=sha(src),
        planned_own_relations=relations,FR_accounting_boundary_changes=endchanges,
        source_factory_4MTA_parts_and_both_sides_unchanged=True,FR_continuity_no_added_electrical_boundary=True,
        negative_deck_new_fore_X_mm=fore,negative_deck_is_subset_of_old_reservation=True,
        FR_post_unchanged_and_root_replaced_as_explicit_side_bond=bool(supported_root),
        FR_old_frame_root_subset_only=not supported_root,
        FR_full_side_bond=bond,FR_routing_Z_from_full_mount_and_tie=z,
        full_constant_length_moving_looms_and_stock_NOT_qualified=True,
        shared_fore_units=parent['shared_fore_units'],PWM_root_ownership_reconciliation=parent['PWM_root_ownership_reconciliation'],
        source_sha256={**world.pins,**{p.relative_to(ROOT).as_posix():sha(p) for p in (src,path,Path(__file__))}},
        open=['Actual body49/shared six-source fan allocation','Reconcile all246currentends and both ends4MTA',
              'Changed FR continuous moving-boundary corridor/length and current body custom middles',
              'Full root/operator/tools/assembly and true contour; no N01 from only this revision'])


def main():
    from feline_candidate_collision_scene import Scene
    supported_root='--supported-root' in sys.argv
    tick=time.monotonic();dest=OUT/('n01-fore-receivers-supported.json' if supported_root else 'n01-fore-receivers-integrated.json');assert not dest.exists()
    # Cheap own-interface constructor before the large frozen scene.
    pilot=proposal(inputs(),supported_root);assert len(pilot[3]['FR_accounting_boundary_changes'])==9
    world=Scene();parts,groups,kinds,doc=proposal(world,supported_root)
    archive=dest.with_suffix('.breps.zip');rows=[]
    parent=json.loads((ROOT/doc['equivalent_prior_packet']).read_text())
    parentrows={r['name']:r for r in parent['parts']}
    # Import/export is not byte-stable for all OCC surfaces. Preserve the
    # original verified blob for every UNMODIFIED actor instead of defeating
    # all pair caches merely by serializing it a second time.
    with zipfile.ZipFile(ROOT/parent['bundle']) as sourcezip,zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for i,(n,s) in enumerate(parts.items()):
            if n in parentrows and n not in doc['changed_parts']:
                pr=parentrows[n];raw=sourcezip.read(pr['entry']);assert hashlib.sha256(raw).hexdigest()==pr['sha256']
            else:raw=s.exportBrepToString().encode()
            entry=f'{i:03d}.brep';z.writestr(entry,raw)
            rows.append(dict(name=n,group=groups[n],kind=kinds[n],entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    doc.update(bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),parts=rows,worker_seconds=round(time.monotonic()-tick,3))
    dest.write_text(json.dumps(doc,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(parts=len(parts),changed=doc['changed_parts'])),flush=True)
    all_current_blockers(dest,world)


if __name__=='__main__':
    import os
    print('WORKER_PID',os.getpid(),flush=True)
    main()
