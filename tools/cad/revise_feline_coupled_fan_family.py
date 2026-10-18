"""Repair one shared fan cause; byte-reuse every unaffected frozen BRep."""
import hashlib
import json
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_central_pi_wedge import packed
from plan_feline_front_service_split import line_tube
from plan_feline_front_bulkhead_architecture import tube
from check_feline_shared_space import tube_prefix


def main():
    tick=time.monotonic();src=OUT/'n01-coupled-allocation-snapshot.json'
    dest=OUT/'n01-coupled-fan-family.json';assert not dest.exists()
    p,shapes,rows=packed(src);planpath=OUT/'n01-coupled-allocation-plan.json';plan=json.loads(planpath.read_text())
    assert plan['profile_revision']==1
    with zipfile.ZipFile(ROOT/p['bundle']) as z:raws={r['name']:z.read(r['entry']) for r in p['parts']}
    changed=set();ends=dict(p['changed_end_overrides'])
    def put(n,s):
        assert s.isValid() and len(s.Solids)==1,n
        shapes[n]=s;changed.add(n)
    def first(n,q,d,b,r,first):
        end=q+d*(first+12.4)+b*12.4;finish=end+b*9
        put(n,tube_prefix(list(q),list(d),r,list(b),12.4,first))
        put(n+':grip',line_tube(list(end),list(finish),r))
        return dict(point_mm=list(q),departure_axis=list(d),R_mm=12.4,first_mm=first,
            after_grip_line_mm=[list(end),list(finish)],bend_unit=list(b),radius_budget_mm=r)
    stations=json.loads((OUT/'n01-twenty-wago-port-contract.json').read_text())['stations']
    stationbyref={r['ref']:r for r in stations}
    case_receipts=[]
    for line in plan['WAGO_station_rows']:
        for ref in line['refs']:
            group='WG:'+ref;cases=[n for n,r in rows.items() if r['group']==group and not r.get('wire_owner')]
            assert len(cases)==1,(ref,cases)
            n=cases[0];s=shapes[n].copy();bb=s.BoundBox
            target=line['side']*(52+bb.YLength/2);delta=A.Vector(0,target-bb.Center.y,0)
            s.translate(delta);put(n,s)
            case_receipts.append(dict(ref=ref,new_centre_Y_mm=target,inner_face_abs_Y_mm=52,actual_case_width_Y_mm=bb.YLength))
            for e in stationbyref[ref]['occupied_ports']:
                old=ends[e['endpoint']];q=A.Vector(*old['point_mm'])+delta;d=A.Vector(*old['departure_axis'])
                ends[e['endpoint']]=first('Station:'+e['endpoint'],q,d,A.Vector(0,0,-1),2.1,3)
                rows['Station:'+e['endpoint']]['kind']='reservation_wire'
                rows['Station:'+e['endpoint']+':grip']['kind']='reservation_wire'
    # Both Pi power mouths unchanged, the downstream complete bend is staggered.
    pi=json.loads((OUT/'n01-pi-full-port-contract.json').read_text())
    rot=A.Rotation(A.Vector(0,0,1),180)*A.Rotation(A.Vector(1,0,0),-12)
    pose=A.Placement(A.Vector(50,0,85)-rot.multVec(A.Vector(0,0,47.72)),rot)
    for wid,mouth in pi['full_selected_USB_C_receiver']['free_wire_mouths_mm'].items():
        ends['PiPower:'+wid]=first('PiPower:'+wid,pose.multVec(A.Vector(*mouth)),A.Vector(-1,0,0),
            A.Vector(0,1,0),1.55,plan['PiPower_first_straights_mm'][wid])
    # Inner head-fuse factory changes topology BEFORE it crossed USB; preserve
    # its independent9mm factory grip after arc and before14mm sleeve.
    owner=next(k for k,e in ends.items() if k.startswith('F_HY.') and e['departure_axis'][1]>.99)
    e=ends[owner];q=A.Vector(*e['point_mm']);d=A.Vector(*e['departure_axis']);b=A.Vector(-1,0,0)
    a=q+d*3;mid=a+d*(12.4/2**.5)+b*(12.4*(1-1/2**.5));end=a+d*12.4+b*12.4;tip=end+b*23
    curve=Part.Wire([Part.makeLine(q,a),Part.Arc(a,mid,end).toShape(),Part.makeLine(end,tip)])
    assert curve.Length+3<100
    put(owner+':factory',tube(curve,2));put(owner+':sleeve',line_tube(list(tip-b*14),list(tip+b*6),2.4))
    put(owner+':custom',line_tube(list(tip-b*8),list(tip+b*18),1.55))
    ends[owner]=dict(e,factory_nominal_mm=curve.Length+3,after_arc_factory_mm=23,
        factory_grip_line_mm=[list(end),list(end+b*9)],custom_grip_line_mm=[list(tip+b*9),list(tip+b*18)])
    bundle=dest.with_suffix('.zip');out=[]
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in shapes.items():
            entry=f'{len(out):04}.brep';raw=s.exportBrepToString().encode() if n in changed else raws[n]
            z.writestr(entry,raw);bb=s.BoundBox
            out.append(dict(rows[n],entry=entry,sha256=hashlib.sha256(raw).hexdigest(),solids=len(s.Solids),
                bounds_mm=[[bb.XMin,bb.YMin,bb.ZMin],[bb.XMax,bb.YMax,bb.ZMax]]))
    result=dict(p,status='COUPLED_PERPENDICULAR_FAN_FAMILY_SAVED_PREFLIGHT_PENDING',
        selected=False,N01_complete=False,physical_pass=False,parts=out,bundle=bundle.relative_to(ROOT).as_posix(),
        bundle_sha256=sha(bundle),changed_part_names=sorted(changed),unchanged_parts_byte_reused=len(out)-len(changed),
        source_parent=src.relative_to(ROOT).as_posix(),case_inner_face_allocation=case_receipts,
        changed_end_overrides=ends,source_sha256={src.relative_to(ROOT).as_posix():sha(src),
            (ROOT/p['bundle']).relative_to(ROOT).as_posix():p['bundle_sha256'],planpath.relative_to(ROOT).as_posix():sha(planpath),
            (OUT/'n01-pi-full-port-contract.json').relative_to(ROOT).as_posix():sha(OUT/'n01-pi-full-port-contract.json'),
            (OUT/'n01-twenty-wago-port-contract.json').relative_to(ROOT).as_posix():sha(OUT/'n01-twenty-wago-port-contract.json'),
            Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    result['six_complete_factory_budget']=[dict(r,nominal_mm=ends[r['interface']]['factory_nominal_mm']) for r in p['six_complete_factory_budget']]
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=result['status'],changed=len(changed),unchanged_byte_reused=result['unchanged_parts_byte_reused'],
        seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
