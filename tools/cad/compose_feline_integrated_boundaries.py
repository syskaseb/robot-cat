"""Small upper-layout overlay, not another copied246-end register.

The parent remains immutable. Real BRep prefix caps, not grip tips, define
new routing exits. Logical internal contacts and selected parts stay intact.
"""
import copy,json,math,hashlib,zipfile,time
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json


def apply_updates(rows,updates):
    result=copy.deepcopy(rows);index={r['id']:r for r in result}
    assert len(index)==len(result)
    for name,values in updates.items():
        assert name in index,('Unknown physical boundary',name)
        assert not set(values)&{'id','wire','portion_id','endpoint','group'},'Do not change electrical/physical identity'
        index[name].update(values)
    return result


def main():
    import FreeCAD as A
    import Part
    tick=time.monotonic();basefile=OUT/'n01-shared-routing-boundaries.json';base=json.loads(basefile.read_text())
    cf=OUT/'n01-shared-Pi-carrier-r3-core-received.json';core=json.loads(cf.read_text())
    wf=OUT/'n01-shared-Pi-carrier-r3-world-received.json';world=json.loads(wf.read_text())
    assert not core['failures'] and not core['errors'] and not world['failures'] and not world['errors']
    assert world['status']=='SEPARATED_PORT_BAYS_STATIC36MOTION_RECEIVED_ROOTS_TOOLS_CAPACITY_OPEN'
    assert world.get('all_motion_received_without_static_deferral')
    assert len(base['endpoints'])==246 and len(base['portions'])==123
    arc=ROOT/core['bundle'];assert sha(arc)==core['bundle_sha256'];actors={}
    with zipfile.ZipFile(arc) as z:
        for row in core['geometry']:
            if not row['name'].startswith(('PiGPIO:','PiPower:','CurrentBUS:BUS.','Station:F_PWM_whole:')):continue
            raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());actors[row['name']]=s
    rows=base['endpoints'];updates={}
    def matching(predicate):
        result=[r for r in rows if predicate(r)];assert len(result)==1,[r['id'] for r in result];return result[0]
    def caps(s):
        faces=[f for f in s.Faces if isinstance(f.Surface,Part.Plane)]
        assert len(faces)==2 and abs(faces[0].Area-faces[1].Area)<1e-4
        return faces
    for e in core['recipe']['new_Pi_full_ends']+core['recipe']['new_BUS_DG_full_ends']:
        name=e['name'];s=actors[name];q=A.Vector(*e['point_mm'])
        end=max(caps(s),key=lambda f:(f.CenterOfMass-q).Length).CenterOfMass
        start,finish=map(lambda p:A.Vector(*p),e['full9_mm']);axis=(finish-start)/9
        assert abs((finish-start).Length-9)<1e-6
        if name.startswith('PiGPIO:'):r=matching(lambda r:r['endpoint']==name.split(':',1)[1])
        elif name.startswith('PiPower:'):
            wid=name.split(':',1)[1];r=matching(lambda r:r['wire']==wid and r['endpoint'].startswith('PI_USB_C.'))
        else:r=matching(lambda r:r['endpoint']==name.split(':',1)[1])
        update=dict(jacket_routing_point_mm=list(q),jacket_grip9_mm=e['full9_mm'],grip_axis=list(axis),grip_length_mm=9,
            routing_exit_mm=list(end),routing_exit_axis=list(axis),routing_boundary_status='CURRENT_RECEIVED_UPPER_PREFIX_AND_FULL9_GRIP',
            retained_straight_after_grip_mm=(end-finish).Length,minimum_R_mm=e['R_mm'],
            prefix_geometry_owner=name,source_prefix_length_mm=s.Volume/caps(s)[0].Area,
            supplier_datum_guaranteed=False,full_middle_route_accepted=False)
        if r['point_mm'] is not None:update['point_mm']=list(q)
        updates[r['id']]=update
    # The complete received F_PWM output rotates as one five-part kit. Its
    # internal accounting contact remains None, not a fabricated connector pin.
    r=matching(lambda r:r['endpoint']=='F_PWM.out');n='Station:F_PWM_whole:F_PWM:out_after_turn_grip';s=actors[n]
    pp=sorted([f.CenterOfMass for f in caps(s)],key=lambda p:p.x);assert abs((pp[1]-pp[0]).Length-9)<1e-6
    first=actors['Station:F_PWM_whole:F_PWM:out_first_bend'];q=min(caps(first),key=lambda f:(f.CenterOfMass-A.Vector(*core['recipe']['FPWM_pivot_mm'])).Length).CenterOfMass
    updates[r['id']]=dict(jacket_routing_point_mm=list(q),jacket_grip9_mm=[list(p) for p in pp],routing_exit_mm=list(pp[1]),
        routing_exit_axis=list((pp[1]-pp[0])/9),grip_length_mm=9,whole_factory_output_kit_preserved=True,
        routing_boundary_status='CURRENT_WHOLE_FPWM_ROTATED_OUTPUT_PREFIX',full_middle_route_accepted=False,supplier_datum_guaranteed=False)
    resolved=apply_updates(rows,updates);assert len(resolved)==246
    for a,b in zip(rows,resolved):
        if a['point_mm'] is None:assert b['point_mm'] is None,'Internal contacts must remain unassigned'
    for wid in ('W079','W080'):
        r=next(r for r in resolved if r['wire']==wid and r['endpoint'].startswith('PI_USB_C.'))
        assert abs(r['retained_straight_after_grip_mm']-(12 if wid=='W080' else 0))<1e-5
    recipe=core['recipe'];result=dict(status='CURRENT_UPPER_ENDS_COMPOSED_WHOLE_CORRIDORS_OPEN',parent_register=basefile.relative_to(ROOT).as_posix(),parent_sha256=sha(basefile),
        updates=updates,physical_portions=123,ends=246,identities_and_internal_None_contacts_preserved=True,
        unchanged_rows_referenced_not_copied=True,separate_whole_USB=dict(Pi_mouth_mm=recipe['Pi_mouth_mm'],BUS_mouth_mm=recipe['BUS_mouth_mm'],jacket_length_mm=recipe['USB_length_mm'],
            Pi_full9_mm=recipe['Pi_full9_mm'],BUS_full9_mm=recipe['BUS_full9_mm'],no_new_cut_or_connector=True),
        all_remaining_end_states_and_whole_shared_corridor_capacity_still_OPEN=True,N01_complete=False,selected=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (basefile,cf,wf,arc,ROOT/'tools/cad/compose_feline_integrated_boundaries.py')},worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-integrated-upper-boundary-overlay.json',result)
    print(json.dumps(dict(status=result['status'],updated=len(updates),ends=len(resolved),seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
