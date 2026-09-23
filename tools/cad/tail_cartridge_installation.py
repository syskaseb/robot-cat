"""Sample lowering the pre-tightened cartridge onto the servo, before upper housing."""
import json
from pathlib import Path
import pilot
from tail_cartridge_service import OUT,TARGET
from tail_cartridge_joints import PARTS


def main():
    import FreeCAD as A
    assert not A.GuiUp and not A.listDocuments()
    try:
        d=pilot.document(A,TARGET)
        robot=pilot.document(A,pilot.TARGET)
        plan=json.loads((pilot.BASE/'assembly-plan.json').read_text())
        absent={'UpperHousing34'}
        while True:
            updated=absent|{j['child'] for j in plan['joints'] if j['parent'] in absent}
            if updated==absent:break
            absent=updated
        # A TEMP joint makes the output a tail descendant, but physically the shaft stays in the servo.
        absent.remove('MG92BOutput29')
        fixed={r['name']:pilot.global_shape(robot.getObject(r['name'])) for r in plan['components'] if r['name'] not in absent}
        moving={n:pilot.global_shape(d.getObject(n)) for n in PARTS+['CommunityHornEnvelope']}
        controls={}
        support=fixed['MG92BMount29']
        for n,z in [('LowerFinalBores',9),('BossClearances',9),('ServiceNutChannel',6)]:
            shape=pilot.global_shape(d.getObject(n));shape.translate(A.Vector(0,0,z))
            controls[n]=abs(shape.common(support).Volume)
        assert all(v>1 for v in controls.values()),controls
        rows=[]
        for height in range(36,-1,-3):
            hits=[]
            for n,shape in moving.items():
                s=shape.copy();s.translate(A.Vector(0,0,height))
                for m,t in fixed.items():
                    # This source model has no actual spline cavity. Its intended shaft overlap cannot verify mating.
                    if n=='CommunityHornEnvelope' and m=='MG92BOutput29':continue
                    if not s.BoundBox.intersect(t.BoundBox):continue
                    v=abs(s.common(t).Volume)
                    if v>.001:hits.append({'moving':n,'fixed':m,'mm3':v})
            rows.append({'height_above_rest_mm':height,'intersections':hits})
            print(height,hits,flush=True)
        report={'study_sha256':pilot.sha(TARGET),'tool_sha256':pilot.sha(Path(__file__)),
            'robot_sha256':pilot.sha(pilot.TARGET),'absent_components':sorted(absent),
            'retained_servo_shaft':True,'ignored_intended_pair':['CommunityHornEnvelope','MG92BOutput29'],
            'samples':rows,'conditional_path_clear':all(not r['intersections'] for r in rows),
            'before_flat_positive_controls_mm3':controls,
            'cad_saved':False,'print_ready':False,
            'scope':'13 sampled rigid vertical placements of pre-tightened cartridge with upper housing and descendants absent; not continuous sweep, spline insertion, screw seating or complete robot assembly proof.',
            'sequence_candidate':['Preassemble four M2 bolts, root, both PETG plates and factory horn on bench, with access to both bolt ends.',
                'Factory horn screw must be loaded before closing cartridge if head cannot pass through 3.4 mm spindle bore; exact screw unknown.',
                'Lower cartridge onto servo before installing upper housing/bearings/tail segments.',
                'Tighten factory horn screw through shaft using correct long precision tip, axial M3 screw and nut absent.',
                'Insert M3 nut via side channel, then complete upper bearing housing, axial retention and tail assembly; latter trajectories remain to test.']}
        (OUT/'installation-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8',newline='\n')
    finally:
        for n in list(A.listDocuments()):A.closeDocument(n)


if __name__=='__main__':main()
