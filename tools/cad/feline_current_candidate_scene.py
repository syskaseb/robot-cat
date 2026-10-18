"""Replay frozen CURRENT candidate poses, not a selected native assembly.

One source for global allocation. Does not rerun accepted static pair checks.
Keeps purchased/native parts separate from five variable scaffold proposals.
"""
import json
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_rev3_query_scene import build
from feline_current_scene import load
from plan_feline_central_pi_wedge import packed
from check_feline_shared_space import tube_prefix
from plan_feline_front_service_split import line_tube


def current():
    files=dict(profiles=OUT/'n01-rev3-whole-profiles.json',candidate=OUT/'n01-dedicated-fuse-bays.json',
        clocked=OUT/'n01-coupled-clocked-joints.json',locals=OUT/'n01-selected-local-head-tail-sources.json',
        motion=OUT/'motion-layout.json')
    docs={k:json.loads(p.read_text()) for k,p in files.items()}
    assert not docs['candidate']['base_failures'] and not docs['candidate']['base_outer']
    scene,meta,pins,bus=build();_,oldmeta,templates,data,otherpins,_=load();pins.update(otherpins)
    changed=set()
    for ref,row in docs['candidate']['joint_station_moves'].items():
        station=next(s for s in data['ports']['stations'] if s['ref']==ref)
        n=next(n for n,r in oldmeta.items() if r.get('role')==station['current_group'])
        case=scene[n];centre=case.BoundBox.Center
        r=A.Rotation(A.Vector(0,1,0),180 if row['departure_flip_about_Y'] else 0)
        target=A.Vector(row['centre_X_mm'],centre.y,centre.z)
        case.Placement=A.Placement(target-r.multVec(centre),r)*case.Placement
        assert abs(case.BoundBox.Center.x-row['centre_X_mm'])<1e-6
        changed.add(n)
    profiles={**docs['profiles']['recipes'],**docs['candidate']['station_profile_recipes']}
    for n,r in profiles.items():
        q,d,b=(A.Vector(*r[k]) for k in ('point_mm','departure_axis','bend_unit'))
        scene[n]=tube_prefix(list(q),list(d),r['radius_mm'],list(b),r['R_mm'],r['first_straight_mm'])
        scene[n+':after9']=line_tube(*r['after_grip_mm'],r['radius_mm'])
        meta[n]=meta[n+':after9']=dict(kind='wire',wire_owner=r['wire'])
        changed.update((n,n+':after9'))
    for key,group in (('clocked','F_PWM'),('locals',None)):
        _,shapes,rows=packed(files[key])
        for n,s in shapes.items():
            if group is None or rows[n]['group']==group:scene[n]=s;meta[n]=rows[n]
    _,shapes,rows=packed(files['clocked'])
    cap=shapes['RetainedMAINCutForeCap'];old=scene.pop('StructureReserve:UpperStrip-1');meta.pop('StructureReserve:UpperStrip-1')
    assert cap.isValid() and cap.Solids and cap.cut(old).Volume<1e-8
    scene['RetainedMAINCutForeCap']=cap;meta['RetainedMAINCutForeCap']=rows['RetainedMAINCutForeCap'];changed.add('RetainedMAINCutForeCap')
    removed=[]
    variable={'StructureReserve:'+x for x in ('BankArm-69_-1','BankArm-69_1','BankArm105_-1','BankArm105_1','UpperStrip1')}
    moving={n for g in docs['motion']['membership'].values() for ns in g.values() for n in ns}
    for n in list(scene):
        if n.startswith(('REV3:F_HY','REV3:F_HP','REV3:F_TY','REV3:Monitor5015')) or n in variable or n in moving:
            removed.append(n);scene.pop(n);meta.pop(n)
    for p in (*files.values(),Path(__file__)):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    return scene,meta,templates,pins,bus,changed,removed,variable
