"""v17 - porzadki we wnetrzu kota.
   .brp maja placement wpieczony => global = flip(raw); ruszanym obiektom zerujemy Placement w XML."""
import os, math
import fc
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeCone, BRepPrimAPI_MakeSphere
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS, TopoDS_Compound
from OCP.gp import gp_Pnt, gp_Ax2, gp_Dir, gp_Vec
from OCP.BRep import BRep_Builder
from OCP.BRepTools import BRepTools as BT
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp

SRC = fc.SRC
def L(gx,gy,gz): return (2*fc.PIVOT_X-gx, -gy, gz)

def box_g(x0,x1,y0,y1,z0,z1):
    x,y,z = L(x1,y1,z0)
    return BRepPrimAPI_MakeBox(gp_Pnt(x,y,z), abs(x1-x0), abs(y1-y0), abs(z1-z0)).Shape()

def cyl_g(gx,gy,z0,z1,r):
    x,y,z = L(gx,gy,z0)
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x,y,z), gp_Dir(0,0,1)), r, z1-z0).Shape()

def cone_g(a, b, r1, r2):
    """stozek miedzy dwoma punktami GLOBALNYMI + kulka na koncu (jak w oryginale)"""
    A = gp_Pnt(*L(*a)); B = gp_Pnt(*L(*b))
    v = gp_Vec(A, B); h = v.Magnitude()
    cone = BRepPrimAPI_MakeCone(gp_Ax2(A, gp_Dir(v)), r1, r2, h).Shape()
    sph  = BRepPrimAPI_MakeSphere(B, r2).Shape()
    op = BRepAlgoAPI_Fuse(cone, sph); op.Build(); return op.Shape()

def fillet_all(shape, r):
    mk = BRepFilletAPI_MakeFillet(shape)
    ex = TopExp_Explorer(shape, TopAbs_EDGE)
    while ex.More(): mk.Add(r, TopoDS.Edge(ex.Current())); ex.Next()
    return mk.Shape()

def compound(ss):
    c=TopoDS_Compound(); b=BRep_Builder(); b.MakeCompound(c)
    for s in ss: b.Add(c,s)
    return c

def cut(a,b):
    op=BRepAlgoAPI_Cut(a,b); op.Build()
    if not op.IsDone(): raise RuntimeError("cut failed")
    return op.Shape()

def vol(s):
    p=GProp_GProps(); BRepGProp.VolumeProperties_s(s,p); return p.Mass()

def gbb(s):
    r=fc.bbox(s); return (2*fc.PIVOT_X-r[1], 2*fc.PIVOT_X-r[0], -r[3], -r[2], r[4], r[5])

def show(tag,s):
    print("  %-22s x[%7.1f,%7.1f] y[%6.1f,%6.1f] z[%6.1f,%6.1f] vol=%8.0f"%((tag,)+gbb(s)+(vol(s),)))

REBUILT = {
    'PiHatCooling':          (-19,  66, -28,   28,   67,  92),
    'PowerDistribution':     ( 66, 118, -32,   32,   78,  92),
    'PiCableAccess':         (-19,  28,  31,   41,   50,  70),
    'PWMControllerUnplaced': ( 35,  95, -49,  -34,   58,  98),
    'MainSwitch':            ( 88, 108,  37,   57,   65,  78),
    'ChargeSocketXT60':      ( 58,  74,  48,   56,   61,  83),
    'BalancerPort':          ( 36,  50,  50,   56,   67,  77),
    'Speaker':               (  6, 106, -22.5, 22.5, 95, 116),
    # schowane pod stozkami szyi i ogona
    'NeckBridge':            (-88, -60, -22,   22,   40,  43),
    'NeckYawServo':          (-86, -62, -12,   12,   45,  74),
    'TailBridge':            (121, 148, -17,   17,   40,  43),
    'TailYawServo':          (140, 164, -12,   12,   52,  72),
    'TailLiftServo':         (124, 144,  -6,    6,   50,  70),
}
TOUCHED = list(REBUILT) + ['BackCover','TailBase','BatteryTray','BellyPod','NeckColumn']

def main():
    n2f = fc.shapefiles()
    print("== obwiednie przebudowane ==")
    for nm,g in REBUILT.items():
        s=box_g(*g); BT.Write_s(s, os.path.join(SRC,n2f[nm])); show(nm,s)

    print("== grzbiet: kratka glosnika + otwory zlaczy ==")
    shell=fc.load('BackCover',n2f); show('przed',shell)
    holes=[]; cx,cy,R,r,pitch=56.0,0.0,21.0,1.6,6.2
    rows=int(R/(pitch*math.sqrt(3)/2))+1; k=int((R+pitch)/pitch)
    for j in range(-rows,rows+1):
        yy=cy+j*pitch*math.sqrt(3)/2; off=(pitch/2) if (j%2) else 0.0
        for i in range(-k,k+1):
            xx=cx+i*pitch+off
            if (xx-cx)**2+(yy-cy)**2<=(R-r)**2: holes.append(cyl_g(xx,yy,100.0,135.0,r))
    print("  otworow kratki:",len(holes))
    shell=cut(shell,compound(holes))
    for ap in (box_g(92,104,45,70,68,76), box_g(61,71,45,70,65,79), box_g(39,47,45,70,69.5,74.5)):
        shell=cut(shell,ap)
    BT.Write_s(shell, os.path.join(SRC,n2f['BackCover'])); show('po',shell)

    print("== nasada ogona: kieszenie na serwa ==")
    tb=fc.load('TailBase',n2f); show('przed',tb)
    for p in (box_g(139,165,-13.5,13.5,50.5,73.5),
              box_g(123,145, -7.5, 7.5,48.5,71.5),
              box_g(119.5,149,-18.5,18.5,38.5,44.5)):
        tb=cut(tb,p)
    BT.Write_s(tb, os.path.join(SRC,n2f['TailBase'])); show('po',tb)

    print("== kolyska akumulatora ==")
    bt=fc.load('BatteryTray',n2f); show('przed',bt)
    bt=cut(bt, box_g(-18.4,72.4,-21.9,21.9,5.9,26.0))
    BT.Write_s(bt, os.path.join(SRC,n2f['BatteryTray'])); show('po',bt)

    print("== brzusiec: owiewka wokol podwozia WAVEGO (sciana 3 mm) ==")
    bp = fillet_all(box_g(-86,126,-53,53,2,40), 14.0)
    show('owiewka pelna', bp)
    bp = cut(bp, fillet_all(box_g(-83,123,-50,50,-2,44), 11.0))
    BT.Write_s(bp, os.path.join(SRC,n2f['BellyPod'])); show('po wydrazeniu',bp)

    print("== kolumna szyi: wydrazenie (sciana 3 mm) ==")
    nc=fc.load('NeckColumn',n2f); show('przed',nc)
    nc=cut(nc, cone_g((-74.0,0.0,58.0), (-130.0,0.0,102.0), 28.0, 21.0))
    BT.Write_s(nc, os.path.join(SRC,n2f['NeckColumn'])); show('po',nc)

if __name__=='__main__': main()
