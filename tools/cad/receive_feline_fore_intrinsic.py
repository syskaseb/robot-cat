"""Receive changed fore packet's own channels/mates from saved BReps only.

No repeated outside/world/motion checks. Does not qualify support roots,
panel partnership, force/temperature, delivered fit or full N01.
"""
import hashlib
import json
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_fore_vertical_packet import prefix
from feline_solid_distance import distance
from check_feline_all_current_lands import near


def main():
    tick=time.monotonic();source=OUT/'n01-fore-topology.json';data=json.loads(source.read_text())
    dest=OUT/'n01-fore-intrinsic.json';assert not dest.exists()
    bundle=ROOT/data['bundle'];assert sha(bundle)==data['bundle_sha256'];parts={}
    with zipfile.ZipFile(bundle) as z:
        for row in data['parts']:
            if row['group']!='ForeFHAC':continue
            blob=z.read(row['entry']);assert hashlib.sha256(blob).hexdigest()==row['sha256']
            s=Part.Shape();s.importBrepFromString(blob.decode('utf-8'));assert s.isValid() and s.Solids
            parts[row['name'].removeprefix('ForeFHAC:')]=s
    result=dict(status='RUNNING_FORE_INTRINSIC',selected=False,N01_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (source,bundle,Path(__file__),
            Path(__file__).with_name('plan_feline_fore_vertical_packet.py'),Path(__file__).with_name('feline_solid_distance.py'))},
        queries=[],failures=[],errors=[],
        initial2_5mm_source_case_mate_not_airgap=True,
        sleeve_is_external_envelope_internal_conductor_material_not_resolved=True,
        case_ring_wall_partner_root_hardware_delivery_fit_OPEN=True)
    case=parts['case'];wires={n:s for n,s in parts.items() if n.endswith((':factory',':sleeve',':custom'))}
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    def gap(a,b,shape,other,minimum):
        g=distance(shape,other);row=dict(a=a,b=b,gap_mm=g,minimum_mm=minimum);result['queries'].append(row)
        if g<minimum-1e-5:result['failures'].append(row)
    def volume(a,b,shape,other):
        c=shape.common(other);assert c.isNull() or c.isValid()
        row=dict(a=a,b=b,overlap_mm3=c.Volume,channel_mating_surfaces_may_touch=True);result['queries'].append(row)
        if c.Volume>1e-5:result['failures'].append(row)
    save()
    try:
        for recipe in data['fore_recipes']:
            q,d,b=(A.Vector(*recipe[k]) for k in ('point_mm','departure_axis','bend_unit'))
            trimmed,_,_=prefix(q+d*2.5,d,b,recipe['bend_degrees']*__import__('math').pi/180,recipe['first_mm']-2.5)
            gap(recipe['side']+':trimmed_factory','case',trimmed,case,1.25)
        for n,s in wires.items():
            if n.endswith(':factory'):continue
            gap(n,'case',s,case,1.25)
        for n,s in parts.items():
            if '_full_grip_' not in n:continue
            if n.endswith(':factory_full_grip_seat'):volume(n,'case',s,case)
            else:gap(n,'case',s,case,1.25)
            side,kind=n.split(':')[0:2];owned=side+':'+kind.split('_')[0]
            for wire,tube in wires.items():
                if not near(s.BoundBox,tube.BoundBox,1.25):continue
                if wire==owned:volume(n,wire,s,tube)
                else:gap(n,wire,s,tube,1.25)
        volume('case_retention_ring_budget','case',parts['case_retention_ring_budget'],case)
        result['status']='FORE_OWN_CHANNELS_AND_CASE_MATES_CLEAR_ROOTS_PANEL_OPEN' if not result['failures'] else 'FORE_OWN_INTERFACE_REJECTED'
    except Exception as e:result['errors'].append(repr(e));result['status']='PARTIAL_FORE_OWN_INTERFACE'
    save();print(json.dumps({k:result[k] for k in ('status','worker_seconds','failures','errors')}),flush=True)


if __name__=='__main__':main()
