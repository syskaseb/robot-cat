"""Relocate W064 passage/insulation seat as one native Carrier replacement.

Preserve the received Pi Carrier, three other source passages/seats and the
three already modelled cage windows. The old unused W064 aperture remains;
the old W064 seat is NOT duplicated. This is not selection of the rejected
joint fanout family, nor qualification of cage access or whole W5.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math
from servo_fuse_inputs_r1 import save, sha

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'hardware/electronics/full-cat/w5-joint-source-carrier-native-r1'
CAD = ROOT/'hardware/cad/studies/w5-joint-source-carrier-native-r1'
BASE = ROOT/'hardware/cad/studies/w5-source-carrier-native-r1/SourceCarrierPassages.FCStd'
RECEIVED = ROOT/'hardware/electronics/full-cat/w5-leg-joint-source-layout-r1/checks.json'
WIRE = RECEIVED.parent/'W064_WORLD.brep'
WINDOWS = [(-91.5,4,139.8,-47.5,32,171.5),
           (-46,-14,139.8,-2,14,171.5), (7,-22,139.8,35,22,171.5)]


def build_passage(A, Part):
    from w5_leg_joint_source_layout_r1 import source_edges
    receipt = json.loads(RECEIVED.read_text(encoding='utf-8'))
    assert receipt['status'].startswith('JOINT_SOURCE_'), 'Receive finished worker first'
    assert all(sha(ROOT/k)==v for k,v in {**receipt['source_sha256'],**receipt['files']}.items())
    original = ROOT/'hardware/electronics/full-cat/w5-s1-source-layout-r8/intent.json'
    rows = json.loads(original.read_text(encoding='utf-8'))['routes']
    next(row for row in rows if row['wire']=='W064')['edges'] = source_edges(rows)
    save(OUT/'intent.json', dict(routes=rows, selected=False, physical_pass=False,
        retained_source_routes=['W065','W067','W068','XA01'],
        same_potential_cage_exchange=receipt['P_FRONT_same_potential_cage_exchange'],
        source_sha256={RECEIVED.relative_to(ROOT).as_posix():sha(RECEIVED),
                       original.relative_to(ROOT).as_posix():sha(original)}))
    parent = A.openDocument(str(BASE)); d = A.newDocument('JointSourceCarrierPassage')
    target = CAD/'JointSourceCarrierPassage.FCStd'; d.saveAs(str(target))
    link = d.addObject('App::Link','ReceivedFourPassageCarrier')
    link.setLink(parent.SourceCarrierFinished); link.LinkPlacement=parent.SourceCarrierFinished.Placement
    par=d.addObject('App::VarSet','PassageParameters')
    par.addProperty('App::PropertyLength','Clearance'); par.Clearance=.7
    tools=[]
    q=d.addObject('Part::Cylinder','W064FullDepthPassage')
    q.setExpression('Radius','2.1 mm + PassageParameters.Clearance')
    q.Height=14.2; q.Placement.Base=A.Vector(-16.5,36.2,139.8); tools.append(q)
    # The tangent arc reaches the lower aperture lip. Use its actual native
    # torus, not an enlarged bbox or a straight drill pretending to clear it.
    e=next(row for row in rows if row['wire']=='W064')['edges'][0]
    edge=Part.Arc(A.Vector(*e['start']),A.Vector(*e['mid']),A.Vector(*e['end'])).toShape()
    centre=edge.Curve.Center; start=edge.valueAt(edge.FirstParameter)
    normal=centre-start; normal.normalize(); tangent=edge.tangentAt(edge.FirstParameter)
    q=d.addObject('Part::Torus','W064ApproachClearance'); q.Radius1=e['radius_mm']
    q.setExpression('Radius2','2.1 mm + PassageParameters.Clearance')
    q.Angle1=-180; q.Angle2=180; q.Angle3=e['angle_rad']*180/math.pi
    q.Placement=A.Placement(centre,A.Rotation(-normal,tangent,tangent.cross(normal),'ZXY')); tools.append(q)
    for i,b in enumerate(WINDOWS):
        q=d.addObject('Part::Box','PreservedCageWindow'+str(i))
        q.Length=b[3]-b[0]; q.Width=b[4]-b[1]; q.Height=b[5]-b[2]
        q.Placement.Base=A.Vector(*b[:3]); tools.append(q)
    compound=d.addObject('Part::Compound','SourcePassageAndCageWindows'); compound.Links=tools
    final=d.addObject('Part::Cut','SourceCarrierFinished'); final.Base=link; final.Tool=compound; final.Refine=False
    d.recompute(); d.save()
    assert final.Shape.isValid() and len(final.Shape.Solids)==1 and not final.Shape.check(True)
    volume=final.Shape.Volume; assert volume<link.Shape.Volume
    assert final.Shape.cut(link.Shape).Volume<1e-5
    par.Clearance=.8; d.recompute(); assert final.Shape.Volume<volume
    par.Clearance=.7; d.recompute(); assert abs(final.Shape.Volume-volume)<1e-5; d.save()
    wire=Part.read(str(WIRE)); hits=[]
    for s in wire.Solids:
        if s.BoundBox.intersect(final.Shape.BoundBox):
            v=s.common(final.Shape).Volume
            if v>1e-5: hits.append(v)
    assert not hits, ('New W064 still intersects received Carrier',hits)
    print('JOINT_SOURCE_NATIVE_PASSAGE_READY',volume,flush=True)
    return target


def main():
    import FreeCAD as A, Part
    import w5_source_grips_native_r1 as template
    started=datetime.now(timezone.utc)
    assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True); CAD.mkdir(parents=True,exist_ok=True)
    parent=build_passage(A,Part)
    template_path=Path(template.__file__)
    source=template_path.read_text(encoding='utf-8')
    source=source.replace('grips-native-r1','joint-source-carrier-native-r1')
    old="raw = d.addObject('Part::MultiFuse', 'CarrierWithFourSeats'); raw.Shapes = [link, *raw_seats]; raw.Refine = False"
    assert source.count(old)==1
    source=source.replace(old,"tools.append(box('XL05LowSeatTunnel', [-76.1,-24.3,147.8,-68.2,-19.8,150.2]))\n    raw = d.addObject('Part::MultiFuse', 'FourRawSeats'); raw.Shapes = raw_seats; raw.Refine = False")
    old="final = d.addObject('Part::Cut', 'SourceGripsFinished'); final.Base = raw; final.Tool = cutters; final.Refine = False"
    assert source.count(old)==1
    source=source.replace(old,"seats = d.addObject('Part::Cut', 'FourClearedSeats'); seats.Base = raw; seats.Tool = cutters; seats.Refine = False\n    final = d.addObject('Part::MultiFuse', 'SourceGripsFinished'); final.Shapes = [link,seats]; final.Refine = False")
    # Checking the entire source wire against the finished Carrier also covers
    # old parent material; the template's added-material checks alone do not.
    needle="for key, t in owners.items(): check('AddedSourceSeats', added, key, t)"
    assert source.count(needle)==1
    source=source.replace(needle,needle+"\n    check('W064', owners['W064'], 'FinishedCarrier', final.Shape)")
    context=dict(__file__=str(Path(__file__).resolve()),__name__='joint_source_native_definition')
    exec(compile(source,str(template_path),'exec'),context)
    original=template.current_owners
    def owners(A,Part):
        current,pins=original(A,Part)
        current['W064']=Part.read(str(WIRE)); pins.extend((WIRE,RECEIVED,template_path,BASE))
        for label,rel in (
            ('SourceCover','hardware/cad/studies/w5-source-cage-access-native-r1/Cover_WORLD.brep'),
            ('SourceWestHood','hardware/cad/studies/w5-source-roof-native-r5/WestHood_WORLD.brep'),
            ('SourceEastHood','hardware/cad/studies/w5-source-roof-native-r5/EastHood_WORLD.brep')):
            p=ROOT/rel; current[label]=Part.read(str(p)); pins.append(p)
        return current,pins
    context.update(OUT=OUT,CAD=CAD,PARENT=parent,INTENT=OUT/'intent.json',current_owners=owners)
    context['SEATS']['W064']=(-16.5,36.2,157,0)
    context['main']()
    receipt=json.loads((OUT/'checks.json').read_text(encoding='utf-8'))
    receipt.update(old_W064_aperture_retained_unused=True,old_W064_seat_not_duplicated=True,
        source_cage_windows_preserved=True,source_cage_access_qualified=False,
        whole_joint_fanout_family_qualified=False,whole_source_assembly_complete=False)
    finish=datetime.now(timezone.utc)
    receipt['seat_worker_wall_seconds']=receipt['worker_wall_seconds']
    receipt.update(started_utc=started.isoformat(),finished_utc=finish.isoformat(),
                   worker_wall_seconds=(finish-started).total_seconds())
    receipt['source_sha256'][template_path.relative_to(ROOT).as_posix()]=sha(template_path)
    save(OUT/'checks.json',receipt)


if __name__=='__main__': main()
