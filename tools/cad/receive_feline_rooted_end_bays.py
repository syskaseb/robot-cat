"""End-bay allocation: outward rear bolts, rooted full grips, separate fore fan.

Reuses one whole-scene receiver, not a new pose search. Bought cases stay
unchanged. Planning solids only; native/editable production detail is N03.
"""
import math,os
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from receive_feline_end_bay_outputs import main,WIRES,bend,pipe


def box(lo,hi):return Part.makeBox(*(np.asarray(hi)-lo),A.Vector(*lo))


def shoe(case):
    """Same removable side cap concept, bolts outside both fuse and root web.

    absY30.5 >= F_AUX25.5 + full driverR3.35 + gap1.25 + .4.
    No straps over the bought inline connector's levers.
    """
    b=case.BoundBox;x,y,z=list(b.Center);side=1 if y>0 else -1
    edge=b.YMax if side>0 else b.YMin;bolt_y=side*30.5
    base=box([b.XMin-1.25,b.YMin-.25,-42.2],[b.XMax+1.25,b.YMax+.25,b.ZMin])
    for a,c in ((b.XMin-1.25,b.XMin-.25),(b.XMax+.25,b.XMax+1.25)):
        base=base.fuse(box([a,b.YMin-.25,-42.2],[c,b.YMax+.25,-36.4]))
    ya,yb=sorted((edge-side*.25,bolt_y+side*3.5))
    # Only the aft arm carries the two bosses. An arm at x127 intersects
    # the preserved belly foot/web; changing bolt-Y alone cannot solve it.
    base=base.fuse(box([x+1.5,ya,-42.2],[x+15.5,yb,b.ZMin]))
    wy0,wy1=sorted((side*18.3,side*21.5))
    base=base.fuse(box([126.5,wy0,-42.1],[129.5,wy1,-38.5]))
    bottom=b.ZMax+.25;top=bottom+2
    # Full2mm spine lies ABOVE the bought case, not in the fixed web gap.
    # Web innerY20.5 - case outerY19.05 =1.45mm, without moving the case.
    sy0,sy1=(edge-2,edge) if side>0 else (edge,edge+2)
    cap=box([b.XMin+1,sy0,bottom],[b.XMax-1,sy1,top]);hardware={}
    for a,c in ((b.XMin+2,b.XMin+4),(b.XMax-4,b.XMax-2)):
        ca=b.YMin-1.25 if side>0 else b.YMin-2.75;cb=b.YMax+2.75 if side>0 else b.YMax+1.25
        cap=cap.fuse(box([a,ca,bottom],[c,cb,top]))
        la,lb=(b.YMin-1.25,b.YMin-.25) if side>0 else (b.YMax+.25,b.YMax+1.25)
        cap=cap.fuse(box([a,la,b.ZMax-1],[c,lb,bottom+.2]))
    for i,bx in enumerate((x+5,x+12)):
        cap=cap.fuse(box([bx-3.5,min(bolt_y-3.5,sy0),bottom],[bx+3.5,max(bolt_y+3.5,sy1),top]))
        base=base.fuse(Part.makeCylinder(3.5,bottom+42.2,A.Vector(bx,bolt_y,-42.2)))
        bore=Part.makeCylinder(1.15,20,A.Vector(bx,bolt_y,-43));base=base.cut(bore);cap=cap.cut(bore)
        pts=[A.Vector(bx+2.4*math.cos(j*math.pi/3),bolt_y+2.4*math.sin(j*math.pi/3),-38.3) for j in range(6)]
        base=base.cut(Part.Face(Part.Wire(Part.makePolygon(pts+[pts[0]]).Edges)).extrude(A.Vector(0,0,1.8)))
        hardware['CapScrew',i]=Part.makeCylinder(1,12,A.Vector(bx,bolt_y,top),A.Vector(0,0,-1)).fuse(Part.makeCylinder(1.9,1.5,A.Vector(bx,bolt_y,top)))
        pts=[A.Vector(bx+2.3094*math.cos(j*math.pi/3),bolt_y+2.3094*math.sin(j*math.pi/3),-38.2) for j in range(6)]
        hardware['CapNut',i]=Part.Face(Part.Wire(Part.makePolygon(pts+[pts[0]]).Edges)).extrude(A.Vector(0,0,1.6)).cut(Part.makeCylinder(.8,2,A.Vector(bx,bolt_y,-38.3)))
    return base.removeSplitter(),cap.removeSplitter(),hardware


def revision(actors,meta,owner,original,recipes,old,fixed,parts,worldmeta):
    mates={};roots={};captured=[];print_groups=[]
    # W037's upper return is a separate inward-Y fan, not the rejected common
    # X-plane crossing the actual W068 saddle at (-129.5,-17.8,32.9).
    r=recipes['W037'];cc=r['custom'][:-1];q=np.asarray(cc[-1]['end']);d=np.array([0.,0,1]);q,t=bend(cc,q,d,[0,1,0],25.2)
    r.update(custom=cc,custom_exit=q.tolist(),custom_axis=t.tolist(),custom_prefix_mm=sum(e['length_mm'] for e in cc))
    actors['EndCustom:W037']=pipe(cc,2.1)
    for w in WIRES:
        fore=w in WIRES[:2];side=1 if recipes[w]['centre'][1]>0 else -1
        panel='LowerBay:'+('ForePanel' if fore else 'RearPanel');web='RootWebReserve'+str((2 if side>0 else 1) if fore else (4 if side>0 else 3))
        base_name='EndBay:CaseBase:'+w+'_Joint';case=actors['EndBay:Ref_Material_'+w+'_Joint_0_0']
        if not fore:
            base,cap,hw=shoe(case);actors[base_name]=base;actors['EndBay:CaseCap:'+w+'_Joint']=cap
            for (kind,i),s in hw.items():actors['EndBay:'+kind+':'+w+'_Joint:'+str(i)]=s
        else:
            ya,yb=sorted((side*18.3,side*21.5))
            actors[base_name]=actors[base_name].fuse(box([-87,ya,-42.1],[-84,yb,-38.5])).removeSplitter()
        mates[base_name]=[panel,web]
        # Place factory's full9 at the named 1.25mm case margin, not .25.
        from receive_feline_positive_service_deck import open_grip
        d=np.asarray(recipes[w]['d']);end=np.asarray(recipes[w]['factory_end']);u=np.array([0.,side,0.])
        start=end-10.25*d;kit=open_grip(start,d,u,4.5);kit['pad'].translate(A.Vector(*(-.25*u)))
        for k,s in kit.items():actors['EndGrip:Factory:'+w+':'+k]=s
        pad='EndGrip:Factory:'+w+':pad';b=actors[pad].BoundBox
        # Root at the first2mm axial end: complete band occupies3.25..5.75.
        px0,px1=(b.XMin,b.XMin+2) if d[0]>0 else (b.XMax-2,b.XMax)
        pillar=box([px0,b.YMin,-43.3],[px1,b.YMax,b.ZMin+1])
        ya,yb=sorted((side*17.25,side*24))
        toe=box([px0,ya,-43.3],[px1,yb,-40.8])
        actors[pad]=actors[pad].fuse(pillar).fuse(toe).removeSplitter();mates[pad]=[panel]
        pad='EndGrip:Custom:'+w+':pad';b=actors[pad].BoundBox
        cy0,cy1=sorted((side*21,side*23));ty0,ty1=sorted((side*12.4,side*23))
        if fore:
            foot=box([b.XMin,cy0,-42.2],[-120.5,cy1,-39.7])
            column=box([b.XMin,cy0,-42.2],[b.XMax,cy1,b.ZMax+1.3])
            top=box([b.XMin,ty0,b.ZMax-.7],[b.XMax,ty1,b.ZMax+1.3])
            support=foot.fuse(column).fuse(top)
        else:
            # Actual panel at x147 has no material here (root preflight,
            # not its bbox). Root through the positively anchored shoe's
            # outer foot instead, outside the complete screw/tool column.
            ya,yb=sorted((side*36,side*38))
            fy0,fy1=sorted((side*33,side*38))
            toe=box([137,fy0,-42.2],[139,fy1,-39.7])
            foot=box([137,ya,-42.2],[139,yb,-10.5]).fuse(toe)
            a=np.array([138.,side*37]);c=np.array([b.Center.x,side*22]);v=c-a;v/=np.linalg.norm(v);normal=np.array([-v[1],v[0]])
            pts=[A.Vector(*xy,-13) for xy in (a-normal,c-normal,c+normal,a+normal)]
            beam=Part.Face(Part.Wire(Part.makePolygon(pts+[pts[0]]).Edges)).extrude(A.Vector(0,0,2.5))
            column=box([b.XMin,cy0,-13],[b.XMax,cy1,b.ZMax+1.3])
            top=box([b.XMin,ty0,b.ZMax-.7],[b.XMax,ty1,b.ZMax+1.3])
            support=foot.fuse(beam).fuse(column).fuse(top)
        actors[pad]=actors[pad].fuse(support).removeSplitter();mates[pad]=[panel] if fore else [base_name]
        roots[w]=dict(base_panel_common_mm3=actors[base_name].common(parts[panel]).Volume,base_web_common_mm3=actors[base_name].common(parts[web]).Volume,
            factory_pad_panel_common_mm3=actors['EndGrip:Factory:'+w+':pad'].common(parts[panel]).Volume,
            custom_pad_root_common_mm3=actors[pad].common(parts[panel] if fore else actors[base_name]).Volume,
            custom_root_parent=panel if fore else base_name)
        for k,v in roots[w].items():
            if k.endswith('_mm3'):assert v>1e-5,('Missing constructive root',w,roots[w])
        if not fore:captured += [['EndBay:CapNut:'+w+'_Joint:'+str(i),panel] for i in (0,1)]
    # These are features of TWO intended printed panels, not unrelated
    # plastic parts that require an invented air gap from one another.
    for fore in (True,False):
        panel='LowerBay:'+('ForePanel' if fore else 'RearPanel');ws=WIRES[:2] if fore else WIRES[2:]
        members=[panel,*(['RootWebReserve1','RootWebReserve2'] if fore else ['RootWebReserve3','RootWebReserve4'])]
        members += [n for w in ws for n in ('EndBay:CaseBase:'+w+'_Joint','EndGrip:Factory:'+w+':pad','EndGrip:Custom:'+w+':pad')]
        shapes=[actors[n] if n in actors else parts[n] for n in members]
        union=shapes[0].multiFuse(shapes[1:]).removeSplitter()
        assert union.isValid() and len(union.Solids)==1,('Disconnected planned print',panel,len(union.Solids))
        print_groups.append(dict(panel=panel,members=members,union_solids=1,volume_mm3=union.Volume))
    for n,s in actors.items():assert s.isValid() and len(s.Solids)==1,n
    return dict(root_mates=mates,positive_load_paths=roots,planned_print_unions=print_groups,captured_nut_panel_pairs=captured,rear_bolt_absY_mm=30.5,rear_bolt_X_mm=[137,144],
        rear_driver_R_mm=3.35,rear_driver_fuse_clearance_mm=1.65,driver_full_sweep_OPEN=True,
        native_production_details_not_claimed=True)


if __name__=='__main__':
    print('WORKER_PID',os.getpid(),flush=True)
    from plan_feline_layout import OUT
    changed=['EndBay:CaseCap:'+w+'_Joint' for w in WIRES[2:]]
    main(revision,'n01-rooted-end-bays-caps',(Path(__file__),),OUT/'n01-rooted-end-bays-side-bridges.json',changed)
