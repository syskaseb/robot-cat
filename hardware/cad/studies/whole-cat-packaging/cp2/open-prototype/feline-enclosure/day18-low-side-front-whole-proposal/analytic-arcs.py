import math,json,pathlib
P=pathlib.Path(__file__).parent
add=lambda a,b:[x+y for x,y in zip(a,b)]
sub=lambda a,b:[x-y for x,y in zip(a,b)]
mul=lambda a,s:[x*s for x in a]
dot=lambda a,b:sum(x*y for x,y in zip(a,b))
norm=lambda a:math.sqrt(dot(a,a))
cross=lambda a,b:[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def rot(p,deg,axis):
 t=math.radians(deg);c=math.cos(t);s=math.sin(t);x,y,z=p
 return [x*c+z*s,y,-x*s+z*c] if axis=='Y' else [x*c-y*s,x*s+y*c,z]
def point(p,yaw,pitch):return add(rot(sub(add(rot(sub(p,[-135,0,121]),pitch,'Y'),[-135,0,121]),[-106,0,127]),yaw,'Z'),[-106,0,127])
Pe=[-62.5,31.1,113.5];results=[]
R=13.5
for yaw in [-20,0,20]:
 for pitch in [-10,0,10]:
  c=point([-206.85,0,134.6],yaw,pitch);v=rot(rot([0,0,-1],pitch,'Y'),yaw,'Z')
  h=sub(Pe,c);h[2]=0;h=mul(h,1/norm(h));end=[0,-1,0]
  def arc_delta(a,b):
   theta=math.acos(max(-1,min(1,dot(a,b))));e=mul(sub(b,mul(a,math.cos(theta))),1/math.sin(theta));return mul(add(mul(a,math.sin(theta)),mul(e,1-math.cos(theta))),R),theta,e
  da,ta,ea=arc_delta(v,h);db,tb,eb=arc_delta(h,end);aa=add(c,da);bb=sub(Pe,db);d=sub(bb,aa);a=dot(d,h);perp=sub(d,mul(h,a));b=norm(perp);rs=(a*a+b*b)/(4*b);phi=2*math.atan2(b,a);ls=2*rs*phi;length=R*(ta+tb)+ls
  results.append(dict(yaw=yaw,pitch=pitch,source=c,first_end=aa,last_start=bb,transit_tangent=h,arc_radius=R,first_turn=ta,last_turn=tb,S_radius=rs,S_turn=phi,length_plus_end10=length+10,remainder_same200=190-length))
out=dict(status='LOW_SIDE_ARC_S_ARC_CONSTRUCTION; GEOMETRIC_LENGTH_ONLY_NOT_STOCK_OCCUPANCY_OR_COLLISION_PASS',source_clock='camera clock0 down; Pi vertical +Y entry',profile=[16.8,1.8],innerR=12.5,centerR=13.5,stock=200,end_debit_once=10,poses=results,raw_cubic_file='low-side-ffc-family-screen.json',physical_decision='Tangent-compatible arcs replace inadmissible cubic interpolation within the same low-side regional architecture. No module/range/profile/radius or cable change. Full stock remainder still needs actual variable side-bight allocation with roll/latches and local moving mechanism check; cannot mark GO.')
(P/'arc-S-arc-length-screen.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print([(r['yaw'],r['pitch'],round(r['length_plus_end10'],2),round(r['S_radius'],2),round(r['remainder_same200'],2)) for r in results])
