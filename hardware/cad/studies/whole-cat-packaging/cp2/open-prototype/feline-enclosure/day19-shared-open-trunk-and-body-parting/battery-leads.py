from common import *
s=(P/'layout.py').read_text();exec(s[:s.index('# Common nine-lead drop')])
def bez(p,t):
 a,b,c,d=map(arr,p);return (1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t**2*c+t**3*d
p=arr([bez([[12,0,86.125],[0,0,86.125],[5,-30,91],[12,-30,102]],t) for t in np.linspace(0,1,61)])
supply=dict(points=np.round(p,4).tolist(),diameter=4.8)
# One half remains stationary. A free loop of the battery lead opens after lifting both caps;
# the battery side moves up through 14 mm before the cell travels out of its door.
# Examine two layouts with the same upper bend. Translate the bend by half the withdrawal,
# lengthening one leg exactly as the other shortens.
arc=[]
for lift in [0,14]:
 top=152+lift;start=arr([28.5,-24.5,top]);u=arr([-1.,-1.,0.])/math.sqrt(2);v=arr([0.,0.,1.])
 centre_z=163+lift/2;rr=17.0
 pts=[start,arr([28.5,-24.5,centre_z])]
 for t in np.linspace(0,math.pi,46):pts.append(arr([28.5,-24.5,centre_z])+rr*(math.sin(t)*v+(1-math.cos(t))*u))
 pts.append(arr([28.5,-24.5,145.])+2*rr*u);arc.append(dict(lift_mm=lift,points=np.round(pts,4).tolist(),developed_mm=centre_z-top+math.pi*rr+centre_z-145))
boot=[24,-30,102];end=arr(d['endpoints']['G1.2']['point']);axis=arr(d['endpoints']['G1.2']['outward_axis']);route('W001',[boot,[24,-30,96]],[],[end+4*axis+[0,0,14],end+4*axis,end],4.8,15)
wr('battery-leads.json',dict(input=supply,W075_model_mm=length(p),W075_with_5_termination_mm=length(p)+5,W075_limit=50,ground=tracks['W001'],ground_with_ends_and_trim=ledger['W001']['transport_mm']+19+20,battery_return=arc,group_jackets=2,jacket_project_OD=4.8,free_bend_centre_radius=17,actual_battery_lead_length=None,pack_neck_port='unknown exit at delivered cell; lower transfer and physical stock to bind before closing',no_fixed_clamp_in_moving_bight=True))
