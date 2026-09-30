"""One constant-length external pitch-servo harness loop on the selected head.

Only new cable/head interfaces. No old horn/key/rim audit repeated. A bundle
reservation models three separately insulated silicone leads, not a real cable.
"""
import json,math,sys
from pathlib import Path
import xb11_upstream_route as R
sys.path.insert(0,str(R.ROOT/'tools/cad'))
from check_main_p0_placement import SavedShapes,prop
A,Part,ROOT=R.A,R.Part,R.ROOT
OUT=ROOT/'hardware/electronics/full-cat/head-external-yaw-loop-r1'
HEAD=ROOT/'hardware/cad/studies/head-p8/head-printed-horns-r2/HeadPrintedPitchYawR2_CANDIDATE.FCStd'
def dump(n,x):(OUT/n).write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def mv(s,yaw,pitch=0):
    v=s.copy()
    if pitch:v.rotate(A.Vector(-152,0,136),A.Vector(0,1,0),pitch)
    if yaw:v.rotate(A.Vector(-110,-5.25,0),A.Vector(0,0,1),yaw)
    return v
def path(yaw,length=210):
    start=A.Vector(-133,10.5,119);start=mv(Part.Vertex(start),yaw).Vertexes[0].Point
    end=A.Vector(-90,60,119);d=end-start;chord=d.Length;u=d/chord
    lo,hi=.001,2*math.pi-.001
    for _ in range(70):
        t=(lo+hi)/2
        if t/(2*math.sin(t/2))>length/chord:hi=t
        else:lo=t
    phi=(lo+hi)/2;r=length/phi
    n=A.Vector(-u.y*math.cos(math.pi/6),u.x*math.cos(math.pi/6),-math.sin(math.pi/6))
    middle=(start+end)/2+n*r*(1-math.cos(phi/2))
    arc=Part.Arc(start,middle,end).toShape();assert abs(arc.Length-length)<1e-5
    p=Part.Wire([arc]);tangent=arc.tangentAt(arc.FirstParameter)
    w=p.makePipeShell([Part.Wire([Part.makeCircle(2.5,start,tangent)])],True,False)
    assert w.isValid() and len(w.Solids)==1
    return p,w,r
def main():
    assert not (OUT/'checks.json').exists();OUT.mkdir(exist_ok=True)
    plan=dict(status='SOURCE_BEFORE_CONSTANT_LENGTH_EXTERNAL_LOOP',
      wires=['XB22 F_HP.out->C_HP.V+ HELU23302 red0.5mm2 OD2.1','XB23 C_HP.GND->G_AUX.4 HELU23301 black0.5mm2 OD2.1','XS23 U1/R2 output->C_HP.PWM Kamami1178401 yellow26AWG supplier0.12mm2 OD1.25'],
      PWM_source='https://kamami.pl/przewody-jednozylowe/1178401-zestaw-przewodow-jednozylowych-silikonowych-26awg-5906623468454.html',
      PWM_condition='Silicone stranded hobby candidate, no supplier cyclic-life/minimum-radius certificate; use R>=31.5mm and inspect during phase2. Not0.14mm2; do not put undersized lead in a terminal requiring0.14 minimum.',
      power_radius_mm={'fixed':12.6,'moving':31.5},bundle_envelope_OD_mm=5,
      packing='Two OD2.1 centers(-1.05,0)/(1.05,0), OD1.25 center(0,1.31), inside a5mm circle; no braid sleeve adding unaccounted diameter.',
      loop_length_mm=210,plane='Chord with outward-left normal tilted30deg down; avoids adding a moving wire through journal/bearing.',
      moving_anchor_rest_mm=[-133,10.5,119],fixed_anchor_mm=[-90,60,119],
      anchor_basis='Cable at +Y outside existing side bar Y8, radius2.5 gives centerY10.5. Existing fixed Deck tie outsidepost. Actual angle/tie pressure and all end transitions still require construction.',
      frames='Pitch servo housing/Carrier follows yaw only. Head shell follows pitch then yaw; fixed yaw servo housing never receives moving loop.',
      sampled_yaw_deg=[-15,0,15],sampled_pitch_deg=[-10,0,5],
      scope='New external loop only, not whole harness or continuous physical sweep. Constant arc length and radius solved perpose; factory250mm lead/JR splice and end transitions remain separate.',
      new_stls=0,phase1_complete=False,physical_pass=False)
    dump('plan.json',plan);reader=SavedShapes();shells={}
    for n in ('FrontLeft','FrontRightPorted','Rear','Nose','EarL','EarR','CageBase','CageRetainerLeft','CageRetainerRight'):
        shells[n]=reader.shape(HEAD,n)
    yawparts={}
    for p,n in [('hardware/cad/studies/head-p8/head-yaw-open-key-r1/UpperForkOpenKey.FCStd','UpperFork'),('hardware/cad/studies/head-p8/pitch-support-r3/PitchBearingFork.FCStd','PitchRetainer')]:
        yawparts[n]=reader.shape(ROOT/p,n)
    p=ROOT/'hardware/cad/studies/head-p8/shell-mount-r2/PitchCarrierAccess.FCStd';parent=reader.placement(reader.doc(p)['PitchInstallation'])
    for n in ('Carrier','ServoReference'):
        s=reader.shape(p,n);s.Placement=parent*s.Placement;yawparts['Pitch_'+n]=s
    fixed={}
    for p,n in [('hardware/cad/studies/upper-cover-mount-r1/RaisedUpperCoverMount.FCStd','CoverMountHole4'),('hardware/cad/studies/xb11-hangers-r2/DeckXB11Hangers.FCStd','Deck'),('hardware/cad/studies/head-p8/head-fixed-deck-tie-r2/HeadFixedDeckTieR2.FCStd','FixedDeckTie')]:
        try:fixed[n]=reader.shape(ROOT/p,n)
        except KeyError:
            if n!='FixedDeckTie':raise
            doc=reader.doc(ROOT/p);names=[k for k,v in doc.items() if prop(v,'Shape') is not None and k in ('FixedTie','Bracket','Tie','HeadFixedDeckTie')]
            assert len(names)==1,names;fixed[n]=reader.shape(ROOT/p,names[0])
    rows=[];summ=[]
    for yaw in plan['sampled_yaw_deg']:
        p,w,r=path(yaw);w.exportBrep(str(OUT/f'loop_yaw{yaw:+}.brep'))
        summ.append(dict(yaw=yaw,length_mm=p.Length,radius_mm=r,bbox_mm=[w.BoundBox.XMin,w.BoundBox.YMin,w.BoundBox.ZMin,w.BoundBox.XMax,w.BoundBox.YMax,w.BoundBox.ZMax],samples=[[v.x,v.y,v.z] for v in p.Edges[0].discretize(Deflection=.1)]))
        for name,s in {**fixed,**{k:mv(v,yaw) for k,v in yawparts.items()}}.items():
            for i,t in enumerate(s.Solids):
                if R.overlap(t.BoundBox,w.BoundBox):
                    hit=t.common(w);vol=R.volume(hit);rows.append(dict(yaw=yaw,pitch=None,owner=name,solid=i,positive_mm3=vol,centers=[list(v.CenterOfMass) for v in hit.Solids] if vol>1e-5 else []))
        for pitch in plan['sampled_pitch_deg']:
            for name,s in shells.items():
                for i,t in enumerate(mv(s,yaw,pitch).Solids):
                    if R.overlap(t.BoundBox,w.BoundBox):
                        hit=t.common(w);vol=R.volume(hit);rows.append(dict(yaw=yaw,pitch=pitch,owner=name,solid=i,positive_mm3=vol,centers=[list(v.CenterOfMass) for v in hit.Solids] if vol>1e-5 else []))
    hits=[r for r in rows if r['positive_mm3']>1e-5]
    for group in (shells,yawparts,fixed):
        for n,s in group.items():s.exportBrep(str(OUT/(n+'_REST.brep')))
    dump('checks.json',dict(status='LOOP_REJECTED' if hits else 'LOOP_SAMPLED_CANDIDATE',source_sha256=reader.hashes,script_sha256=R.sha(Path(__file__)),plan_sha256=R.sha(OUT/'plan.json'),
      loop_poses=summ,exact_pairs=rows,hits=hits,min_sampled_radius_mm=min(s['radius_mm'] for s in summ),new_stls=0,physical_pass=False,phase1_complete=False))
    print(json.dumps(dict(hits=hits,pairs=len(rows),radii=[s['radius_mm'] for s in summ])),flush=True)
if __name__=='__main__':main()
