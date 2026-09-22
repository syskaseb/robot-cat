"""Provisional head sizing and a revision-specific tail budget.

Head servo boxes are still placeholders. Test candidate axes at their centres
and a balanced head alternative. v29 tail uses the measured supplier STEP
axis; older revisions use placeholders. None certifies the mounting/load path.
"""
import json,math
import numpy as np
from cad_model import ROOT,OUT,REVISION,combine,KGFCM_TO_NM,xyz
from cad_kinematics import rotation


def budget(parts,pivot,axis,angles,acceleration=2.):
    aggregate=combine(parts);axis=np.array(axis,dtype=float);axis/=np.linalg.norm(axis)
    offset=np.array(aggregate['com_m'])-pivot
    I=np.array(aggregate['inertia_kg_m2'])+aggregate['mass_kg']*(offset@offset*np.eye(3)-np.outer(offset,offset))
    inertia=float(axis@I@axis)
    static=[abs(float(axis@np.cross(rotation(axis,math.radians(a))@offset,[0,0,-9.80665*aggregate['mass_kg']]))) for a in angles]
    return dict(parts=[p['name'] for p in parts],mass_kg=aggregate['mass_kg'],com_m=aggregate['com_m'],
                candidate_pivot_m=list(pivot),candidate_axis=axis.tolist(),angle_range_deg=[min(angles),max(angles)],
                peak_gravity_nm=max(static),inertia_about_axis_kg_m2=inertia,
                acceleration_rad_s2=acceleration,gravity_plus_inertia_nm=max(static)+inertia*acceleration)


def main():
    model=json.loads((OUT/'model.json').read_text(encoding='utf8'))
    parts=model['components'];byname={p['name']:p for p in parts}
    prefixes=('HeadFront','HeadRear','Eye','Ear','Muzzle','Nose','ToF','MicBolt33_','MicNut33_')
    head=[p for p in parts if p['name'].startswith(prefixes) or p['name'] in ('Camera','ToF','Microphones','IrIlluminator')]
    pitch=budget(head,byname['HeadPitchServo']['com_m'],[0,1,0],range(-20,21))
    head_com=combine(head)['com_m']
    balanced=budget(head,head_com,[0,1,0],range(-20,21))
    yaw_parts=head+[byname[n] for n in ('HeadPitchServo','NeckColumn','NeckCollar')]
    yaw=budget(yaw_parts,byname['NeckYawServo']['com_m'],[0,0,1],range(-30,31))
    if REVISION in ('v29','v30','v31','v32','v33','v34','v35'):
        geometry=json.loads((OUT/'geometry.json').read_text(encoding='utf8'))
        tail_names={p['name'] for p in geometry['components'] if p.get('native_stage')=='Motion_Tail_Yaw'}
        tail=[p for p in parts if p['name'] in tail_names]
        plan=json.loads((ROOT/'hardware/skorupa'/REVISION/'assembly-plan.json').read_text())
        assert plan['source_sha256']==model['source_sha256']==geometry['source_sha256']
        tail_pivot=xyz(next(j for j in plan['joints'] if j['name']=='Rev_TailYaw29')['pivot_mm'])
        tail_key='tail_yaw_actual_cad_axis'
        tail_warning='v29 rigid keyed PETG tail: horn and independent output support unresolved. Not print ready.'
        if REVISION in ('v34','v35'):
            tail_warning='v34 two-608 support modeled; bearing fits, PETG strength and physical horn coupling unresolved. This budget is not a tail-bearing or servo qualification.'
    else:
        tail=[p for p in parts if p['name'].startswith(('TailSegment','TailJoint','TailSocket'))]
        tail_pivot=byname['TailYawServo']['com_m']
        tail_key='tail_yaw_placeholder_centre'
        tail_warning='Legacy tail flexure shapes are placeholders, not validated PETG hinges. Use 1 tail servo, not 2.'
    tail_yaw=budget(tail,tail_pivot,[0,0,1],range(-30,31))
    # Robust upper bound for a tilted chassis / alternative tail hinge axis.
    tail_gravity=combine(tail)['mass_kg']*9.80665*np.linalg.norm(np.array(combine(tail)['com_m'])-tail_pivot)
    report=dict(source_sha256=model['source_sha256'],scope=__doc__,
                mg92b_5V=dict(stall_nm=3.1*KGFCM_TO_NM,no_load_rad_s=math.pi/3/.13,
                    provisional_25pct_screen_nm=3.1*KGFCM_TO_NM*.25,
                    source='https://towerpro.com.tw/product/mg92b/',continuous_torque='unknown'),
                head_pitch_placeholder_centre=pitch,head_pitch_balanced_candidate=balanced,
                neck_yaw_placeholder_centre=yaw,
                tail_arbitrary_axis_gravity_upper_bound_nm=float(tail_gravity),
                warnings=['Bracket, horn and cable loads absent; not approval of mounts or servo.',
                    'Vertical yaw has zero gravity torque only with level chassis; radial bearing loads remain.',
                    'Balance head near COM instead of selecting a larger servo solely by stall torque.',
                    'Mass assumes solid CAD PETG at 1.27 g/cm3 and estimated bought parts.',
                    tail_warning])
    report[tail_key]=tail_yaw
    (OUT/'auxiliary-budget.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
