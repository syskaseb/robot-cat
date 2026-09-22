"""Geometric tail mass/inertia screening, not a thermal/strength certificate."""
from pathlib import Path
import hashlib,json,math
import FreeCAD as A
import Part

ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'hardware/skorupa/v29'
plan=json.loads((OUT/'assembly-plan.json').read_text())
assert hashlib.sha256((OUT/'Kot_v29_OGON_PROTOTYP.FCStd').read_bytes()).hexdigest()==plan['source_sha256']
assert json.loads((OUT/'shape-cache/index.json').read_text())['source_sha256']==plan['source_sha256']
rows=[];axis=(171,-6,91)
for p in plan['components']:
    if p['stage']!='Motion_Tail_Yaw':continue
    s=Part.Shape();s.read(str(OUT/'shape-cache'/(p['name']+'.brep')))
    volume=sum(v.Volume for v in s.Solids)
    if p['name']=='MG92BOutput29':mass_g=1.;assumption='1 g allocated from total servo 13.8 g; shaft fraction unmeasured'
    elif p['name'].startswith(('TailBolt29','TailNut29')):mass_g=volume*.00785;assumption='Nominal steel envelope at 7.85 g/cm3; no threads/hex recess'
    else:mass_g=volume*.00127;assumption='Full CAD solid PETG at 1.27 g/cm3, not slicer mass'
    rho=mass_g/volume
    com=[sum(v.Volume*v.CenterOfMass[i] for v in s.Solids)/volume for i in range(3)]
    izz=sum(rho*(v.MatrixOfInertia.A33+v.Volume*((v.CenterOfMass.x-axis[0])**2+(v.CenterOfMass.y-axis[1])**2)) for v in s.Solids)*1e-9
    rows.append(dict(name=p['name'],mass_g=mass_g,com_CAD_mm=com,yaw_inertia_kg_m2=izz,assumption=assumption))
mass=sum(r['mass_g'] for r in rows)/1000
com=[sum(r['mass_g']*r['com_CAD_mm'][i] for r in rows)/(1000*mass) for i in range(3)]
radius=math.hypot(com[0]-axis[0],com[1]-axis[1])/1000
inertia=sum(r['yaw_inertia_kg_m2'] for r in rows)
tilt=math.radians(15);alpha=2.
gravity=mass*9.80665*radius*math.sin(tilt)
result=dict(source_sha256=plan['source_sha256'],moving_components=rows,moving_mass_kg=mass,com_CAD_mm=com,yaw_axis_CAD_mm=axis,
    yaw_inertia_kg_m2=inertia,assumed_peak_angular_acceleration_rad_s2=alpha,
    inertial_torque_Nm=inertia*alpha,level_yaw_gravity_torque_Nm=0,
    assumed_robot_tilt_deg=15,max_gravity_yaw_at_tilt_Nm=gravity,
    inertia_plus_tilt_screen_Nm=gravity+inertia*alpha,
    static_shaft_bending_level_Nm=mass*9.80665*radius,
    mg92b_5V_stall_Nm=3.1*.0980665,arbitrary_25pct_stall_screen_Nm=3.1*.0980665*.25,
    continuous_rating_known=False,horn_and_support_verified=False,
    scope='Rigid tail estimate only. Missing output support/horn, cable friction, impacts, supply droop and measured thermal/servo response. Arbitrary 25% stall screen is not a manufacturer continuous rating. Native 1 s animation is not a validated hardware command.')
(OUT/'tail-budget.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='moving_components'},indent=2))
