"""Pinned common scene after seven-return qualification, no repeated gates."""
import json
from pathlib import Path
from current_leg_harness_context import context as retained_context,W,Part
from plan_current_main_sources import ROOT,BASE,OUT,SHA

def context():
    # Refuse to turn a planning/rejected ground row into accepted context.
    gf=OUT/'ground-tree-checks.json';gate=json.loads(gf.read_text())
    assert gate['status']=='COUPLED_GROUND_TREE_SAMPLED_CLEAR_NATIVE_OPEN',gate['status']
    assert not gate['contacts'] and not gate['errors']
    for n,h in gate['source_sha256'].items():assert SHA(ROOT/n)==h,n
    reader,pins,targets,old=retained_context();pins.add(gf)
    def load(tag):
        f=OUT/(tag+'-plan.json');pins.add(f);p=json.loads(f.read_text())
        for n,h in p.get('source_sha256',{}).items():assert SHA(ROOT/n)==h,n
        return p
    bank=load('bank-input');cut=targets['Foundation']
    for h in bank['required_foundation_passages']:
        x,y=h['centre_xy_mm'];z0,z1=h['z_range_mm']
        cut=cut.cut(Part.makeCylinder(h['diameter_mm']/2,z1-z0,W.A.Vector(x,y,z0)))
    assert cut.isValid();targets['Foundation']=cut
    rem=bank['obsolete_side_attachment_removal'];cut=targets[rem['target']]
    for b in rem['cut_bounds_mm']:cut=cut.cut(W.box(b))
    assert cut.isValid() and not cut.check(True);targets[rem['target']]=cut
    old.update({n:(W.makewire(v['parts']),v['radius_mm']) for n,v in bank['routes'].items()})
    main=load('main-pi');old.pop('W077_PREFIX',None)
    targets['F_PI_sleeve']=W.box(main['factory_custom_overlap']['sleeve_bounds_mm'])
    old.update({n:(W.makewire(v['parts']),v['radius_mm']) for n,v in main['routes'].items()})
    front=load('front-gallery');targets.update({n:W.box(v['casing_mm']) for n,v in front['stations'].items()})
    old.update({n:(W.makewire(v['parts']),v['radius_mm']) for n,v in front['routes'].items()})
    ground=load('ground-tree')
    targets.update({n:W.box(v['casing_mm']) for n,v in ground['rear_gallery'].items()})
    targets['FR_G']=W.box(ground['front_ground_station']['casing_mm'])
    targets['G1_CP2']=W.box(ground['G1']['casing_mm'])
    old.update({n:(W.makewire(v['parts']),v['radius_mm']) for n,v in ground['routes'].items()})
    for n in ('XT60_CP2','F0_CP2','PostF0Splice_CP2'):
        assert n not in targets;targets[n]=reader.shape(BASE/'OpenPrototypePlan.FCStd',n)
    return reader,pins,targets,old
