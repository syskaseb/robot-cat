"""Diagnose full P_REAR in already received equivalent615 bays; no new layout.

One cheap field decomposition followed by named source point distances.
No whole-part clearance, collision acceptance, new CAD or N01 score.
"""
import hashlib
import json
import time
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from scipy.interpolate import RegularGridInterpolator
from scipy.spatial import cKDTree
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_flat_station_templates import build,self_wire_gap
from feline_candidate_collision_scene import Scene
from receive_feline_flat_station_proposal import restore


def main():
    tick=time.monotonic();dest=OUT/'n01-power-bay-limiting-owners.json';assert not dest.exists()
    planfile=OUT/'n01-flat-station-architecture.json';plan=json.loads(planfile.read_text())
    sourcefile=OUT/'n01-common-low-closure-domains.json';old=json.loads(sourcefile.read_text())
    proofpath=OUT/'n01-flat20-field-joint.json';proof=json.loads(proofpath.read_text())
    fieldfile=ROOT/proof['field'];assert sha(fieldfile)==proof['field_sha256']
    field=np.load(fieldfile,allow_pickle=False);axes=[field[k] for k in ('x','y','z')]
    fields={k:RegularGridInterpolator(axes,field[k+'_distance'],bounds_error=False,fill_value=0)
        for k in ('material','reservation','curve_hold','motion36','outer')}
    trees={k:cKDTree(field[k+'_context']) for k in ('P_SYS','W043','S1')}
    station=next(s for s in plan['stations'] if s['ref']=='P_REAR')
    slots={}
    for ref in ('P_REAR','G1','P_FRONT'):
        for row in old['domains'][ref]:
            key=(tuple(row['centre_mm']),row['side'],row['departure_X'],row.get('bend_mode','OUTWARD_CONCENTRIC'),row.get('closure_mode','AUTO'))
            slots.setdefault(key,dict(row,source_bay_owner=ref))
    scene=Scene();identity=scene.parts['Ref_Material_P_SYS_new_0_0'].copy();restore(scene,proof)
    scene.parts['Ref_Material_P_SYS_new_0_0']=identity
    result=dict(status='RUNNING_FULL_POWER_BAY_OWNER_DIAGNOSIS',selected=False,N01_complete=False,
        physical_pass=False,source_sha256={**proof['source_sha256'],**scene.pins,**{
            p.relative_to(ROOT).as_posix():sha(p) for p in (sourcefile,planfile,proofpath,fieldfile,
                Path(__file__),ROOT/'tools/cad/feline_flat_station_templates.py')}},
        no_manual_new_case_position=True,only_received_equivalent615_bays=True,
        point_distance_NOT_full_geometry_contact_or_clearance=True,receipts=[],errors=[])
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    save()
    try:
        for row in slots.values():
            if time.monotonic()-tick>60:raise TimeoutError('60s complete-kit diagnostic budget')
            m=build(station,row['family'],row['side'],row['departure_X'],row['centre_mm'][0],
                row.get('centre_y_override_mm'),row.get('bend_mode','OUTWARD_CONCENTRIC'),row.get('closure_mode','AUTO'))
            p=m['points'];rr=m['radii'];best=None
            for label,interp in fields.items():
                gap=1 if label=='outer' else 3.35 if label=='curve_hold' else .2
                values=interp(p)-rr-gap;i=int(np.argmin(values));value=float(values[i])
                if best is None or value<best['margin']:
                    best=dict(layer=label,margin=value,point=p[i].tolist(),type=int(m['types'][i]),radius=float(rr[i]))
            for label,tree in trees.items():
                values=tree.query(p,workers=1)[0]-rr-.2;i=int(np.argmin(values));value=float(values[i])
                if value<best['margin']:best=dict(layer=label+'_context',margin=value,point=p[i].tolist(),type=int(m['types'][i]),radius=float(rr[i]))
            point=A.Vector(*best['point']);vertex=Part.Vertex(point)
            def boxgap(s):
                b=s.BoundBox;q=np.array(best['point'])
                return float(np.linalg.norm(np.maximum(0,np.maximum(np.array([b.XMin,b.YMin,b.ZMin])-q,q-np.array([b.XMax,b.YMax,b.ZMax])))))
            names=sorted(scene.parts,key=lambda n:boxgap(scene.parts[n]))[:12];near=[]
            for name in names:
                shape=scene.parts[name];q=vertex
                if name==scene.bus['name']:
                    q=Part.Vertex(scene.bus['inverse'].multVec(point));shape=scene.bus['original']
                if not shape.isValid():continue
                dist=min(float(q.distToShape(s)[0]) for s in shape.Solids) if shape.Solids else float(q.distToShape(shape)[0])
                inside=any(s.isInside(q.Point,1e-7,True) for s in shape.Solids)
                near.append(dict(source=name,source_kind=scene.meta.get(name,{}).get('kind'),
                    point_gap_mm=dist,point_inside_valid_source_solid=inside,
                    source_wire=scene.wire(name) if name in scene.meta else False))
            near.sort(key=lambda r:r['point_gap_mm'])
            record=dict(source_bay_owner=row['source_bay_owner'],centre_mm=m['centre_mm'],
                departure_X=m['departure_X'],bend_mode=m['bend_mode'],closure_mode=m['closure_mode'],
                self_jacket_gap_margin_mm=self_wire_gap(m),limiting_field_point=best,
                actual_named_sources_near_limiting_point=near[:4])
            result['receipts'].append(record);save()
            print(m['centre_mm'],m['bend_mode'],best['layer'],best['type'],near[0]['source'],flush=True)
        result['status']='FULL_POWER_BAY_LIMITING_OWNERS_RECEIVED_NOT_GEOMETRY_PASS'
    except Exception as e:result['errors'].append(repr(e));result['status']='PARTIAL_POWER_BAY_OWNER_DIAGNOSIS'
    save();print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],bays=len(result['receipts']),errors=result['errors'])))


if __name__=='__main__':main()
