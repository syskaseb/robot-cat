"""Read-only qualification of the retained neck risers' eight bolt stacks.

Checks the affected existing head and frame, not the whole robot or actual
tools. Tool budgets are explicit design assumptions. Never rewrites CAD.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import math
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'hardware/cad/studies/whole-cat-packaging/cp2'
NECK = BASE / 'neck-support/coupled'
CORRECT_PACKET = '--correct-nut-packet' in sys.argv
OUT = BASE / ('neck-support/mount-check-corrected.json' if CORRECT_PACKET
              else 'neck-support/mount-check.json')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    import FreeCAD as A
    import Part
    tick = time.monotonic()
    started = datetime.now(timezone.utc).isoformat()
    assert not OUT.exists(), 'Do not repeat unchanged qualification'
    files = [BASE/'BoardDatumCandidate.FCStd', NECK/'NeckRisers.FCStd',
             NECK/'checks.json', ROOT/'hardware/manufacturing/one-batch-prototype-r53/fixed-fastener-cart.json',
             Path(__file__)]
    pins = {p.relative_to(ROOT).as_posix():sha(p) for p in files}
    prior = json.loads(files[2].read_text(encoding='utf-8'))
    assert prior['native_sha256'] == sha(files[1])
    cart = json.loads(files[3].read_text(encoding='utf-8'))
    screws = {r['supplier_sku']:r['dimensions_mm'] for r in cart['rows']}
    for length in (10,12):
        dim = screws[f'0912A2-M020X{length:03}VISK']
        assert (dim['d'],dim['L'],dim['head_d'],dim['head_h'],dim['key']) == (2,length,3.8,2,1.5)
    src = A.openDocument(str(files[0])); neck = A.openDocument(str(files[1]))
    try:
        parts = {o.Name:o.Shape.copy() for o in src.Objects
                 if 'Shape' in o.PropertiesList and not o.Shape.isNull()
                 and o.Name.startswith(('Head_', 'P0_Frame'))}
        parts.update({n:neck.getObject(n).Shape.copy() for n in ('LeftRiser','RightRiser')})
        assert all(s.isValid() for s in parts.values())
        for n in ('Head_Foundation','Head_YawCarrier','Head_Bridge','P0_FrameFront20'):
            assert n in parts
        results=[]; tools=[]; errors=[]; stack=[]

        def check(label, shape, names, output):
            tested=0; contacts=[]
            for name in names:
                obstacle=parts[name]
                if not shape.BoundBox.intersect(obstacle.BoundBox):continue
                tested+=1
                try:
                    hit=shape.common(obstacle)
                    assert hit.isValid()
                    if hit.Volume>1e-5: contacts.append(dict(neighbor=name,volume_mm3=hit.Volume))
                except Exception as exc:
                    errors.append(dict(test=label,neighbor=name,error=str(exc)))
            output.append(dict(test=label,exact_pairs=tested,contacts=contacts))

        for side,y in [('Left',22.5),('Right',-22.5)]:
            for anchor_x in (-80,-70):
                for role,x,zhead,length,nut_z,washer_z in [
                    ('lower',anchor_x,35.22,10,42.82,42.52),
                    ('upper',anchor_x-42,71.82,12,61.62,63.22)]:
                    sign=1 if role=='lower' else -1
                    ztip=zhead+sign*length
                    shank=Part.makeCylinder(1,length,A.Vector(x,y,zhead),A.Vector(0,0,sign))
                    head=Part.makeCylinder(1.9,2,A.Vector(x,y,zhead),A.Vector(0,0,-sign))
                    washer=Part.makeCylinder(2.5,.3,A.Vector(x,y,washer_z)).cut(
                        Part.makeCylinder(1.1,.3,A.Vector(x,y,washer_z)))
                    nut=Part.makeCylinder(4/math.sqrt(3),1.6,A.Vector(x,y,nut_z)).cut(
                        Part.makeCylinder(1,1.6,A.Vector(x,y,nut_z)))
                    target=f'{side}_{role}_{anchor_x}'
                    for name,shape in [('shank',shank),('head',head),('nut',nut),('washer',washer)]:
                        check(target+'_'+name,shape,list(parts),results)
                    # Supplier full-thread screw; no unthreaded shank through nut.
                    nut_end=nut_z+1.6
                    protrusion=ztip-nut_end if sign==1 else nut_z-ztip
                    assert protrusion>=.4
                    stack.append(dict(id=target,axis_mm=[x,y],underhead_z_mm=zhead,
                                      tip_z_mm=ztip,nut_thread_length_mm=1.6,
                                      protrusion_mm=protrusion,pitch_mm=.4))
                    # Explicit assembly sequence: upper before yaw/bridge, lower
                    # from inside bare frame, not through its bottom flange.
                    upper_pre = [n for n in parts if not n.startswith('Head_') or n=='Head_Foundation']
                    if role=='upper':
                        probe=Part.makeCylinder(1.5,35,A.Vector(x,y,zhead+2))
                        check(target+'_vertical_driver_pre_yaw',probe,upper_pre,tools)
                        check(target+'_vertical_driver_complete_head',probe,list(parts),tools)
                    else:
                        probe=Part.makeCylinder(1.5,23.22,A.Vector(x,y,10))
                        check(target+'_short_hex_key_inside_bare_frame',probe,
                              [n for n in parts if n.startswith('P0_') or n.endswith('Riser')],tools)
                    # A 6x2.4 mm nominal nut/washer packet from outside Y.
                    start_y=y-3 if y>0 else -55
                    travel=55-y+3 if y>0 else y+3+55
                    packet_z=min(nut_z,washer_z) if CORRECT_PACKET else washer_z
                    packet_height=max(nut_z+1.6,washer_z+.3)-packet_z if CORRECT_PACKET else 2.2
                    packet=Part.makeBox(5.6,travel,packet_height,A.Vector(x-2.8,start_y,packet_z))
                    check(target+'_lateral_nut_before_head',packet,
                          upper_pre if role=='upper' else [n for n in parts if not n.startswith('Head_')],tools)
        assembled=[r for r in results if r['contacts']]
        pre=[r for r in tools if 'complete_head' not in r['test'] and r['contacts']]
        post=[r for r in tools if 'complete_head' in r['test'] and r['contacts']]
        report=dict(status='NECK_STACK_SEQUENCE_CLEAR' if not(assembled or pre or errors)
                    else 'NECK_STACK_SEQUENCE_REJECTED', selected=False,M2_complete=False,physical_pass=False,
                    source_sha256=pins,stacks=stack,hardware_checks=results,tool_checks=tools,
                    corrected_packet=CORRECT_PACKET,
                    original_probe_issue='Upper packet started at washer rather than nut; reports false contact above real nut/washer stack' if CORRECT_PACKET else None,
                    assembled_hardware_failures=assembled,assembly_tool_failures=pre,
                    completed_head_service_blockers=post,errors=errors,
                    tool_budget={'basis':'Design allowance, NOT supplied actual tool',
                                 'upper_driver_d_mm':3,'upper_driver_length_mm':35,
                                 'lower_key_d_mm':3,'lower_key_inside_frame_z_mm':[10,33.22],
                                 'nut_packet_xz_mm':[5.6,1.9 if CORRECT_PACKET else 2.2],
                                 'nut_packet_calibrated_allowance':False},
                    excluded_scope=['Leg and body shell installation/removal','All wiring','Moving head',
                                    'Physical tool/washer/nut tolerances and PETG load tests'],
                    started_utc=started,finished_utc=datetime.now(timezone.utc).isoformat(),
                    worker_wall_seconds=round(time.monotonic()-tick,3))
        assert all(sha(ROOT/p)==h for p,h in pins.items())
        OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(report['status'],'hardware failures',len(assembled),'preassembly failures',len(pre),
              'service blockers',len(post),'errors',len(errors),flush=True)
        for row in assembled+pre:print(row,flush=True)
    finally:
        A.closeDocument(src.Name);A.closeDocument(neck.Name)


if __name__=='__main__':main()
