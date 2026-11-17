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
for yaw in [-20,0,20]:
 for pitch in [-10,0,10]:
  c=point([-206.85,0,134.6],yaw,pitch)
  v=rot(rot([0,0,-1],pitch,'Y'),yaw,'Z')
  cps=[c,add(c,mul(v,40)),add(Pe,[0,40,0]),Pe]
  def val(t):return [sum(math.comb(3,i)*(1-t)**(3-i)*t**i*cps[i][k] for i in range(4)) for k in range(3)]
  points=[val(i/800) for i in range(801)];length=sum(norm(sub(b,a)) for a,b in zip(points,points[1:]));rads=[]
  for j in range(801):
   t=j/800;d=[3*((1-t)**2*(cps[1][k]-cps[0][k])+2*(1-t)*t*(cps[2][k]-cps[1][k])+t*t*(cps[3][k]-cps[2][k])) for k in range(3)]
   dd=[6*((1-t)*(cps[2][k]-2*cps[1][k]+cps[0][k])+t*(cps[3][k]-2*cps[2][k]+cps[1][k])) for k in range(3)]
   den=norm(cross(d,dd));rads.append(norm(d)**3/den if den>1e-10 else 1e9)
  results.append(dict(yaw=yaw,pitch=pitch,source=c,control_points=cps,numeric_curve_length=length,plus_end10=length+10,remainder_same200=190-length,min_center_radius_sampled=min(rads),bounds=[min(x[k] for x in points) for k in range(3)]+[max(x[k] for x in points) for k in range(3)]))
out=dict(status='ONE_LOW_SIDE_CONSTRUCTIVE_RECIPE_SCREEN_NOT_CONTINUOUS_OR_FULL_STOCK_PASS',profile=[16.8,1.8],innerR=12.5,centerR_required=13.4,end_debit=10,stock=200,poses=results,interpretation='Handle40 derived as conservative nominal tangent allowance from 1.5*h^2/transverse distance; no parameter search. Sample radius and numeric length reject a recipe; they do not certify every pose or a fully occupied same200 variable bight. Remainder needs accessible reconfiguration upstream true grips; no stock borrowed.')
(P/'low-side-ffc-family-screen.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print([(r['yaw'],r['pitch'],round(r['plus_end10'],2),round(r['min_center_radius_sampled'],2),round(r['remainder_same200'],2)) for r in results])
