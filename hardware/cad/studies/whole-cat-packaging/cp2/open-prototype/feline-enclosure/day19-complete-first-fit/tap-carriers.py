from pathlib import Path
import math,json
P=Path(__file__).parent;O=P.parent;E=O/'day19-simple-box-common-core';F=O/'day19-connected-servo-usb-and-closure'
exec((E/'core.py').read_text().split('# Each board/power cluster')[0].replace('19E.FCStd','19I.FCStd'))
q=json.loads((P/'remote-pulldown-lay.json').read_bytes());fixed=json.loads((F/'service-lay.json').read_bytes())['fixed'];result={}
def vec(a):return V(*a)
def beam(a,b,r):
 v=b-a;return Part.makeCylinder(r,v.Length,a,v)
for role,pair,host in [('yaw','D19D_YawMatedPair','E19_ForeLid'),('pitch','BR_FLANK_HP_PAIR','E19_UpperYawCover'),('tail','B19_TailMatedPair','E19_RearLid')]:
 path=next(a['points'] for a in q['pitch'] if a['yaw']==0) if role=='pitch' else fixed['JR_'+role]['points']
 p=list(map(vec,path));ds=[0.]
 for a,b in zip(p,p[1:]):ds.append(ds[-1]+(b-a).Length)
 N=V(0,1,0) if role=='pitch' else V(0,0,-1)
 def sample(u):
    i=next(i for i in range(len(ds)-1) if ds[i+1]>=u);t=p[i+1]-p[i];t.normalize();c=p[i]+(u-ds[i])*t;side=t.cross(N);side.normalize();return c,t,side
 def run(a,b,lo,hi,top,bot):
    wires=[]
    for j in range(1+max(2,math.ceil((b-a)/3))):
        u=a+(b-a)*j/max(2,math.ceil((b-a)/3));c,t,h=sample(u)
        pts=[c+x*h+z*N for x,z in [(lo,top),(hi,top),(hi,bot),(lo,bot)]]
        wires.append(Part.makePolygon(pts+[pts[0]]))
    return Part.makeLoft(wires,True,True)
 parts=[run(2,50,-3.9,4.5,3.65,5.7)]
 # End grips on intact insulation, no load on the two staggered windows.
 for a,b in [(2,5.8),(44.2,48.2)]:
    parts.append(run(a,b,-2.85,2.85,1.02,4.55))
    for lo,hi in [(-3.02,-1.88),(1.88,3.02)]:parts.append(run(a,b,lo,hi,-1.35,3.95))
    for lo,hi in [(-2.85,-1.25),(1.25,2.85)]:parts.append(run(a,b,lo,hi,-1.45,-1.0))
 # Central resistor rests on a short longitudinal land beside the strip.
 c,t,h=sample(25);pivot=c+3.0*h+2.78*N
 pad=run(21.8,28.2,2.12,4.23,3.48,4.05);parts.append(pad)
 rn='G19_RemoteR_'+role;rod=Part.makeCylinder(.8,3.6,pivot-1.8*t,t);D.getObject(rn).Shape=rod
 bb=sh(pair).BoundBox;root=V(bb.XMax-8.1,bb.YMax+3.1,bb.ZMin+.35);elbow=V(bb.XMax+2.7,root.y,root.z)
 c0,t0,h0=sample(4);last=c0+4.6*N
 parts.extend([beam(root,elbow,1.43),beam(elbow,last,1.43),Part.makeSphere(1.43,elbow)])
 tray=join(parts);orig=sh(host).Solids[0];s=orig
 for piece in tray.Solids:s=s.fuse(piece,.00001)
 s=s.removeSplitter()
 rec=dict(valid=s.isValid(),solids=[dict(volume=x.Volume,bounds=bounds(x)) for x in s.Solids],added=s.Volume-orig.Volume,root_join=tray.Volume+orig.Volume-s.Volume,resistor_center=list(pivot),basis='first 50 mm rigid in connector member (body/body/yaw); two insulated jacket grips outside windows',material_bounds=bounds(tray));result[role]=rec;wr('tap-carriers.json',result)
 assert rec['valid'] and len(s.Solids)==1
 D.getObject(host).Shape=s;tray.exportBrep(str(P/(role+'-tray.tmp.brep')))
# The source cap already opens beside the pitch return. Extend its moving-side
# lip where the re-clocked 196 mm reaches the fixed deck near +20 yaw.
n='E19_ForeLid';s=sh(n).Solids[0].cut(box(-32.8,-55.5,170.7,9.9,9,3.65),.00001).removeSplitter()
assert len(s.Solids)==1 and s.isValid();D.getObject(n).Shape=s
D.recompute();D.save()
