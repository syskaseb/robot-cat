import math,json,pathlib,datetime
P=pathlib.Path(__file__).parent
def wr(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
# Same complete DATA500, two full project boots=52, not supplier mould measurements.
# The storage plane is above the full PCA/E1 tops, rather than a vertical coil imposing a hump.
z=170.; R0=30.; pi=(6.,-.66,104.1);bus=(40.11,-6.804,109.77)
start=(pi[0],pi[1]);goal=(bus[0]-R0,bus[1]-R0)
rise_pi=z-pi[2]-2*R0;rise_bus=z-bus[2]-2*R0
assert min(rise_pi,rise_bus)>=0
transport=2*math.pi*R0+rise_pi+rise_bus;wanted=448-transport
def rlr(r):
 dx,dy=goal[0]-start[0],goal[1]-start[1];d=math.hypot(dx,dy)/r;theta=math.atan2(dy,dx)
 a=(math.pi-theta)%(2*math.pi);b=(-theta)%(2*math.pi)
 u=(6-d*d+2*math.cos(a-b)+2*d*(math.sin(a)-math.sin(b)))/8
 assert -1<=u<=1
 p=2*math.pi-math.acos(u)
 t=(a-math.atan2(math.cos(a)-math.cos(b),d-math.sin(a)+math.sin(b))+p/2)%(2*math.pi)
 q=(a-b-t+p)%(2*math.pi)
 return (t,p,q)
lo,hi=30.,80.
assert sum(rlr(lo))*lo<wanted<sum(rlr(hi))*hi
for i in range(60):
 m=(lo+hi)/2
 if sum(rlr(m))*m<wanted:lo=m
 else:hi=m
r=(lo+hi)/2;turns=rlr(r);segments=[];pos=start;heading=math.pi;pts=[]
for side,angle in zip([-1,1,-1],turns):
 cx=pos[0]-side*r*math.sin(heading);cy=pos[1]+side*r*math.cos(heading)
 begin=heading
 for i in range(101):
  h=begin+side*angle*i/100;pts.append((cx+side*r*math.sin(h),cy-side*r*math.cos(h),z))
 end=begin+side*angle;new=(cx+side*r*math.sin(end),cy-side*r*math.cos(end))
 segments.append(dict(kind='R' if side<0 else 'L',center=[cx,cy,z],radius=r,heading_start=begin,turn=angle,side=side,start=[*pos,z],end=[*new,z],length=r*angle))
 pos=new;heading=end
assert math.dist(pos,goal)<1e-8
assert abs(math.atan2(math.sin(heading),math.cos(heading)))<1e-8
wr('DATA500-horizontal-stock-plan.json',dict(organization='Single complete DATA cable: two full project boots, port-normal R30 rise at each real mouth, horizontal RLR stock take-up above full fixed electronics. Storage radius derived ONCE from whole 500 unit, not pose trials.',source_pi=pi,source_bus=bus,landing_z=z,source_transport_R=30,free_transport_length=transport,free_storage_length=wanted,storage_radius=r,storage_segments=segments,storage_polyline_preview=pts,stock_debit=dict(project_boots=52,free=448,total=500),capacity_OD=6.8,actual_nominal_jacket_OD='UNVERIFIED: old model5 / allowance5.8; conservative6.8 retained',clearance_extent=[min(a[0] for a in pts)-3.4,min(a[1] for a in pts)-3.4,z-3.4,max(a[0] for a in pts)+3.4,max(a[1] for a in pts)+3.4,z+3.4],checks_required=['Full FFC9-family versus changed static DATA lane','Source transport against F0/AMP/E1/PCA','Actual new skin versus occupied lane; no inheriting D1 skin proof'],physical_PASS=False))
wr('progress.json',dict(input='01a1ecdf-a0d7-7631-be90-7201245c6297',source_commit='638c727ee67edaf352f927ef82bc2a94f2a42b10',started_utc='2026-11-18T04:17:28Z',updated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),current_decision='One skull/two small lower muzzle pads; whole horizontal DATA storage chosen jointly with shoulder section and common receivers; no new supplier parts.',last_fact=dict(DATA_total=transport+wanted+52,DATA_source_R=30,DATA_storage_R=r,storage_extent=[min(a[0] for a in pts),max(a[0] for a in pts),min(a[1] for a in pts),max(a[1] for a in pts)]),consequence='Upper space can be allocated from actual constant-radius full-stock path, not vertical hump or arbitrary empty reserve. R/stock algebra is not collision/physical acceptance.',next_common_test='Whole head/body views plus classify BUS126 by primary board datum; then local full profile and root/skin checks',physical_PASS=False))
print(json.dumps(dict(r=r,total=transport+wanted+52,transport=transport,storage=wanted,bounds=[min(a[0] for a in pts),max(a[0] for a in pts),min(a[1] for a in pts),max(a[1] for a in pts)])))
