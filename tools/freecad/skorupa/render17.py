import os, math, numpy as np, xml.etree.ElementTree as ET
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.colors as mcolors
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import fc

SRC = fc.SRC

def placements():
    r = ET.parse(os.path.join(SRC,'Document.xml')).getroot()
    out={}
    for o in r.find('ObjectData').findall('Object'):
        for p in o.iter('Property'):
            if p.get('name')=='Placement':
                pp=p.find('.//PropertyPlacement')
                if pp is not None:
                    out[o.get('name')]=(float(pp.get('Px')),float(pp.get('Py')),float(pp.get('Pz')))
    return out

SHELL = ('BackCover','HeadFront','HeadRear','Muzzle','Nose','Ear','EyeLens','EyeRing',
         'NeckCollar','TailSocket','TailSegment','TailJoint','ToF','NeckColumn','TailBase','BellyPod')
DARK  = ('EyeLens','Nose','TailJoint','EarInset','ToF')
GUTS  = {'Battery':'#c0392b','Pi':'#2e8b57','PiHatCooling':'#3a7d5d','PiCableAccess':'#7f8c8d',
         'Pololu':'#b8860b','AuxBuck':'#b8860b','BusAdapter':'#8e44ad','PowerDistribution':'#d35400',
         'IMU':'#16a085','Touch':'#16a085','AudioAmp':'#16a085','Speaker':'#1f6fb4',
         'PWMControllerUnplaced':'#27ae60','ComputerDeck':'#95a5a6','BatteryTray':'#95a5a6',
         'NeckBridge':'#95a5a6','TailBridge':'#95a5a6','NeckYawServo':'#34495e',
         'TailYawServo':'#34495e','TailLiftServo':'#34495e','HeadPitchServo':'#34495e',
         'MainSwitch':'#e74c3c','ChargeSocketXT60':'#e67e22','BalancerPort':'#e67e22',
         'Camera':'#111111','Microphones':'#2c3e50','IrIlluminator':'#8e44ad'}

def collect(names, n2f, pl, defl=1.2):
    polys=[]
    for n in names:
        if n not in n2f: continue
        try: sh = fc.load(n, n2f)
        except Exception: continue
        for t in fc.tris(sh, defl):
            polys.append(tuple((2*fc.PIVOT_X-v[0], -v[1], v[2]) for v in t))
    return polys

def shade(polys, col, gain=1.0):
    L=np.array([0.45,-0.75,0.5]); L/=np.linalg.norm(L); base=np.array(mcolors.to_rgb(col)); out=[]
    for t in polys:
        a,b,c=(np.array(v) for v in t); nn=np.cross(b-a,c-a); ln=np.linalg.norm(nn)
        lam=0.0 if ln==0 else abs(float(np.dot(nn/ln,L)))
        f=(0.34+0.66*lam)*gain
        out.append(tuple(np.clip(base*f+0.06*lam**6,0,1)))
    return out

LEGS = {'FL':((130.810,16.0,18.5),(146.398,60.484,12.258),(196.164,79.516,-80.071)),
        'FR':((130.810,-16.0,18.5),(146.398,-60.484,12.258),(196.164,-79.516,-80.071)),
        'RL':((-88.810,16.0,18.5),(-104.398,60.484,12.258),(-54.631,79.516,-80.071)),
        'RR':((-88.810,-16.0,18.5),(-104.398,-60.484,12.258),(-54.631,-79.516,-80.071))}

CHASSIS = ['Part__Feature','Part__Feature002','Part__Feature003','Part__Feature005',
           'Part__Feature038','Part__Feature107','Part__Feature111','Part__Feature112',
           'Part__Feature105','Part__Feature106']

def collect_raw(names, n2f, defl=1.6):
    polys=[]
    for n in names:
        if n not in n2f: continue
        try: sh = fc.load(n, n2f)
        except Exception: continue
        for t in fc.tris(sh, defl): polys.append(t)
    return polys

def render(out_png, title, elev=18, azim=-62, ghost=False, defl=1.2, chassis=True):
    n2f = fc.shapefiles(); pl = placements()
    shell_names = [n for n in n2f if n.startswith(SHELL)]
    gut_names   = [n for n in GUTS if n in n2f]
    fig = plt.figure(figsize=(13,8)); ax = fig.add_subplot(111, projection='3d')
    allpts=[]
    if ghost:
        for n in gut_names:
            ps = collect([n], n2f, pl, defl)
            if not ps: continue
            ax.add_collection3d(Poly3DCollection(ps, facecolors=shade(ps,GUTS[n]), edgecolors='none'))
            allpts += [v for t in ps for v in t]
        ps = collect(shell_names, n2f, pl, defl)
        pc = Poly3DCollection(ps, facecolors=shade(ps,'#8899aa',1.15), edgecolors='none'); pc.set_alpha(0.16)
        ax.add_collection3d(pc); allpts += [v for t in ps for v in t]
    else:
        for n in gut_names:
            ps = collect([n], n2f, pl, defl)
            if not ps: continue
            ax.add_collection3d(Poly3DCollection(ps, facecolors=shade(ps,GUTS[n]), edgecolors='none'))
            allpts += [v for t in ps for v in t]
        for n in shell_names:
            ps = collect([n], n2f, pl, defl)
            if not ps: continue
            col = '#23272c' if n.startswith(DARK) else '#4a5159'
            ax.add_collection3d(Poly3DCollection(ps, facecolors=shade(ps,col), edgecolors='none'))
            allpts += [v for t in ps for v in t]
    if chassis:
        ps = collect_raw(CHASSIS, n2f)
        if ps:
            ax.add_collection3d(Poly3DCollection(ps, facecolors=shade(ps,'#6b7078'), edgecolors='none'))
            allpts += [v for t in ps for v in t]
    for ch in LEGS.values():
        ax.plot([p[0] for p in ch],[p[1] for p in ch],[p[2] for p in ch],'-o',color='#1f6fb4',lw=3,ms=5)
        allpts += list(ch)
    A=np.array(allpts); c=A.mean(axis=0); r=(A.max(axis=0)-A.min(axis=0)).max()/2*0.62
    ax.set_xlim(c[0]-r,c[0]+r); ax.set_ylim(c[1]-r,c[1]+r); ax.set_zlim(c[2]-r,c[2]+r)
    ax.set_box_aspect((1,1,1)); ax.view_init(elev=elev,azim=azim); ax.set_axis_off()
    ax.set_title(title,fontsize=13,pad=4); fig.tight_layout()
    fig.savefig(out_png,dpi=145,facecolor='white'); plt.close(fig)
    print("zapisano",out_png)

if __name__=='__main__':
    import sys
    render(sys.argv[1], sys.argv[2], elev=float(sys.argv[3]), azim=float(sys.argv[4]),
           ghost=(len(sys.argv)>5 and sys.argv[5]=='ghost'))
