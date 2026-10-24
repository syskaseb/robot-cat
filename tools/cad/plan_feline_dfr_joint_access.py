"""N01 necessary space check: swing all five terminated D_FR leads together.

This does not authorize a motion or prove release of the existing comb/root.
The case is a project reservation; its overlap is a HOLD, not supplier contact.
"""
import math,time
import FreeCAD as A
import Part
from feline_solid_distance import bbox_lower_bound,distance
from receive_feline_pi_split_service_space import independent


def save_partial(path, parts, recipe, evidence):
    """Persist a non-selected planning proposal, never a whole-layout receipt."""
    import hashlib, json, zipfile
    from pathlib import Path
    path=Path(path); archive=path.with_suffix('.breps.zip'); rows=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for i,(name,shape) in enumerate(parts.items()):
            shape.check(True)
            assert shape.isValid() and len(shape.Solids)==1
            raw=shape.exportBrepToString().encode(); entry=f'{i}.brep'
            z.writestr(entry,raw)
            reopened=Part.Shape(); reopened.importBrepFromString(raw.decode())
            reopened.check(True); assert reopened.isValid()
            rows.append(dict(name=name,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),strict_reopen=True))
    report=dict(status='PARTIAL_SIDE_ACCESS_PLAN_NOT_SELECTED',selected=False,
        N01_complete=False,physical_pass=False,recipe=recipe,evidence=evidence,
        geometry=rows,bundle=archive.name,
        constructor_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        bundle_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
        open=['whole factory900 allocation at CURRENT moving seams',
              'missing current actors and moving envelopes',
              'F_R3 ATO removal prerequisite',
              'bed retained load paths and provisional adhesive qualification'])
    with path.open('w',encoding='utf-8',newline='\n') as f:
        json.dump(report,f,indent=2); f.write('\n')
    return report


def pose(scene, degrees=45):
    theta=math.radians(degrees); length=24.25; radius=length/theta
    assert 0<degrees<=90 and radius>=12.4
    parts={};ends=[]
    for port in range(1,6):
        x=25.125-(port-1)*4.75
        def point(a):
            return A.Vector(x,-32.25-radius*math.sin(a),
                            45.26-radius*(1-math.cos(a)))
        p,q=point(0),point(theta)
        edge=Part.Arc(p,point(theta/2),q).toShape()
        assert abs(edge.Length-length)<1e-7
        ring=Part.Wire([Part.makeCircle(1.55,p,A.Vector(0,-1,0))])
        s=Part.Wire([edge]).makePipeShell([ring],True,False)
        s.check(True);assert s.isValid() and len(s.Solids)==1
        parts['lead'+str(port)]=s;ends.append(list(q))
    case=independent(scene['Station:D_FR:case'])
    origin=A.Vector(15.625,-56.5,45.26)
    case.rotate(origin,A.Vector(1,0,0),degrees)
    case.translate(A.Vector(*ends[2])-origin)
    case.check(True);parts['case_reservation']=case
    return parts,dict(angle_deg=degrees,each_jacket_length_mm=length,
        bend_radius_mm=radius,fixed_portals_unchanged=True,
        all_five_terminated_together=True,
        requires_whole_comb_release_not_only_top_cap=True,
        continuous_motion_and_hand_access_qualified=False)


def necessary_space(scene,parts):
    tick=time.monotonic(); checks={};errors={}
    excluded={k for k in scene if k.startswith('Station:D_FR:')}
    for n,a in parts.items():
        for k,b in scene.items():
            if k in excluded or bbox_lower_bound(a.BoundBox,b.BoundBox)>1.25:continue
            try:
                b.check(True);assert b.isValid() and b.Solids
                gap=distance(a,b)
                checks[n+'|'+k]=dict(gap_mm=gap,clear=gap>=1.25)
            except Exception as e:errors[n+'|'+k]=str(e)
    return dict(checks=checks,errors=errors,
        holds=[k for k,v in checks.items() if not v['clear']],
        excluded_existing_station_parts=sorted(excluded),
        scope='Necessary end-pose only; no full scene, path, lever or mounting approval',
        worker_seconds=round(time.monotonic()-tick,3),N01_complete=False)


def side_access(scene):
    """Move the whole station outside the bank, not a service-angle microoffset.

    Same five purchased conductors, existing route portals and nine-mm grip.
    Each prefix needs15mm more material: factory900 total allocation is OPEN.
    Lever/hand volumes are project budgets, NOT supplier geometry.
    """
    case=independent(scene['Station:D_FR:case']);case.translate(A.Vector(0,-15,0))
    # Bottom-only adhesive support, no side ears invading adjacent FR_G.
    tray=Part.makeBox(26,39.5,2,A.Vector(2.625,-92.5,38.26))
    # Full finger/access budget plus1.25 each side, not lever-only slot.
    slot=Part.makeBox(14.5,49.75,6,A.Vector(8.375,-120,51))
    bed=scene['CurrentFoundation:BankBedCurrent:-1'].cut(slot)
    result={'case_reservation':case,'tray':tray,'slotted_bank_bed':bed}
    for port in range(1,6):
        result['lead'+str(port)]=Part.makeCylinder(1.55,39.25,
            A.Vector(25.125-(port-1)*4.75,-71.5,45.26),A.Vector(0,1,0))
    for s in result.values():
        s.check(True);assert s.isValid() and len(s.Solids)==1
    return result,dict(case_delta_mm=[0,-15,0],extra_per_lead_mm=15,
        prefix_length_mm=39.25,existing_grip_and_portals_unchanged=True,
        holding_method='Provisional bottom adhesive on0.5mm bondline; wire comb remains independent',
        original_bank_pad_region_preserved_Y_above=-67.75,
        slot_ends_at_Y=-70.25,frame_purchase_and_bank_positions_unchanged=True,
        lever_requires_F_R3_ATO_removed_before_operation=True,
        lever_envelope_is_project_assumption_not_supplier_guarantee=True,
        factory900_whole_length_allocation_received=False,
        selected=False,N01_complete=False)
