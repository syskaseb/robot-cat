"""One full open W027 saddle instead of a space-wasting closed cylinder.

Retain its actual first9, selected radius/R12.4, TE and bank. This receives
only current121+ownTE; the selected whole53 world gate remains required.
"""
import hashlib
import json
import time
import zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_central_pi_wedge import packed
from feline_s1_flexible_fans import saddle_shapes
from receive_feline_flat_station_proposal import wire_shape
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound


def proposal():
    path=OUT/'n01-flat20-field-modulejoint.json';proof=json.loads(path.read_text())
    r=next(x for x in proof['bank_joint_full_source_ports'] if x['id']=='W027/single/end')
    row=dict(point_mm=r['start_mm'],departure_axis=r['departure_axis'],bend_unit=[0,0,-1],
        R_mm=r['bend_R_mm'],first_mm=9,radius=r['radius_mm'])
    wire=wire_shape(row)
    land=dict(grip_start_mm=r['start_mm'],grip_axis=r['departure_axis'],
              jacket_radius_mm=r['radius_mm'],head_follows_strap=True)
    return r,row,wire,land


def main():
    tick=time.monotonic();dest=OUT/'n01-bank-W027-open-saddle.json';assert not dest.exists()
    corepath=OUT/'n01-six-source-current-core.json';doc,current,rows=packed(corepath)
    r,row,wire,land=proposal();full=json.loads((OUT/'n01-full-material-scene.json').read_text())
    te=next(x for x in full['parts'] if x['name']==r['terminal_name'])
    assert sha(ROOT/full['bundle'])==full['bundle_sha256']
    with zipfile.ZipFile(ROOT/full['bundle']) as z:raw=z.read(te['entry'])
    assert hashlib.sha256(raw).hexdigest()==te['sha256']
    ownte=Part.Shape();ownte.importBrepFromString(raw.decode());q=SolidQueries()
    result=dict(status='RUNNING_W027_OPEN_FULL_SOURCE',N01_complete=False,selected=False,physical_pass=False,
        source_bank_and_bought_TE_unchanged=True,source_first9_and_R_and_fullwire_unchanged=True,
        recipe=row,source_endpoint=r,domains=[],rejected=[],queries=[],parts=[],
        source_sha256={corepath.relative_to(ROOT).as_posix():sha(corepath),doc['bundle']:doc['bundle_sha256'],
            'n01-flat20-field-modulejoint.json':sha(OUT/'n01-flat20-field-modulejoint.json'),
            Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        open=['Whole selected53 fixed/motion/mutual','Frame roots and all246ends/4MTA/assembly'])
    archive=dest.with_suffix('.breps.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for head in (270,0):
            kit={'wire':wire,**saddle_shapes(land,270,head)};bad=[]
            for k,s in kit.items():
                assert s.isValid() and s.Solids
                if k!='wire' and wire.common(s).Volume>1e-5:bad.append(dict(part=k,own_wire_overlap_mm3=wire.common(s).Volume))
                c=s.common(ownte);assert c.isNull() or c.isValid()
                if c.Volume>1e-5:bad.append(dict(part=k,own_TE_overlap_mm3=c.Volume))
                for n,t in current.items():
                    kind={'kind':'proposal_wire' if k=='wire' else 'project_stock_reservation' if 'budget' in k else 'proposal_material'}
                    name='OpenW027:'+k;minimum=pair_spacing(name,kind,n,rows[n])
                    if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
                    gap=q.distance(s,t);receipt=dict(head=head,part=k,other=n,gap_mm=gap,required_mm=minimum)
                    result['queries'].append(receipt)
                    if gap<minimum-1e-6:bad.append(receipt)
            if bad:result['rejected'].append(dict(head=head,failures=bad));continue
            candidate=dict(row,ref='Bank:W027/single/end',bank_source=True,bank_simple_source=True,
                normal_degrees=270,head_degrees=head,full_grip_mm=9,cap_wall_mm=2,parts=[])
            for k,s in kit.items():
                raw=s.exportBrepToString().encode();entry=f'{len(result["parts"]):03d}.brep';z.writestr(entry,raw)
                rr=dict(name='OpenW027:'+str(head)+':'+k,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),kind=k)
                candidate['parts'].append(rr);result['parts'].append(rr)
            result['domains'].append(candidate)
    result.update(bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),worker_seconds=round(time.monotonic()-tick,3),
        status='W027_OPEN_SOURCE_CURRENT121_OWNTE_RECEIVED_NOT_WHOLE_N01' if result['domains'] else 'W027_OPEN_SOURCE_REQUIRES_COMMON_INTERFACE_REVIEW')
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=result['status'],domains=len(result['domains']),queries=len(result['queries']),rejected=result['rejected'],seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
