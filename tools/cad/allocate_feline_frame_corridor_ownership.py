"""Joint ownership: provisional overhead beams are variables, not purchases.

Preserves all actual materials/P0/4MTA/MAIN cut channel. Separates only the
named R4 rectangular BankArm and positiveUpperStrip proposals. Their load
paths must be replaced in the common plan BEFORE N01 or native acceptance.
"""
import io
import json
import time
import zipfile
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import label
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT,BASE


def variable(name):return name.startswith('StructureReserve:BankArm') or name=='StructureReserve:UpperStrip1'


def main():
    tick=time.monotonic();src=OUT/'n01-shared-space-atlas-received.json';parentfile=OUT/'n01-shared-space-atlas.json';mapfile=OUT/'n01-whole-constraint-map.json'
    dest=OUT/'n01-reservation-ownership-plan.json';field=OUT/'n01-shared-space-atlas-joint-field.npz';assert not dest.exists()
    p=json.loads(src.read_text());parent=json.loads(parentfile.read_text());mapping=json.loads(mapfile.read_text());record={r['name']:r for r in mapping['parts']}
    assert p['stage']=='complete';oldfield=ROOT/p['field'];assert sha(oldfield)==p['field_sha256'];a=np.load(oldfield,allow_pickle=False)
    lo=np.array([-147,-104,-54]);hi=np.array([189,104,118]);dims=hi-lo+1;total=int(np.prod(dims));mandatory=np.zeros(total,dtype=np.uint16);movable=np.zeros(total,dtype=np.uint16)
    realloc=[];bundle=ROOT/parent['bundle']
    # Rebuild BOTH masks from the source clouds. The compact atlas's first-
    # owner field is insufficient where mandatory and movable reserves overlap.
    with zipfile.ZipFile(bundle) as z:
        for i,r in enumerate(parent['parts']):
            if r['category']!='reservation':continue
            isvar=variable(r['source'])
            if isvar:
                evidence=record[r['source']];s=evidence['source_record']
                assert s['role']=='ScaffoldPlanning' and s['kind']=='rectangular_reservation' and s['origin']=='backbone_R4_rectangular_recipe_only'
                realloc.append(dict(name=r['source'],source_record=s,geometry_category=evidence['geometry_category'],
                    decision='Reallocate planned load path JOINTLY, never delete a selected physical part'))
            raw=z.read(r['entry']);assert __import__('hashlib').sha256(raw).hexdigest()==r['sha256'];q=np.load(io.BytesIO(raw),allow_pickle=False)
            if not len(q):continue
            q=np.rint(q-lo).astype(np.int32);ids=(q[:,0]*dims[1]+q[:,1])*dims[2]+q[:,2];o=movable if isvar else mandatory;take=o[ids]==0;o[ids[take]]=i+1
    assert realloc and not variable('StructureReserve:UpperStrip-1')
    axes=[a[k] for k in ('x','y','z')];grid=np.stack(np.meshgrid(*axes,indexing='ij'),axis=-1);points=grid.reshape(-1,3);shape=grid.shape[:3];distances={};owners={}
    for name,o in [('mandatory_reservation',mandatory),('reallocatable_frame',movable)]:
        ids=np.flatnonzero(o);x=ids//(dims[1]*dims[2]);y=(ids//dims[2])%dims[1];zz=ids%dims[2];cloud=np.column_stack((x,y,zz))+lo
        tree=cKDTree(cloud);d,ix=tree.query(points,workers=1);distances[name]=d.reshape(shape).astype(np.float32);owners[name]=(o[ids[ix]]-1).reshape(shape)
    nominal=a['inside'].copy();conservative=a['inside'].copy()
    for cat in ('material','motion36'):
        nominal&=a[cat+'_distance']>=3.75;conservative&=a[cat+'_distance']>=6.9162
    nominal&=distances['mandatory_reservation']>=3.75;conservative&=distances['mandatory_reservation']>=6.9162
    nominal&=(a['outer_distance']>=5.75)&~a['service'];conservative&=(a['outer_distance']>=8.9162)&~a['service'];components,count=label(nominal)
    values={k:a[k] for k in a.files if k not in ('nominal','conservative','components')}
    values.update(nominal=nominal,conservative=conservative,components=components,
        **{k+'_distance':v for k,v in distances.items()},**{k+'_owner':v for k,v in owners.items()})
    np.savez_compressed(field,**values)
    anchorlist=[];groups={'PiUSB':set(),'BUSUSB':set()}
    for r in p['USB_variable_land_anchors']:
        q=np.array(r['after9_mm']);ix=tuple(int(np.argmin(abs(axis-q[i]))) for i,axis in enumerate(axes));gap=float(np.linalg.norm(grid[ix]-q));cid=int(components[ix]) if gap<=4 else 0
        anchorlist.append(dict(r,component=cid))
        if cid:groups[r['owner']].add(cid)
    mountfile=BASE/'mounting-checkpoint/manifest.json';mount=json.loads(mountfile.read_text())
    result=dict(status='JOINT_FRAME_SURFACE_ATLAS_PLANNING_NOT_N01',selected=False,N01_complete=False,physical_pass=False,
        field=field.relative_to(ROOT).as_posix(),field_sha256=sha(field),grid_shape=list(shape),grid_mm=4,
        nominal_candidate_cells=int(nominal.sum()),previous_nominal_cells=p['nominal_candidate_cells'],
        conservative_candidate_cells=int(conservative.sum()),connected_component_count=count,
        reallocated_provisional_beams=realloc,all_actual_materials_unchanged=True,
        preserved=['All purchased/source solids/P0/E6/15drives/MG92B/4MTA/full factory paths',
            'NegativeUpperStrip source MAIN channel; no solid rebuilt across it',
            'All non-named reservations including full Pi ports/plugs and FHAC sleeves',
            '36leg motion and all12outward60mm ATO withdrawal reservations'],
        proposed_shared_load_path=dict(status='PLANNING_ONLY_NOT_LOAD_OR_NATIVE_APPROVAL',
            bank='Support bank bed atZ52..55 from below. No arbitrary overhead BankArms atZ85 across USB',
            candidate_anchor_evidence=mount['changed_foundation'],
            candidate_sequence='Actual free rail clamps x0/90 installed before boards; lower bank cradle branches before bank, retained MAIN channel, Pi same hole/stack with candidate roots away from full cable corridors',
            required_before_N01=['Reconcile current clamp/hole owners with lower4MTA and battery, not only historic free-hole coordinates',
                'Allocate whole bank/Pi/module loads, positive root union and fastener/tool budgets WITH all123wire portions',
                'Exact current source checks of replacement common frame. Removing an old proposal from hard obstacles is not a completed support']),
        USB_variable_land_anchors=anchorlist,USB_shared_component_ids=sorted(groups['PiUSB']&groups['BUSUSB']),
        whole_solid_interiors_not_globally_classified=True,graph_connected_not_a_radius_length_or_collision_proof=True,
        source_sha256={f.relative_to(ROOT).as_posix():sha(f) for f in (src,parentfile,oldfield,bundle,mapfile,mountfile,Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=result['status'],provisional_beams=len(realloc),old_cells=p['nominal_candidate_cells'],joint_cells=result['nominal_candidate_cells'],seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
