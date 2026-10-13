"""Common front arm/fixed-port interface, NOT another band offset trial.

Preserve cable land positions and the existing case roots. A conservative
manufacturable clearance pocket may remove only peripheral arm material;
the three original lands, cap and old branch cores must remain untouched.
Rejected geometry stays rejected. No native/wholeW5/physical PASS here.
"""
import json
import time
from pathlib import Path
import FreeCAD as A
import Part
import build_complete_source_carriers as B
from loom_land_port import build
P=B.P


def run():
    tick=time.monotonic();nf=P.OUT/'complete-source-carriers-native.json'
    pf=P.OUT/'remaining-loom-roots-plan.json';cf=P.OUT/'complete-source-carriers-plan.json'
    gf=P.OUT/'source-carrier-port-bridges-material.json'
    native,plan,carrier,gate=[json.loads(f.read_text()) for f in (nf,pf,cf,gf)]
    model=P.ROOT/native['native'];assert P.SHA(model)==native['native_sha256']
    af=P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(af.read_text())['axes']
    reader=B.H.P.SavedShapes();rows=[];errors=[]
    for leg,loom,code in [('FrontLeft','FL1','RL'),('FrontRight','FR1','RR')]:
        name=leg+'SourceCarrier';old=reader.shape(model,name)
        fixed=next(r for g in plan['groups'] for r in g['lands'] if r['id']==loom+'/Hip/Fixed')
        port=build(fixed,[1,0,0],0)
        b=port['body'].BoundBox;c=port['band'].BoundBox;margin=.4
        bounds=[min(getattr(b,k+'Min'),getattr(c,k+'Min'))-margin for k in 'XYZ']
        bounds += [max(getattr(b,k+'Max'),getattr(c,k+'Max'))+margin for k in 'XYZ']
        tool=P.box(bounds);cutters=[];new=old.copy();transforms={}
        axis=next(r for r in axes if r['code']==code and r['stage']=='Hip')
        pivot=A.Vector(*axis['pivot_mm']);direction=A.Vector(*axis['axis'])
        for angle in (-15,0,15):
            rotation=A.Rotation(direction,angle)
            inverse=A.Placement(pivot-rotation.multVec(pivot),rotation).inverse()
            cutter=tool.copy();cutter.Placement=inverse*cutter.Placement
            new=new.cut(cutter).removeSplitter();cutters.append(dict(Hip_deg=angle,world_fixed_box_mm=bounds,
                                                                      fixed_to_owner=list(inverse.toMatrix().A)))
            transforms[angle]=inverse.inverse()
        removed=old.cut(new).removeSplitter()
        root=next(r for r in carrier['roots'] if r['leg']==leg)
        x,y,z,X,Y,Z=root['bond_bounds_world_mm'];cap=P.box([x,y,Z,X,Y,Z+4])
        cap_loss=removed.common(cap).Volume
        land_losses=[]
        for pad in gate['recipes'][name]['pads']:
            if pad['name'].endswith('NineMmLand'):
                land_losses.append(dict(name=pad['name'],removed_mm3=removed.common(P.box(pad['bounds_mm'])).Volume))
        # Exact cylinders/spheres preserve the same old branch centre cores.
        # This is a subtraction guard, not a PETG stiffness/strength rating.
        core_hits=[]
        for path in root['paths']:
            for i,(a,b) in enumerate(zip(path['points_mm'],path['points_mm'][1:])):
                start=A.Vector(*a);vector=A.Vector(*b)-start
                core=Part.makeCylinder(1.25,vector.Length,start,vector)
                volume=removed.common(core).Volume
                if volume>1e-6:core_hits.append(dict(loom=path['loom'],segment=i,removed_mm3=volume))
            for i,p in enumerate(path['points_mm']):
                volume=removed.common(Part.makeSphere(1.25,A.Vector(*p))).Volume
                if volume>1e-6:core_hits.append(dict(loom=path['loom'],node=i,removed_mm3=volume))
        contacts=[]
        for angle,T in transforms.items():
            moving=new.copy();moving.Placement=T*moving.Placement
            for tag,s in [('fixed_print',port['body']),('fixed_band',port['band'])]:
                volume=moving.common(s).Volume
                if volume>1e-5:contacts.append(dict(Hip_deg=angle,target=tag,volume_mm3=volume))
        valid=new.isValid() and len(new.Solids)==1 and not new.check(True)
        failed=not valid or cap_loss>1e-6 or any(r['removed_mm3']>1e-6 for r in land_losses) or bool(core_hits) or bool(contacts)
        if failed:errors.append(name)
        rows.append(dict(part=name,fixed_land_id=fixed['id'],fixed_port_recipe=port['recipe'],
                         clearance_pocket_margin_project_mm=margin,cutters=cutters,
                         valid=valid,solids=len(new.Solids),removed_volume_mm3=removed.Volume,
                         original_volume_mm3=old.Volume,removed_fraction=removed.Volume/old.Volume,
                         cap_removed_mm3=cap_loss,land_losses=land_losses,old_branch_core_radius_mm=1.25,
                         core_hits=core_hits,contacts=contacts,accepted_candidate=not failed))
        print('front fixed interface',name,'removed',round(removed.Volume,3),'valid',valid,
              'corehits',len(core_hits),'landhits',sum(r['removed_mm3']>1e-6 for r in land_losses),'contacts',len(contacts),flush=True)
    result=dict(status='FRONT_FIXED_PORT_CLEARANCE_SUBSET_NATIVE_OPEN' if not errors else 'REJECTED_FRONT_FIXED_PORT_CLEARANCE',
                rows=rows,errors=errors,selected=False,W5_complete=False,physical_pass=False,
                inherited_geometry='Only a subset of the exact received moving carriers. No new material or new wire path. Other retained collisions cannot be introduced by removal; load/land/core guards and new fixed ports checked separately.',
                motion_scope='Hip-15/0/+15 sampled. Rectangular0.4mmclearance pockets are defined machining/printing geometry, not bbox proof of prior contact or continuous swept-volume proof.',
                open=['Native editable pockets and fresh current package before any source-carrier replacement',
                      'Complete fixed support arms/all other current interfaces/assembly/stock; no wholeW5',
                      'Casing adhesive, long arm stiffness, PETG creep and real trial remain phase2 gates'],
                source_sha256={p.relative_to(P.ROOT).as_posix():P.SHA(p) for p in (nf,model,pf,cf,gf,af,Path(__file__),Path(__file__).with_name('loom_land_port.py'))},
                worker_seconds=round(time.monotonic()-tick,3))
    (P.OUT/'front-fixed-port-clearance.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],errors=errors,worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':run()
