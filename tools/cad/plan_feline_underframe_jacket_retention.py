"""Four common removable bars for the seventeen underframe jacket fields.

N01 constructive study, not N03 feature-tree/print or physical pull approval.
Only local nominal jacket profiles are modeled: unequal OD must actually reach
both bed and cap. No end-to-end conductor trajectories are generated.
"""
import FreeCAD as A
import Part


def isolated(s):
    q=Part.Shape(); q.importBrepFromString(s.exportBrepToString()); return q


def box(lo,hi):
    return Part.makeBox(*(b-a for a,b in zip(lo,hi)),A.Vector(*lo))


def build(carrier):
    groups={
        'G2':dict(axis=0,land=[6.5,15.5],centres=[-25.5,-20.75,-16,-11.25,-6.5],
                  radii=[1.25,1.55,1.55,1.55,1.55],z=-10.25,bed_bottom=-13.8,
                  cap_span=[8.5,13.5],band_at=11.,ids=['XA05/extra/start','W003/retained0/end','W063/retained0/start','W062/retained0/start','W061/retained0/end']),
        'D_FR':dict(axis=0,land=[6.5,15.5],centres=[6.5,11.25,16,20.75,25.5],
                    radii=[1.55]*5,z=-10.25,bed_bottom=-13.8,
                    cap_span=[8.5,13.5],band_at=11.,ids=['W007/retained0/end','W008/body/end','W009/body/end','W010/body/end','W011/retained0/start']),
        'FL_P':dict(axis=1,land=[-18.5,-9.5],centres=[11.5,16.25,21,25.75],
                    radii=[2.1,1.55,1.55,1.55],z=-20.5,bed_bottom=-24.6,
                    cap_span=[-16.5,-11.5],band_at=-14.,ids=['W026/custom/end','W027/single/start','W028/single/start','W029/single/start']),
        'P_FRONT':dict(axis=1,land=[11,20],centres=[-2.5,4,10.5],
                       radii=[2.1]*3,z=-33,bed_bottom=-37.1,
                       cap_span=[13,18],band_at=16.5,ids=['W064/single/start','W042/custom/end','W041/custom/end'])}
    caps={};bands={};heads={};profiles={};shims=[];records={}
    for name,g in groups.items():
        ax=g['axis'];z=g['z'];lo=min(c-r for c,r in zip(g['centres'],g['radii']))-2
        hi=max(c+r for c,r in zip(g['centres'],g['radii']))+2;top=z+max(g['radii'])+2
        # FL_P faces the adjacent G2 case. Use an open-ended pressure spreader
        # over all four wire centres, not closed outer side cheeks that force
        # the complete band into G2. The bed still supports each full profile.
        if name=='FL_P':lo,hi=min(g['centres'])-1,max(g['centres'])+1
        rect=lambda u0,u1,v0,v1,z0,z1:box([u0,v0,z0],[u1,v1,z1]) if ax==0 else box([v0,u0,z0],[v1,u1,z1])
        cap=rect(*g['cap_span'],lo,hi,z,top)
        for eid,c,r in zip(g['ids'],g['centres'],g['radii']):
            origin=[g['land'][0],c,z] if ax==0 else [c,g['land'][0],z]
            direction=A.Vector(1,0,0) if ax==0 else A.Vector(0,1,0)
            jacket=Part.makeCylinder(r,9,A.Vector(*origin),direction);profiles[eid]=jacket
            cap=cap.cut(isolated(jacket))
            bed_top=g['bed_bottom']+2
            if z-r>bed_top+1e-6:
                shims.append(rect(*g['land'],c-r,c+r,bed_top-.3,z-r))
        cap=cap.removeSplitter();cap.check(True);assert len(cap.Solids)==1,name
        # Complete nominal2.5x1.2 band around cap AND bed; head is not clipped.
        innerlo,innerhi=lo-.2,hi+.2
        # The two upper beds overlap FL_P in plan. Thread the lower band run
        # through a .7mm-deep channel in our 2mm bed rather than hanging the
        # entire run below it. Leaves1.3mm minimum nominal bed ligament.
        thread_depth=.7 if name in ('G2','D_FR') else 0
        bottom=g['bed_bottom']-.2+thread_depth
        band=rect(g['band_at']-1.25,g['band_at']+1.25,innerlo-1.2,innerhi+1.2,bottom-1.2,top+1.4)
        band=band.cut(rect(g['band_at']-1.5,g['band_at']+1.5,innerlo,innerhi,bottom,top+.2))
        # Both upper closures face OUTBOARD: an inward D_FR head would meet
        # the G2 loop in the shared inter-bed gap. Change the complete closure
        # direction, not a wire centre or a clearance requirement.
        head_side=1 if name=='D_FR' else -1
        headlo,headhi=(innerhi+1.2,innerhi+5.5) if head_side>0 else (innerlo-5.5,innerlo-1.2)
        head=rect(g['band_at']-2.5,g['band_at']+2.5,headlo,headhi,z-2.65,z+2.65)
        band.check(True);head.check(True)
        loop=2*((innerhi-innerlo)+1.2+(top+.2-bottom)+1.2)
        assert loop+25<=100+1e-7,(name,loop)
        caps[name]=cap;bands[name]=band;heads[name]=head
        records[name]={**g,'cap_wall_above_largest_profile_mm':2,'supported_jacket_length_mm':9,
            'bar_axial_width_mm':5,'band_width_mm':2.5,'neutral_loop_project_mm':loop,
            'head_and_usable_tail_allowance_mm':25,'nominal_selected_T18I100_mm':100,
            'remaining_project_length_mm':100-loop-25,'bed_channel_depth_mm':thread_depth,
            'bed_ligament_after_channel_mm':2-thread_depth,
            'open_ended_pressure_spreader':name=='FL_P',
            'closure_head_side':head_side,
            'case_port_assignment':'Project slot assignment on same common-potential WAGO, not manufacturer cavity data',
            'physical_each_wire_pull_and_actual_OD_required':True}
    current=isolated(carrier)
    if shims:current=current.multiFuse(shims).removeSplitter()
    for n,b in bands.items():
        clearance=isolated(b).makeOffsetShape(.2,1e-5,join=2)
        current=current.cut(clearance)
        current=current.cut(isolated(heads[n]).makeOffsetShape(.2,1e-5,join=2))
    current=current.removeSplitter();current.check(True);assert len(current.Solids)==1
    return current,caps,bands,heads,profiles,records
