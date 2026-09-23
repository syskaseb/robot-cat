"""One-time R4 ownership/link migration; never overwrites signed predecessors.

GUI/MCP for history and view providers. Validation is a separate fresh process.
The stable active-entry file selects the whole robot, not the bench study.
"""
import json
from pathlib import Path
import sys
import pilot

CAD = pilot.CAD
SOURCE = CAD/'studies/tail-cartridge-clearance'
MODULE = CAD/'modules/tail/TailCartridge.FCStd'
TARGET = CAD/'assembly/RobotCatTailCartridge.FCStd'
OUT = CAD/'validation/tail-cartridge-integration'
REPLACEMENTS = {'TailRoot29': 'SupportedRoot34', 'BearingCap34': 'BearingCap34'}
ADDED = ['TailLowerRetainer'] + [f'TailCartridge{k}{i}' for k in ('Bolt', 'Nut') for i in range(4)]
SOURCES = {'TailLowerRetainer': 'LowerRetainerPETG'} | {
    f'TailCartridge{k}{i}': f'Cartridge{k}{i}' for k in ('Bolt', 'Nut') for i in range(4)}
PARAMETERS = ['CartridgeParameters', 'BossInterface', 'LidServiceParameters']


def old_files():
    return [pilot.TARGET, pilot.PARAMS] + [CAD/'modules'/(n+'.FCStd') for n in pilot.MODULES]


def write(name, data):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/name).write_text(json.dumps(data, indent=2), encoding='utf-8', newline='\n')


def prepare():
    """Copy editable histories, NOT the bench solver or the uncertain horn."""
    import FreeCAD as A
    assert A.GuiUp and not MODULE.exists() and not TARGET.exists()
    r4 = pilot.document(A, SOURCE/'TailCartridgeClearance.FCStd')
    lid = pilot.document(A, SOURCE/'TailBearingLidService.FCStd')
    d = A.newDocument('TailCartridge')
    d.saveAs(str(MODULE))  # FreeCAD needs a path before resolving copied links.
    names = ['SupportedRoot34'] + list(SOURCES.values()) + PARAMETERS[:2]
    d.copyObject([r4.getObject(n) for n in names], True)
    d.copyObject([lid.getObject('BearingCap34'), lid.getObject(PARAMETERS[2])], True)
    physical = list(REPLACEMENTS.values()) + list(SOURCES.values())
    assert len(set(physical)) == 11
    assert all(d.getObject(n) for n in physical + PARAMETERS)
    assert not any(o.TypeId.startswith('Assembly::') or 'JointType' in o.PropertiesList for o in d.Objects)
    assert not d.getObject('CommunityHornEnvelope')
    for o in d.Objects:
        o.Visibility = False
        if o.TypeId == 'PartDesign::Body':
            o.ViewObject.DisplayModeBody = 'Tip'
    for n in physical:
        o = d.getObject(n)
        o.Visibility = True
        for key, value in {'PartRevision': 'R4', 'MaterialSpec': 'PETG' if o.TypeId == 'PartDesign::Body' else 'STEEL nominal',
                           'DesignStatus': 'Development prototype; real horn/fastener fit and PETG strength unverified'}.items():
            if key not in o.PropertiesList: o.addProperty('App::PropertyString', key, 'Traceability')
            setattr(o, key, value)
        o.ViewObject.ShapeColor = (.12, .13, .14) if o.TypeId == 'PartDesign::Body' else (.65, .67, .70)
        o.ViewObject.Transparency = 0
    d.getObject('SupportedRoot34').Label = 'Tail root with integrated upper cartridge — PETG R4'
    d.getObject('LowerRetainerPETG').Label = 'Removable lower retainer — PETG R4'
    d.getObject('BearingCap34').Label = 'Bearing lid with driver access — PETG R4'
    d.Label = 'Tail cartridge and service lid — R4 prototype'
    d.recompute()
    sketches = [o for o in d.Objects if o.TypeId == 'Sketcher::SketchObject']
    assert len(sketches) == 25 and all(o.FullyConstrained and o.solve() == 0 for o in sketches)
    assert not any('Invalid' in o.State for o in d.Objects)
    d.save()
    print(json.dumps({'module': str(MODULE), 'physical_parts': 11, 'constrained_sketches': len(sketches)}))


def author():
    """Keep the active robot and its existing edits; save as a new development entry.

    Existing wrappers and their joint frames are unchanged. Explicit datum
    joints and cross-document links are not covered by MCP face mating.
    """
    import FreeCAD as A
    import FreeCADGui as G
    import JointObject
    assert A.GuiUp and MODULE.exists() and not TARGET.exists()
    before = {p.relative_to(pilot.ROOT).as_posix(): pilot.sha(p) for p in old_files()}
    d = pilot.document(A, pilot.TARGET)
    module = pilot.document(A, MODULE)
    asm, joints = d.getObject('RobotCatAssembly24'), d.getObject('Joints')
    plan = json.loads((pilot.BASE/'assembly-plan.json').read_text())
    assert len(plan['components']) == 320
    assert all(d.getObject('Rigid_'+r['name']).Placement.isSame(A.Placement(), 1e-6) for r in plan['components'])
    # Preserve unknown live flags/edits without overwriting their disk owners.
    backup = CAD/'_before-tail-cartridge-integration'
    backup.mkdir(exist_ok=False)
    d.saveCopy(str(backup/'RobotCat-live.FCStd'))
    A.getDocument('TailSupport').saveCopy(str(backup/'TailSupport-live.FCStd'))
    assert (backup/'RobotCat-live.FCStd').stat().st_size > 100000
    assert (backup/'TailSupport-live.FCStd').stat().st_size > 10000
    d.saveAs(str(TARGET))
    for name, source in REPLACEMENTS.items():
        link = d.getObject(name)
        assert link.TypeId == 'App::Link'
        assert link.LinkPlacement.isSame(A.Placement(), 1e-6)
        link.setLink(module.getObject(source))
        link.LinkTransform = False
        link.LinkPlacement = A.Placement()
        link.Label = module.getObject(source).Label
        link.Visibility = True
    for name in ADDED:
        assert d.getObject(name) is None
        parent_name = 'TailRoot29' if name == 'TailLowerRetainer' or 'Nut' in name else 'TailLowerRetainer'
        wrapper = d.addObject('App::Part', 'Rigid_'+name)
        asm.addObject(wrapper)
        link = d.addObject('App::Link', name)
        link.setLink(module.getObject(SOURCES[name]))
        link.LinkTransform = False  # explicit source hardware placement, applied once
        link.LinkPlacement = module.getObject(SOURCES[name]).Placement
        wrapper.addObject(link)
        link.Label = module.getObject(SOURCES[name]).Label
        for key, value in {'MaterialSpec': 'PETG' if name == 'TailLowerRetainer' else 'STEEL nominal M2',
                           'RigidStage': 'Motion_Tail_Yaw', 'DesignStatus': 'R4 bolted cartridge; nominal fit, not print approved'}.items():
            link.addProperty('App::PropertyString', key, 'Traceability'); setattr(link, key, value)
        parent = d.getObject('Rigid_'+parent_name)
        joint = joints.newObject('App::FeaturePython', 'Fix_'+name)
        JointObject.Joint(joint, 0)
        joint.Detach1 = joint.Detach2 = True
        joint.Reference1 = (parent, ['', '']); joint.Reference2 = (wrapper, ['', ''])
        datum = A.Placement(A.Vector(171, -6, 94), A.Rotation())
        joint.Placement1 = parent.Placement.inverse()*datum
        joint.Placement2 = wrapper.Placement.inverse()*datum
        joint.addProperty('App::PropertyString', 'DesignStatus', 'Traceability')
        joint.DesignStatus = 'Four modeled nominal M2x10 bolts and nuts; fit and PETG clamp load unverified'
        JointObject.ViewProviderJoint(joint.ViewObject); joint.Visibility = False
        wrapper.Visibility = link.Visibility = True
        plan['components'].append({'name': name, 'label': link.Label, 'stage': 'Motion_Tail_Yaw'})
        plan['joints'].append({'name': joint.Name, 'parent': parent_name, 'child': name, 'type': 'Fixed'})
    for name in PARAMETERS:
        link = d.addObject('App::Link', 'Cartridge_'+name)
        link.setLink(module.getObject(name)); link.Visibility = False
    d.Label = 'Robot cat — integrated tail cartridge R4 — PROTOTYPE'
    d.recompute()
    assert asm.solve() == 0
    assert all(d.getObject('Rigid_'+r['name']).Placement.isSame(A.Placement(), 1e-6) for r in plan['components'])
    assert sum('TEMP' in d.getObject(j['name']).DesignStatus.upper() for j in plan['joints']) == 29
    d.save()
    assert all(pilot.sha(pilot.ROOT/p) == h for p, h in before.items())
    plan.update({'source_sha256': pilot.sha(TARGET), 'predecessor_sha256': before[pilot.TARGET.relative_to(pilot.ROOT).as_posix()],
                 'entry': TARGET.relative_to(pilot.ROOT).as_posix(), 'print_ready': False})
    write('assembly-plan.json', plan)
    write('migration.json', {'assembly_sha256': pilot.sha(TARGET), 'module_sha256': pilot.sha(MODULE),
        'source_sha256': {p.relative_to(pilot.ROOT).as_posix(): pilot.sha(p) for p in [SOURCE/'TailCartridgeClearance.FCStd', SOURCE/'TailBearingLidService.FCStd']},
        'unchanged_predecessor_files': before, 'added': SOURCES, 'replaced': REPLACEMENTS,
        'components': 329, 'fixed': 315, 'revolute': 13, 'temporary': 29,
        'horn_included_as_physical_part': False, 'servo_coupling_confirmed': False,
        'live_backup': backup.relative_to(pilot.ROOT).as_posix(), 'historical_checkpoints_preserved': True})
    A.setActiveDocument(d.Name)
    G.activeDocument().activeView().viewAxonometric(); G.activeDocument().activeView().fitAll()
    print('INTEGRATED 329 parts; 315 Fixed / 13 Revolute; 29 TEMP retained')


if __name__ == '__main__':
    {'prepare': prepare, 'author': author}[sys.argv[1]]()
