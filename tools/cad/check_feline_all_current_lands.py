"""Single current178end first-land gate against the complete retained scene.

Identify coupled blocked interfaces BEFORE routing middles or detailing mounts.
Nominal project ports/diameters; not producer pin/fit or full wiring acceptance.
"""
import json
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
import numpy as np
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT


def near(a,b,gap=1.25):
    return sum(max(0,u-v,w-x)**2 for u,v,w,x in ((a.XMin,b.XMax,b.XMin,a.XMax),
        (a.YMin,b.YMax,b.YMin,a.YMax),(a.ZMin,b.ZMax,b.ZMin,a.ZMax)))<=gap*gap


def main():
    tick=time.monotonic();dest=OUT/'n01-all-current-first-lands.json';assert not dest.exists()
    paths={k:OUT/n for k,n in dict(ends='n01-current-endpoint-packet-r2.json',scene='n01-full-material-scene.json',
        lower='n01-lower-bay-world-probe.json',specs='prefix-allocation.json',bank='n01-common-backbone-preflight-r4.json').items()}
    p={k:json.loads(f.read_text()) for k,f in paths.items()}
    assert len(p['ends']['endpoints'])==178 and not p['ends']['rejected_central_cassette_MTA_endpoints_used']
    report=dict(status='RUNNING_COMPLETE_CURRENT_FIRST_LANDS',selected=False,N01_complete=False,physical_pass=False,
        endpoint_count=178,covered=[],reused_splice_grips=[],contacts=[],reservation_contacts=[],errors=[],
        jacket_conflicts=[],pairs=0,wire_pairs=0,port_trim_mm=2.5,
        port_trim_basis='Nominal mate overlap only; other neighbouring material tested with full land',
        hard_material_gap_mm=1.25,jacket_gap_mm=.2,full_middle_routes_or_grips_or_motion_accepted=False,
        source_sha256={f.relative_to(ROOT).as_posix():sha(f) for f in (*paths.values(),Path(__file__))})
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def gate():
        if time.monotonic()-tick>240:raise TimeoutError('240s bounded first-land gate; preserve completed coverage')
    scene={};metadata={}
    for key in ('scene','lower'):
        probe=p[key];bundle=ROOT/probe['bundle'];assert sha(bundle)==probe['bundle_sha256']
        report['source_sha256'][bundle.relative_to(ROOT).as_posix()]=sha(bundle)
        with zipfile.ZipFile(bundle) as z:
            for row in probe['parts']:
                if row.get('role')=='CurrentCassette' or row.get('role','').startswith('leg:'):continue
                name=row['name'];assert name not in scene,name
                s=Part.Shape();s.importBrepFromString(z.read(row['entry']).decode('utf-8'))
                scene[name]=s;metadata[name]=row
    boxes={n:s.BoundBox for n,s in scene.items()};valid={n:s.isValid() and bool(s.Solids) for n,s in scene.items()}
    specs={r['id']:r for r in p['specs']['specifications']};bywire={}
    for r in specs.values():bywire[r['wire']]=max(bywire.get(r['wire'],0),r['radius'])
    factory={r['wire']:r for r in json.loads((OUT/'n01-full-lower-bay-plan-r3.json').read_text())['factory_routes']}
    lands={};ends={e['id']:e for e in p['ends']['endpoints']}
    def same_wire(name,e):
        return name in (e['wire'],'Factory:'+e['wire'],'CustomPrefix:'+e['wire'],'End:'+e['id'])
    def mate(name,row,e):
        g=e['group']
        if row.get('role')==g:return True
        if g=='MAIN':return name.startswith('Ref_Material_MAIN_')
        if g=='F_PI':return name=='Ref_Material_F_PI_new_0_0'
        if g=='WAGO:P_SYS_new':return name=='Ref_Material_P_SYS_new_0_0'
        return row.get('owner')==g and row.get('kind')=='actual_case'
    try:
        save()
        for e in p['ends']['endpoints']:
            gate();name=e['id'];d=e['departure_axis'];assert d is not None,(name,'No direction')
            a=np.array(e['point_mm']);d=np.array(d);assert abs(np.linalg.norm(d)-1)<1e-5,name
            if e['group']=='SelectedSolderSpliceClip':
                report['reused_splice_grips'].append(dict(id=name,source='n01-central-spine-power-plan-r4.json',
                    reason='Bare8mm overlap is not a jacket land; two actual outside-sleeve9mm grips retained'))
                report['covered'].append(name);continue
            R=specs.get(name,{}).get('radius',bywire.get(e['wire'],1.55))
            if e['wire'] in factory:R=factory[e['wire']]['radius_mm']
            if e['group']=='MAIN' or e['wire']=='W078':R=1.05
            if e['group'].startswith('NineWireCuff'):R=1.55
            length=e.get('initial_jacket_land_mm',9);assert length>=9,name
            s=Part.makeCylinder(R,length,A.Vector(*a),A.Vector(*d));assert s.isValid() and len(s.Solids)==1
            short=Part.makeCylinder(R,length-2.5,A.Vector(*(a+2.5*d)),A.Vector(*d));bounds=s.BoundBox
            lands[name]=(s,e,R)
            for n,t in scene.items():
                gate()
                if same_wire(n,e) or not near(bounds,boxes[n]):continue
                report['pairs']+=1
                if not valid[n]:report['errors'].append(dict(end=name,part=n,error='Invalid candidate actual part'));continue
                tested=short if mate(n,metadata[n],e) else s
                c=tested.common(t);assert c.isNull() or c.isValid(),(name,n)
                volume=c.Volume
                gap=tested.distToShape(t)[0] if volume<=1e-5 else 0
                if volume>1e-5 or gap<1.25-1e-5:
                    record=dict(end=name,group=e['group'],part=n,part_role=metadata[n].get('role',metadata[n].get('owner')),
                        volume_mm3=volume,gap_mm=gap,nominal_source_port_mating_trim=mate(n,metadata[n],e))
                    key='reservation_contacts' if 'reservation' in metadata[n]['kind'] else 'contacts'
                    report[key].append(record)
            report['covered'].append(name)
            save()
        for i,(name,(s,e,R)) in enumerate(lands.items()):
            for other,(t,f,r) in list(lands.items())[i+1:]:
                gate()
                if not near(s.BoundBox,t.BoundBox,.2):continue
                report['wire_pairs']+=1;gap=s.distToShape(t)[0]
                if gap<.2-1e-5:report['jacket_conflicts'].append(dict(a=name,b=other,gap_mm=gap,
                    same_physical_segment=name.rsplit('/',1)[0]==other.rsplit('/',1)[0]))
        report['status']='ALL_CURRENT_FIRST_LANDS_CLEAR_FULL_ROUTES_OPEN' if not any(report[k] for k in ('contacts','reservation_contacts','jacket_conflicts','errors')) else 'CURRENT_FIRST_LAND_BLOCKERS_BEFORE_ROUTING'
    except Exception as exc:report['errors'].append(repr(exc));report['status']='CURRENT_FIRST_LANDS_PARTIAL'
    report['land_recipes']=[dict(id=n,start_mm=ends[n]['point_mm'],axis=ends[n]['departure_axis'],radius_mm=r,
        straight_mm=ends[n].get('initial_jacket_land_mm',9),nominal_project_diameter=True) for n,(s,e,r) in lands.items()]
    save();print(json.dumps({k:report[k] for k in ('status','worker_seconds','pairs','wire_pairs')})+
        f" covered={len(report['covered'])} contacts={len(report['contacts'])} reserves={len(report['reservation_contacts'])} jackets={len(report['jacket_conflicts'])} errors={len(report['errors'])}",flush=True)


if __name__=='__main__':main()
