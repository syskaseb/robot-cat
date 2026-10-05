"""One editable native passage set for the received whole37-wire harness.

Wire centreline snapshots are explicit immutable inputs, not substituted
print-part geometry. Native profiles/sweeps/cuts remain editable. This stage
does not qualify restraints, retained wall strength or wholeW1/W5.
"""
from pathlib import Path
from datetime import datetime,timezone
import json
import w5_central_shared_routes as scope
from servo_fuse_inputs_r1 import sha,save

ROOT=scope.ROOT;BASE=ROOT/'hardware/electronics/full-cat'
PLAN=BASE/'w5-harness-construction-plan-r1/plan.json'
CENTRAL=BASE/'w5-central-received-joint-r2/received.json'
OUT=BASE/'w5-harness-passages-native-r1'
CAD=ROOT/'hardware/cad/studies/w5-harness-passages-native-r1'
PARENTS={
    'SourceDeck':('w5-source-platform-native-r4/SourceInletPlatform.FCStd','SourcePlatformDeckFinished'),
    'SourceCarrier':('w5-joint-source-carrier-native-r1/SourceCarrierInsulationGrips.FCStd','SourceGripsFinished'),
    'SourceCover':('w5-source-cage-access-native-r1/SourceCageServiceWindows.FCStd','SourceAccessCoverFinished'),
    'SourceWestHood':('w5-source-roof-native-r5/SourceProtectiveHoods.FCStd','WestHoodFinished'),
    'SourceEastHood':('w5-source-roof-native-r5/SourceProtectiveHoods.FCStd','EastHoodFinished'),
    'SourceBankLeft':('w5-source-bank-passage-native-r1/SourceBankEdgePassage.FCStd','SourceBankLeftFinished')}
OWNER_ALIASES={
    'main-positive-complete-r8/positive_portal_seat_DESIGN':'SourceDeck',
    'main-positive-complete-r8/splice_seat_DESIGN':'SourceDeck'}


def root_owner(name):
    return OWNER_ALIASES.get(name,name)


def centreline(wire,central):
    if wire in central['routes']:
        body=ROOT/central['routes'][wire]['geometry']
        name='W001_CENTERLINE_RECEIVED.brep' if wire=='W001' else wire+'_CENTERLINE.brep'
        p=body.parent/name
    else:
        folders=('w5-branch-joint-routes-r3','w5-branch-joint-routes-r2','w5-branch-joint-routes-r1','w5-coupled-corridors-r3')
        body=next(BASE/f/(wire+'_WORLD.brep') for f in folders if (BASE/f/(wire+'_WORLD.brep')).exists())
        p=body.parent/(wire+'_CENTERLINE_WORLD.brep')
    assert p.is_file(),str(p)
    return p


def main():
    import FreeCAD as A,Part
    from w5_ground_entries_r1 import profile
    begin=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    plan=json.loads(PLAN.read_text(encoding='utf-8'));assert not plan['errors']
    central=json.loads(CENTRAL.read_text(encoding='utf-8'));assert central['complete']
    affected={root_owner(h['owner']) for h in plan['actual_contacts']}
    assert affected<=set(PARENTS),('Receive native parent map before building',affected-set(PARENTS))
    pins=[Path(__file__),PLAN,CENTRAL,ROOT/'tools/electronics/w5_ground_entries_r1.py']
    OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    docs={}
    for owner in sorted(affected):
        relative,obj=PARENTS[owner];p=ROOT/'hardware/cad/studies'/relative
        parent_receipt=BASE/relative.split('/')[0]/'checks.json'
        proof=json.loads(parent_receipt.read_text(encoding='utf-8'))
        rel=p.relative_to(ROOT).as_posix()
        assert proof['files'][rel]==sha(p),('Native parent changed',rel)
        pins.append(parent_receipt)
        if p not in docs:docs[p]=A.openDocument(str(p))
        assert docs[p].getObject(obj) is not None,(owner,obj)
        pins.append(p)
    d=A.newDocument('WholeHarnessPassages');target=CAD/'WholeHarnessPassages.FCStd';d.saveAs(str(target))
    param=d.addObject('App::VarSet','PassageParameters')
    param.addProperty('App::PropertyLength','RadialAllowance');param.RadialAllowance=.4
    tools={};finals={};initial={}
    for wire in sorted({h['wire'] for h in plan['actual_contacts']}):
        if wire in ('G1_NEW_BODY','G2_NEW_BODY'):
            # Remove obsolete material above the registered bearing plane,
            # never below it. Retention is a subsequent independent feature.
            p=BASE/'w5-central-bridge-low-arc-r1/received-family.json';pins.append(p)
            placement=json.loads(p.read_text(encoding='utf-8'))['placement']
            block=wire.split('_')[0];x,y=placement[block.lower()+'_centre'];z=placement['floor']
            dx,dy,height=(37,22,11) if block=='G1' else (19,30,9)
            assert placement['angles'][block]==(90 if block=='G1' else 180)
            q=d.addObject('Part::Box',block+'RegisteredBodyPocket')
            q.setExpression('Length',str(dx)+' mm + 2 * PassageParameters.RadialAllowance')
            q.setExpression('Width',str(dy)+' mm + 2 * PassageParameters.RadialAllowance')
            q.setExpression('Height',str(height)+' mm + PassageParameters.RadialAllowance')
            q.setExpression('Placement.Base.x',str(x-dx/2)+' mm - PassageParameters.RadialAllowance')
            q.setExpression('Placement.Base.y',str(y-dy/2)+' mm - PassageParameters.RadialAllowance')
            q.Placement.Base.z=z;tools[wire]=q;continue
        p=centreline(wire,central);pins.append(p)
        path=d.addObject('Part::Feature',wire+'ReceivedCentreline');path.Shape=Part.read(str(p))
        path.addProperty('App::PropertyString','SnapshotSource');path.SnapshotSource=p.relative_to(ROOT).as_posix()
        path.addProperty('App::PropertyString','SnapshotSHA256');path.SnapshotSHA256=sha(p)
        first=path.Shape.Edges[0]
        q=d.addObject('Part::Circle',wire+'ClearanceProfile')
        diameter=2 if wire=='W002' else profile(wire)['OD_mm']
        q.setExpression('Radius',str(diameter/2)+' mm + PassageParameters.RadialAllowance')
        q.Placement=A.Placement(first.valueAt(first.FirstParameter),A.Rotation(A.Vector(0,0,1),first.tangentAt(first.FirstParameter)))
        sweep=d.addObject('Part::Sweep',wire+'NativeClearance')
        sweep.Sections=[q];sweep.Spine=(path,[]);sweep.Solid=True;sweep.Frenet=False;tools[wire]=sweep
    for owner in sorted(affected):
        relative,obj=PARENTS[owner];parent=docs[ROOT/'hardware/cad/studies'/relative]
        link=d.addObject('App::Link',owner+'ReceivedPart');link.setLink(parent.getObject(obj))
        link.LinkPlacement=parent.getObject(obj).Placement;initial[owner]=link.Shape.Volume
        cutter=d.addObject('Part::Compound',owner+'PassageTools')
        cutter.Links=[tools[w] for w in sorted({h['wire'] for h in plan['actual_contacts'] if root_owner(h['owner'])==owner})]
        final=d.addObject('Part::Cut',owner+'HarnessFinished');final.Base=link;final.Tool=cutter;final.Refine=False;finals[owner]=final
    d.save();print('HARNESS_NATIVE_SOURCE_SAVED',len(finals),len(tools),flush=True)
    d.recompute();d.save()
    checks=[]
    for owner,final in finals.items():
        shape=final.Shape;valid=not shape.isNull() and shape.isValid()
        errors=(shape.check(True) or []) if valid else ['Null/invalid native result']
        row=dict(owner=owner,valid=valid,solids=len(shape.Solids),BOP_errors=errors,
            original_mm3=initial[owner],remaining_mm3=shape.Volume)
        checks.append(row);print('HARNESS_NATIVE_PART',owner,valid,len(shape.Solids),len(errors),flush=True)
        shape.exportBrep(str(CAD/(owner+'_CANDIDATE_WORLD.brep')))
    finish=datetime.now(timezone.utc)
    pins += [Path(q.FileName) for q in A.listDocuments().values() if q.FileName and Path(q.FileName)!=target]
    save(OUT/'checks.json',dict(status='NATIVE_PASSAGES_CONSTRUCTED_CHECKPOINT',parts=checks,
        geometry_valid=all(r['valid'] and r['solids']==1 and not r['BOP_errors'] for r in checks),
        radial_allowance_mm=.4,parameter_probe_pending=True,wall_continuity_review_pending=True,
        registered_block_bearing_floor_preserved=True,registered_block_retention_pending=True,
        restraints_complete=False,closed_STL=False,relocated_reopen=False,
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        started_utc=begin.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-begin).total_seconds(),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in CAD.glob('*') if p.is_file()}))


if __name__=='__main__':main()
