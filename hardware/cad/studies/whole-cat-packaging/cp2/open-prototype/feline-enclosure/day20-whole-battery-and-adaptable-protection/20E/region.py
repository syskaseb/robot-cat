from pathlib import Path
from runpy import run_path
from zipfile import ZipFile
from xml.etree import ElementTree
import hashlib, math, json, os
import numpy as np
import FreeCAD as App
import Part
V=App.Vector
here=Path(__file__).resolve().parent
src=here.parent/'20D/whole-cat20D.FCStd'
source_sha=hashlib.sha256(src.read_bytes()).hexdigest()
assert source_sha=='b1549964028b289ccc9b27adb023ed804f331b8f4fa23159c00a072975a750e9'
box=run_path(str(here.parent/'20D/geometry.py'))['box']
R=12.2
margin_radius=3.35
mouth=V(153.05,74,127.79608338621)
arc_z=mouth.z+R/2
arc_x=mouth.x-R*math.sin(math.pi/3)
def line(a,b):return Part.makeLine(a,b)
end0=V(130,62,arc_z)
a,b,c=V(108,41,157),V(123,46.15,155.4),end0
P=[b,V(136.5,51.6,153.96),V(130,51.7,arc_z),c]
turn=Part.BezierCurve()
turn.setPoles(P)
def xy(t):return V(142-12*math.cos(t),62+12*math.sin(t),arc_z)
def xz(t):return V(arc_x+R*math.sin(t),74,arc_z-R*(1-math.cos(t)))
def arc(f,last):return Part.Arc(f(0),f(last/2),f(last)).toShape()
edges=[line(a,b),turn.toShape(),arc(xy,math.pi/2),line(xy(math.pi/2),xz(0)),arc(xz,math.pi/3-.014)]
path=Part.Wire(edges)
profile=Part.Wire([Part.makeCircle(margin_radius,a,b-a)])
gauge=path.makePipeShell([profile],True,True)
assert gauge.isValid() and len(gauge.Solids)==1
results={}
zones={'available_lower_pocket':box(126.5,51.1,128.4,150.22,77.45,137.55),
       'upper_departure':box(104.5,36.8,150.31,133,49.0,160.5),
       'connected_bend_gauge':gauge,'ring_collar':Part.makeCylinder(3.35,5.9,mouth-5.9*V(.5,0,-math.sqrt(3)/2),V(.5,0,-math.sqrt(3)/2))}
names=['C20_MTA_RR','NIGHT_MTA0100335_UNKNOWN_3','E19_RearBase','E19_RearLid','F19_RearCap',
 'PCA9685_Adafruit815_PCB','E1_populated_prototype_board','G19_E1_population_limits',
 'S0_body','S0_ring_IN_0_0','S0_nut_IN_0_0','S0_washer_IN_0_0','S0_stud_IN_0_0','S0_ring_OUT_0_0',
 'D19_SIDE_BUNDLE_POS','E19_WagoRearPos','Speaker','E19_BUS_PCB','H19_Wires_speaker','PBAY_P_SYS',
 'G19_Group_JRP','G19_Group_POWER']
def bounds(s):
 b=s.BoundBox;return [round(q,3) for q in (b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax)]
with ZipFile(src) as z:
 root=ElementTree.fromstring(z.read('Document.xml'))
 pins={n.get('name'):n.find('./Properties/Property[@name="Shape"]/Part') for n in root.findall('./ObjectData/Object')}
 source={}
 for n in names:
  assert pins[n] is not None,n
  obj=Part.Shape()
  obj.importBrepFromString(z.read(pins[n].get('file')).decode('ascii'))
  source[n]=obj
 for n,shape in zones.items():
  row={'bounds_mm':bounds(shape),'overlaps':{}}
  for ob,s in source.items():
   if not shape.BoundBox.intersect(s.BoundBox):
    row['overlaps'][ob]=0.0
    continue
   q=shape.common(s)
   assert q.isNull() or q.isValid(),(n,ob,'invalid common')
   row['overlaps'][ob]=round(float(q.Volume),5)
   if q.Volume>.002:
    row.setdefault('contact_vertices_mm',{})[ob]=[[round(u,3) for u in (v.Point.x,v.Point.y,v.Point.z)] for v in q.Vertexes]
  results[n]=row
t=np.linspace(0,1,401); one=1-t
xyz=np.asarray([[v.x,v.y,v.z] for v in P])
points=one[:,None]**3*xyz[0]+3*(one*one*t)[:,None]*xyz[1]+3*(one*t*t)[:,None]*xyz[2]+t[:,None]**3*xyz[3]
u=np.diff(points,axis=0);n=np.linalg.norm(u,axis=1);cross=np.linalg.norm(np.cross(u[:-1],u[1:]),axis=1)
rr=n[:-1]*n[1:]*np.linalg.norm(u[:-1]+u[1:],axis=1)/(2*cross)
assert results['connected_bend_gauge']['overlaps']['E19_RearLid']>10
for n in ('available_lower_pocket','upper_departure','ring_collar'):
 assert max(results[n]['overlaps'].values())<.002
manifest=here.parent/'20D/20D-manifest.json'
prev=here.parent/'20D/20D-final-gate.json'
data=json.loads(prev.read_bytes())
heli=data['wire_budgets']['W076_custom']
waypoints=np.array(heli['allocated_waypoints'])
entry=list(heli['allocated_waypoints']).index([108,41,157])
prefix=float(np.linalg.norm(np.diff(waypoints[:entry+1],axis=0),axis=1).sum())
end_amount=heli['terminal_debits_mm']; laying=heli['one_laying_allowance_mm']
tested_length=float(path.Length)+mouth.distanceToPoint(path.Vertexes[-1].Point)
pocket=results['available_lower_pocket']['bounds_mm']
quote={
 'decision':'HOLD_LOCAL_RR_TO_S0_CONNECTED_LAY_REGION',
 'actual_input':'01a1f9a2-2830-7f32-9795-2612339fa255',
 'source':{'20D_commit':'9e358f17c79ac9bbf75e51762c9f8a48f05f8940',
           '20D_native_sha256':source_sha,
           '20D_manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),
           '20D_gate_sha256':hashlib.sha256(prev.read_bytes()).hexdigest(),
           'work_document':'20D/whole-cat20D.FCStd remains the operative native document',
           'changed_prints':[]},
 'carry_forward':{'one_free_HELU23802_OD_mm':4.2,'minimum_clearance_to_rigid_mm':1.25,
                  '20D_RR_gap_mm':0.5381,'clearance_gauge_OD_mm':6.7,
                  'body_and_factory_leads_retained':True,
                  'retained_RR_proxy':'Current mounted 32 x 18 x 18 body plus closed lid envelope; bought piece/ends still physically unknown',
                  'speaker_occupation':'Preserved stock field H19_Wires_speaker as an occupied region'},
 'assembly_hypothesis':'With top open and removable RR holder laid aside, prefit the S0 end and hand-place the free span in the lower pocket. It must still clear the RR holder and rear cover after installation.',
 'checks':results,
 'lower_pocket_dimensions_mm':[round(pocket[i+3]-pocket[i],3) for i in range(3)],
 'S0_barrel_face_mm':[mouth.x,mouth.y,mouth.z],
 'S0_free_collar_length_mm':5.9,
 'tested_connection':{'regional_bend_gauge_only':True,
    'rear_base_side_witness_overlap_mm3':2.794,
    'rear_lid_side_witness_overlap_mm3':results['connected_bend_gauge']['overlaps']['E19_RearLid'],
    'tested_entry_min_inside_R_mm':round(float(min(rr))-2.1,2),
    'final_XZ_turn_inside_R_mm':round(R-2.1,2),
    'consequence':'The separate upstream and lower volumes and the S0 collar are supported by CAD. The transition between levels lacks a closed interference and bend proof with the cover seated. No demonstrated continuous installation region and no general impossibility claim.'},
 'budget':{'20D_reference_project_blank_mm':heli['project_blank_mm'],
           'unchanged_upstream_allocation_mm':round(prefix,2),
           'tested_nonaccepted_regional_extent_mm':round(tested_length,2),
           'ends_once_mm':end_amount,'dressing_once_mm':laying,
           'nonaccepted_reference_blank_mm':math.ceil(prefix+tested_length+end_amount+laying),
           'accepted_20E_blank_mm':None,'nominal_HELU_project_stock_mm':9000,'actual_stock_mm':None},
 'new_prints':0,'physicalPASS':False,'actualfit':None,'cut':None,'slack':None
}
out=here/'20E-RR-S0.json';temp=out.with_suffix('.tmp')
before=out.read_bytes() if out.exists() else None
with temp.open('x',encoding='utf-8',newline='\n') as f:
 json.dump(quote,f,indent=2,ensure_ascii=False);f.write('\n')
assert (out.read_bytes() if out.exists() else None)==before
os.replace(temp,out)
print(quote['decision'],quote['budget'],flush=True)
