"""Two failures -> changed source-port/topology, not a third scalar retry."""
import hashlib
import json
import time
import zipfile
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_central_pi_wedge import packed
from plan_feline_front_service_split import line_tube
from check_feline_shared_space import tube_prefix


def main():
    tick=time.monotonic();src=OUT/'n01-coupled-fan-family.json';dest=OUT/'n01-coupled-clocked-joints.json';assert not dest.exists()
    p,shapes,rows=packed(src);planpath=OUT/'n01-coupled-allocation-plan.json';plan=json.loads(planpath.read_text());assert plan['profile_revision']==2
    with zipfile.ZipFile(ROOT/p['bundle']) as z:raws={r['name']:z.read(r['entry']) for r in p['parts']}
    changed=set();ends=dict(p['changed_end_overrides']);centres=[]
    contract=OUT/'n01-pi-full-port-contract.json';pi=json.loads(contract.read_text())
    rot=A.Rotation(A.Vector(0,0,1),180)*A.Rotation(A.Vector(1,0,0),-12)
    pose=A.Placement(A.Vector(50,0,85)-rot.multVec(A.Vector(0,0,47.72)),rot)
    d=A.Vector(-1,0,0);bend=rot.multVec(A.Vector(0,-1,0))
    def put(n,s):
        assert s.isValid() and len(s.Solids)==1,n
        shapes[n]=s;changed.add(n)
    for wid,mouth in pi['full_selected_USB_C_receiver']['free_wire_mouths_mm'].items():
        q=pose.multVec(A.Vector(*mouth));R=plan['PiPower_concentric_radii_mm'][wid];first=9
        finish=q+d*(first+R)+bend*R;tip=finish+bend*9;n='PiPower:'+wid
        put(n,tube_prefix(list(q),list(d),1.55,list(bend),R,first))
        put(n+':grip',line_tube(list(finish),list(tip),1.55))
        centres.append(q+d*first+bend*R)
        ends[n]=dict(point_mm=list(q),departure_axis=list(d),R_mm=R,first_mm=first,
            bend_unit=list(bend),after_grip_line_mm=[list(finish),list(tip)])
    centre_gap=(centres[0]-centres[1]).Length;assert centre_gap<1e-8,centre_gap
    # Rigid housing clocking puts its calibrated -1mm source exit ABOVE the
    # long axis. Flexible factory profiles are reallocated, not rigidly flipped.
    centre=A.Vector(-65,-22,97.5);roll=A.Rotation(A.Vector(0,1,0),180)
    tf=A.Placement(centre-roll.multVec(centre)+A.Vector(0,0,1.25),roll)
    s=shapes['F_HY:case'].copy();s.Placement=tf*s.Placement;put('F_HY:case',s)
    for n,s in list(shapes.items()):
        if n.startswith('F_HY.'):
            s=s.copy();s.translate(A.Vector(0,0,3.25));put(n,s)
    for n,e in list(ends.items()):
        if n.startswith('F_HY.'):
            ends[n]=dict(e,point_mm=[e['point_mm'][0],e['point_mm'][1],e['point_mm'][2]+3.25],
                factory_grip_line_mm=[[q[0],q[1],q[2]+3.25] for q in e['factory_grip_line_mm']],
                custom_grip_line_mm=[[q[0],q[1],q[2]+3.25] for q in e['custom_grip_line_mm']])
            assert abs(ends[n]['point_mm'][2]-99.75)<1e-6
    bundle=dest.with_suffix('.zip');out=[]
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in shapes.items():
            entry=f'{len(out):04}.brep';raw=s.exportBrepToString().encode() if n in changed else raws[n];z.writestr(entry,raw);bb=s.BoundBox
            out.append(dict(rows[n],entry=entry,sha256=hashlib.sha256(raw).hexdigest(),
                bounds_mm=[[bb.XMin,bb.YMin,bb.ZMin],[bb.XMax,bb.YMax,bb.ZMax]]))
    result=dict(p,status='CONCENTRIC_POWER_AND_CLOCKED_FHY_SAVED_GATE_PENDING',parts=out,
        selected=False,N01_complete=False,physical_pass=False,changed_part_names=sorted(changed),
        unchanged_parts_byte_reused=len(out)-len(changed),source_parent=src.relative_to(ROOT).as_posix(),
        changed_end_overrides=ends,bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle),
        concentric_common_centre_gap_mm=centre_gap,concentric_centre_mm=list(centres[0]),
        source_sha256={src.relative_to(ROOT).as_posix():sha(src),(ROOT/p['bundle']).relative_to(ROOT).as_posix():p['bundle_sha256'],
            planpath.relative_to(ROOT).as_posix():sha(planpath),contract.relative_to(ROOT).as_posix():sha(contract),
            Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},worker_seconds=round(time.monotonic()-tick,3))
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=result['status'],changed=len(changed),unchanged=result['unchanged_parts_byte_reused'],
        common_centre_gap_mm=centre_gap,seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
