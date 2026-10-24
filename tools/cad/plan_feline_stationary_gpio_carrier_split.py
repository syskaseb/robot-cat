"""N01 removable upper Pi frame / retained lower GPIO support hypothesis."""
import time
import json, hashlib, zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from check_feline_current_gpio_release import certify
from feline_solid_distance import distance, bbox_lower_bound
from receive_feline_pi_split_service_space import independent


def construct(source):
    """One upper removable frame, lower GPIO clamp; purchased parts unchanged.

    M2 direct-PETG pilot retention is provisional, not tested strength or stock.
    Nylon clamp tightens on the connector casing, never on its individual leads.
    """
    below=source.common(Part.makeBox(600,600,404,A.Vector(-300,-300,-300)))
    lower=next(s for s in below.Solids if s.BoundBox.XMin<0)
    upper=source.cut(lower)
    bosses={side:Part.makeCylinder(2.5,h,A.Vector(-8,-11,z)).fuse(
        Part.makeCylinder(2.5,h,A.Vector(-8,-6,z))).fuse(
        Part.makeBox(5,5,h,A.Vector(-10.5,-11,z))).removeSplitter()
        for side,z,h in [('lower',98,6),('upper',104,4)]}
    lower=lower.fuse(bosses['lower']);upper=upper.fuse(bosses['upper'])
    for y in [-11,-6]:
        lower=lower.cut(Part.makeCylinder(.8,6.1,A.Vector(-8,y,98)))
        upper=upper.cut(Part.makeCylinder(1.1,4.2,A.Vector(-8,y,103.9)))
    back=Part.makeBox(12,2.5,8,A.Vector(36,-12.4818903653,84)).fuse(
        Part.makeBox(12,5,3,A.Vector(36,-12.4818903653,83)))
    front=Part.makeBox(12,2.5,8,A.Vector(36,-20.0818903653,84)).fuse(
        Part.makeBox(12,5,3,A.Vector(36,-22.5818903653,83)))
    p=A.Vector(28,3,87.3);q=A.Vector(42,-10,87.3)
    root=Part.makeCylinder(1.5,(q-p).Length,p,q-p)
    lower=lower.fuse(root).fuse(back).removeSplitter()
    result={'lower':lower,'upper':upper.removeSplitter(),'front_jaw':front.removeSplitter(),
            'housing_tie_band_budget':Part.makeBox(14.4,17.5,2.5,A.Vector(34.8,-23.7818903653,83.25)),
            'housing_tie_head_budget':Part.makeBox(5.3,5,4.3,A.Vector(49.2,-17.5318903653,82.35))}
    for name,s in result.items():
        assert s.isValid() and len(s.Solids)==1,name
        s.check(True)
    return result


def clip_motion(scene, upper, clip):
    tick=time.monotonic()
    moving={n:s for n,s in scene.items() if n.startswith('PiBudget:') and
            n not in ('PiBudget:GPIO1992OccupiedHousing','PiBudget:RetainedK1474Boot')}
    moving['upper_frame']=upper
    checks={}; invalid={}
    for name,s in {**moving,**clip}.items():
        try:
            assert s.isValid() and s.Solids
            s.check(True)
        except Exception as exc:invalid[name]=str(exc)
    if invalid: return dict(invalid=invalid,accepted=False,N01_complete=False)
    for a,s in moving.items():
        for b,t in clip.items():
            def gap(z):
                m=independent(s);m.translate(A.Vector(0,0,z))
                lower=bbox_lower_bound(m.BoundBox,t.BoundBox)
                return lower if lower>2 else distance(m,t)
            checks[a+'|'+b]=certify(gap,stop=10,minimum=1.25)
    return dict(checks=checks,accepted=all(v['continuous_clear'] for v in checks.values()),
                invalid=invalid,worker_seconds=round(time.monotonic()-tick,3),
                N01_complete=False,scope='Only new housing clip versus moving Pi/upper frame')


def own_motion(scene, parts):
    tick=time.monotonic()
    high=Part.makeBox(600,600,196,A.Vector(-300,-300,104))
    low=Part.makeBox(600,600,404,A.Vector(-300,-300,-300))
    upper_low=parts['upper'].common(low)
    lower_high=parts['lower'].common(high)
    assert lower_high.Volume < 1e-7
    assert upper_low.Volume > 0
    xgap=upper_low.BoundBox.XMin-parts['lower'].BoundBox.XMax
    assert xgap>1.25
    # The sole upper material belowZ104 is its remote power restraint.
    # The rest moves away from the common horizontal mating plane.
    moving={n:s for n,s in scene.items() if n.startswith('PiBudget:') and
            n not in ('PiBudget:GPIO1992OccupiedHousing','PiBudget:RetainedK1474Boot',
                      'PiBudget:UnlabelledTopComponentsBudget')}
    checks={}
    for n,s in moving.items():
        s.check(True)
        for target in ['lower','front_jaw','housing_tie_band_budget','housing_tie_head_budget']:
            def gap(z):
                m=independent(s);m.translate(A.Vector(0,0,z))
                bound=bbox_lower_bound(m.BoundBox,parts[target].BoundBox)
                return bound if bound>2 else distance(m,parts[target])
            checks[n+'|'+target]=certify(gap,stop=10,minimum=0 if target=='lower' else 1.25)
    return dict(checks=checks,accepted=all(v['continuous_clear'] for v in checks.values()),
                upper_lower_plane_proof=dict(lower_volume_above_Z104=lower_high.Volume,
                    remote_upper_below_plane_X_gap_mm=xgap,initial_plane_contact_intended=True),
                own_mount_check_is_nonintersection_not_1p25_clearance=True,
                worker_seconds=round(time.monotonic()-tick,3),N01_complete=False)


def receive(parts, evidence):
    archive=OUT/'n01-stationary-GPIO-carrier-split-20261024.brep.zip'
    geometry=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for i,(name,s) in enumerate(parts.items()):
            assert s.isValid() and s.Solids
            s.check(True)
            raw=s.exportBrepToString().encode()
            import Part
            restored=Part.Shape();restored.importBrepFromString(raw.decode())
            restored.check(True)
            entry=f'{i:02d}.brep';z.writestr(entry,raw)
            geometry.append(dict(name=name,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),strict_reopen=True))
    paths=[Path(__file__),ROOT/'tools/cad/plan_feline_gpio_service_bights.py',
           OUT/'n01-current-carrier-GPIO-release-20261024.json']
    result=dict(status='CONSTRUCTIVE_SPLIT_HYPOTHESIS_NOT_WHOLE_SERVICE',
                geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),
                source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in paths},
                evidence=evidence,split_plane_Z_mm=104,Pi_pose_changed=False,
                selected_native_changed=False,N01_complete=False,physical_pass=False,
                service_sequence=[
                    'Isolate source, support robot and open access; no energizing.',
                    'Release D_FR.3 and park complete W009 first; still OPEN.',
                    'Release Power2 tie, unplug K1474 from Delock female along received+X15; park full pair without desoldering MAIN; parking OPEN.',
                    'At original Pi pose release USB jacket/root ties and remove empty USB restraint through received8625cd86 path. Manually support cable, do not pull the BUS plug.',
                    'Support Pi+upper frame, remove the two new M2 screws. Retain lower cradle, GPIO wire restraints and GPIO casing clamp.',
                    'Lift Pi+upper frame10mm: header leaves stationary GPIO housing. Keep data USB mated; complete452mm jacket deformation and W009 parking still OPEN.',
                    'Withdraw USB-A along reserved+X15 after arm removal, keeping BUS-C mated; complete cable parking/stroke not yet received.',
                    'Continue lifting Pi+upper frame to bench only after complete remaining path qualified.'],
                assembly_sequence=[
                    'Install lower carrier, GPIO wiring and casing clamp before presenting Pi.',
                    'Prepare Pi on removable upper frame with its original four mounting stacks.',
                    'Support upper frame above seat, mate data USB then lower Pi onto stationary GPIO header housing; validate actual fit in phase2.',
                    'Secure the two M2 frame screws, restore USB restraint/ties, power connector/strain relief, and W009 last.'],
                sequence_is_conditional_not_execution_ready=True,
                open=['Qualify two-M2 split retention and housing-clamp actuation/access',
                      'Whole moving group and W009/USB/power parking',
                      'Full123portions/246ends; remaining scene coverage',
                      'Actual connector housing fit, clamp force and printed strength are phase2 gates'])
    dest=OUT/'n01-stationary-GPIO-carrier-split-20261024.json'
    dest.write_text(json.dumps(result,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
    return result
