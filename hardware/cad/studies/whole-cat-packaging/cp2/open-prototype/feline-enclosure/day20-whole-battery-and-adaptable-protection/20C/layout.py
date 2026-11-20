"""Fixed +Y inlet, complete lead budgets, and the changed module mounts."""
import json
import math
from pathlib import Path
import FreeCAD as App
import Part

ACTIVE_X = 25.25
POS_Z = 137.0
NEG_Z = 145.0
POST_MOUTH_X = 81.0
F0_IN = (8.,-15.,141.25)
F0_OUT = (8.,-66.,141.25)
ACTIVE_M = [14.25,18,132.25,36.25,43,148.75]
PACK_F = [14.25,43,132.25,36.25,68,148.75]
FUSE_FULL = [-.75,-66,130.5,16.75,-15,152.]
POST_FULL = [81.,-89.25,142.,101.,-76.25,152.]
POST_ADJUST_X = (58.,84.)

def length(points):
    return sum(math.dist(a,b) for a,b in zip(points,points[1:]))

def bezier(p0,p1,p2,p3,segments=240):
    p = [App.Vector(*row) for row in [p0,p1,p2,p3]]
    path=[]; radii=[]
    for i in range(segments+1):
        t=i/segments; u=1-t
        w=p[0]*(u**3)+p[1]*(3*u*u*t)+p[2]*(3*u*t*t)+p[3]*(t**3)
        d=(p[1]-p[0])*(3*u*u)+(p[2]-p[1])*(6*u*t)+(p[3]-p[2])*(3*t*t)
        e=(p[2]-p[1]*2+p[0])*(6*u)+(p[3]-p[2]*2+p[1])*(6*t)
        path.append([w.x,w.y,w.z])
        radii.append(d.Length**3/max(d.cross(e).Length,1e-7))
    return path,min(radii)

def factory_pack_witness(prior):
    out={}
    for pole,z,y0 in [('plus',POS_Z,32.65),('minus',NEG_Z,27.35)]:
        s=[78.3,y0,94.]
        port=[58.25,58.,z]
        # Preserve the 20B corner witness up to the first supported turn.
        prefix=[p for p in prior['battery'][pole]['points'] if p[2]<94]
        prefix.append(s)
        # Return toward vertical before going above BNO. This reserves a
        # high, accessible diagonal transfer, beyond the hard AUX edge.
        theta=2*math.atan2(8.2,20.5)
        recover=[]
        for i in range(61):
            t=theta*(1-i/60)
            recover.append([s[0]-17*(math.cos(t)-math.cos(theta)),y0,
                            s[2]+17*(math.sin(theta)-math.sin(t))])
        j=recover[-1]
        h0,h1=(17.0,17.0) if pole=='plus' else (21.0,18.0)
        tail,r=bezier(j,[j[0],j[1],j[2]+h0],[port[0],port[1]-h1,z],port)
        path=recover+tail[1:]
        r=min(r,17.)
        states={}
        for name,mouth,turn in [('seated',68.,75.5),('stroke',82.,82.5)]:
            arch=[]
            for i in range(101):
                a=math.pi*i/100
                arch.append([41.75+16.5*math.cos(a),turn+16.5*math.sin(a),z])
            points=prefix+path[1:]+arch+[[ACTIVE_X,mouth,z]]
            states[name]={"free_length_mm":round(length(points),3),
                          "points":[[round(q,4) for q in b] for b in points[::6]]+[points[-1]]}
        out[pole]={"projected_exit":prefix[0],"states":states,"transfer_inner_R_mm":round(r-2.4,2),
                   "turn_inner_R_mm":14.1,
                   "min_exit_to_boot_incl_dressing_mm":round(max(x["free_length_mm"] for x in states.values())+8,2),
                   "aux_PCB_prefix_clearance_mm":prior['battery'][pole]['sampled_AUX_PCB_clearance_after_2p4_jacket_radius_mm']}
    return out

def wire_budgets(prior):
    w075,r=bezier((ACTIVE_X,18,POS_Z),(ACTIVE_X,3.5,POS_Z),(8.,-.5,141.25),F0_IN)
    w001=[[ACTIVE_X,18,NEG_Z],[ACTIVE_X,8,NEG_Z],[14,0,150],[-3,12,153],[-3,58,153],[-.5,70,151]]
    custom=[[POST_MOUTH_X,-79.5,147.],[73,-79.5,147.],[63,-72,149],
            [77,-52,153],[112,-46,149],[140,-16,136],[146,40,128],[147,74,124],[161.5,74,113.1602]]
    def regional(points,ends,dress,od,**kw):
        return dict(points=points,chord_polyline_mm=round(length(points),2),ends_mm=ends,dressing_mm=dress,
                    project_blank_mm=math.ceil(length(points)+ends+dress),OD_mm=od,**kw)
    def factory_output(x,amp):
        # Smooth forward bow in an openly supported strip, both end tangents retained.
        a=[]
        for i in range(101):
            t=i/100
            station_x=28+(x-28)*t
            blend=min(1.,(station_x-28)/26.)
            z=141.25+2.875*(1-math.cos(math.pi*blend))
            a.append((station_x,-86+(amp/2)*(1-math.cos(2*math.pi*t)),z))
        return math.pi*10+length(a)+11
    whole={
        "battery_factory":factory_pack_witness(prior),
        "W075_factory_trim_at_robot_cup":{"bare_ends_project_mm":5,
            "length_mm":round(length(w075),2),"project_total_mm":round(length(w075)+5,2),
            "inner_R_mm":round(r-2.4,2),"limit_mm":50,"points":w075[::10]+[list(F0_IN)]},
        "W076_full_factory_output":{"outline_region_mm":[5,-90,138.85,85,-73.5,149.4],
            "port_adjust_x_mm":list(POST_ADJUST_X),
            "point_of_first_curve_mm":list(F0_OUT),"project_center_R_min_mm":15.8,
            "modeled_choices_mm_including_11_end":[round(factory_output(58,0),2),round(factory_output(84,10),2)],
            "source_measured_factory_length_mm":None,"keep_full":True,"rise_above_POST_shelf":{"rise_complete_x_mm":54.0,"shelf_begins_x_mm":56.0,"section_outer_lower_z_mm":144.6,"highest_shelf_z_mm":142.0}},
        "W001_black_LAPP":regional(w001,19,15,3.1,connector_pocket_project_OD_mm=4.8),
        "W076_custom_HELU":regional(custom,26,20,4.2),
        "stock_delivered":None,"actualfit":None,"cut":None,"slack":None,"physicalPASS":False}
    assert whole["W075_factory_trim_at_robot_cup"]["project_total_mm"] <=50
    return whole

def f0_prints(doc,g):
    box,fuse,bore,overlap=[g[k] for k in ('box','fuse','bore','overlap')]
    front=doc.H19_FrontFrame.Shape
    # Joined initial bearing from the original front web at X5..8.25.
    foot=box(5.3,-38,88.8,8.2,-32,94.0)
    socket=box(3.5,-38,92.0,11,-32,98)
    root=fuse(foot,socket).cut(box(4.5,-37.0,94.2,10.0,-33.1,98.4))
    # Single small open frame holds the fuse body on two crosswise straps.
    mast=box(4.8,-36.7,94.2,9.7,-33.4,128.7)
    girder=box(4,-63,125.5,12,-17,129)
    platform=box(-1.9,-63,128,18,-17,130.5)
    support=fuse(mast,girder,platform)
    for y in (-53,-42,-31,-24):
        support=support.cut(box(-.4,y,127.7,3.1,y+4,131))
        support=support.cut(box(13.0,y,127.7,16.5,y+4,131))
    closed=doc.E19_RearLid.Shape
    if overlap(support,closed)>.001:
        contact=support.common(closed).BoundBox
        relief=box(contact.XMin-.85,contact.YMin-.85,contact.ZMin-.85,
                   contact.XMax+.85,contact.YMax+.85,contact.ZMax+.85)
        support=support.cut(relief)
    root_mm3=overlap(front,root)
    front=fuse(front,root)
    return front,support.removeSplitter(),root,root_mm3

def post_print(doc,g):
    box,fuse,overlap=[g[k] for k in ('box','fuse','overlap')]
    bank=doc.E19_WagoRearNeg.Shape
    shoes=[]
    for x in (74.,92.):
        foot=bank.common(box(x,-62.95,110.5,x+5,-58.8,124))
        if foot.Volume<.12:raise RuntimeError("No POST foot")
        top=foot.BoundBox.ZMax
        shoes.append(box(x,-62.95,top,x+5,-58.8,140.7))
        shoes.append(box(x,-79.8,138.8,x+5,-58.8,140.7))
    post=fuse(box(56,-89.8,139.25,105,-76.0,142.0),*shoes)
    for y in (-88.7,-80.9):
        post=post.cut(box(57.5,y,139.05,104.,y+3.35,142.3))
    return post.removeSplitter()
