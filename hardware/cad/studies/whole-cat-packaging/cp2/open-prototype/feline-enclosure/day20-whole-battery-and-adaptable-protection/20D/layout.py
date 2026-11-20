"""20D single fixed axial-X layout and conditional wire budgets, in world mm."""
import math
import numpy as np

Y=27.6
POS_Z=148.9
NEG_Z=144.6
POS_Y=30.45
NEG_Y=24.75
Z0,Z1=137.35,153.85
FIXED_X=12.
END_X=FIXED_X+50
BOX_M=[FIXED_X,16.6,Z0,FIXED_X+25,38.6,Z1]
BOX_F=[FIXED_X+25,16.6,Z0,END_X,38.6,Z1]
BOX_SWEEP=[FIXED_X+25,16.6,Z0,END_X+14,38.6,Z1]
F0=[-71,20,134.15,-20,40,155.65]
F0_OPEN=[-62,17,155.65,-20,43,187]
F0_Z=144.9
POST_X=-111.
FACTORY_PORT_X=POST_X+2.75
CUSTOM_PORT_X=POST_X-2.75
POST_Y=-30.
POST_TRAVEL=(-34.,-20.)
POST=[POST_X-6.5,POST_Y-20,139.9,POST_X+6.5,POST_Y,149.9]
POST_SWEEP=[POST_X-6.5,POST_TRAVEL[0]-20,139.9,POST_X+6.5,POST_TRAVEL[1],149.9]
POST_ACCESS=[-119,-54,150,-103.5,-19,165]
HAND_M=[FIXED_X-2,8.8,154,FIXED_X+26,42.8,174]
HAND_F=[FIXED_X+25,13.7,154,END_X+14,46,174]
HAND_F_UPPER=[FIXED_X+25,8.8,162,END_X+14,46,174]
STOW=[FIXED_X+38.5,16.6,Z0,END_X+14,38.6,156]
SMALL_PLUG=[69,55.2,53,93,67.2,67]
EXIT_X=94.5
EXIT_MIN_X=94.5
PACK_POSES=[('parked',0,0.0),('mid',7,4.4),('withdraw',14,8.8)]

def concatenate(*arrays):
    return np.concatenate([arrays[0],*(a[1:] for a in arrays[1:])])

def length(points):
    return float(np.linalg.norm(np.diff(points,axis=0),axis=1).sum())

def inner_radius(points,od):
    # Use a three-point circumradius on contiguous curved pieces.
    u=np.diff(points,axis=0)
    aa=np.linalg.norm(u[:-1],axis=1)
    bb=np.linalg.norm(u[1:],axis=1)
    cc=np.linalg.norm(u[:-1]+u[1:],axis=1)
    cross=np.linalg.norm(np.cross(u[:-1],u[1:]),axis=1)
    turn=(cross>1e-9)&(aa>1e-8)&(bb>1e-8)
    return float(min(aa[turn]*bb[turn]*cc[turn]/(2*cross[turn]))-od/2)

def nominal_pack_curve(pole,stroke,outer_shift):
    # Photo establishes the short end. Exact wire exit and molded extension
    # remain fit inputs. This witness comes from the upper inboard corner of
    # the selected +X end, alongside the AUX board and above its upper edge.
    start_y=29.15 if pole=='plus' else 23.85
    start_z=69.0 if pole=='plus' else 69.0
    end_y=POS_Y if pole=='plus' else NEG_Y
    end_z=POS_Z if pole=='plus' else NEG_Z
    r=20.5+outer_shift
    a=np.linspace(0,math.pi/2,150)
    under=np.column_stack((EXIT_X+r*np.sin(a),np.full(a.shape,start_y),start_z+r*(1-np.cos(a))))
    x0,y0,z0=under[-1]
    upper_z=113.5
    stem=np.column_stack((np.full(7,x0),np.full(7,y0),np.linspace(z0,upper_z,7)))
    tail=np.column_stack((END_X+stroke+(x0-END_X-stroke)*np.cos(a),
                          y0+(end_y-y0)*(np.sin(a)**2),
                          upper_z+(end_z-upper_z)*np.sin(a)))
    return concatenate(under,stem,tail)

def wire_budgets():
    leads={}
    for pole in ("plus","minus"):
        result={}
        for name,stroke,outer_shift in PACK_POSES:
            p=nominal_pack_curve(pole,stroke,outer_shift)
            result[name]={"free_length_mm":round(length(p),2),"inner_R_mm":round(inner_radius(p,4.8),2),
                          "stations":p[::5].round(4).tolist()+[p[-1].round(4).tolist()]}
        lead_allowance=8.0
        leads[pole]={"states":result,"project_OD_mm":4.8,
                     "exit_to_boot_with_dressing_mm":round(max(q["free_length_mm"] for q in result.values())+lead_allowance,2),
                     "dressing_mm":lead_allowance,"actual_exit_and_internal_end_debits":None}
    # Two equal, opposing circular bends give the same axial tangencies
    # at the fixed robot cup and at the molded F0 strain relief.
    transverse=np.array([30-POS_Y,F0_Z-POS_Z])
    span=FIXED_X+20
    delta=float(np.linalg.norm(transverse)); r=(span**2+delta**2)/(4*delta)
    a=np.linspace(0,2*math.atan2(delta,span),80)
    xx=-r*np.sin(a); yy=r*(1-np.cos(a))
    q=np.column_stack((xx,yy))
    q=np.concatenate([q,np.array([-span,delta])-q[-2::-1]])
    w075=np.column_stack((FIXED_X+q[:,0],np.array([POS_Y,POS_Z])+q[:,1,None]*transverse/delta))
    def regional(p,od,end,dress):
        return {"allocated_waypoints":p,"nominal_span_mm":round(length(np.array(p)),2),"OD_mm":od,
                "terminal_debits_mm":end,"one_laying_allowance_mm":dress,
                "project_blank_mm":math.ceil(length(np.array(p))+end+dress)}
    w001=[[FIXED_X,NEG_Y,NEG_Z],[3,28,143.5],[-1,39,141.5],[-4,53,148],[-.5,70,151]]
    # Leave the adjacent molded wire and the head change in separate
    # lanes initially. The remainder uses an accessible upper body region.
    helu=[[CUSTOM_PORT_X,-30,144.9],[CUSTOM_PORT_X,-24,144.9],[CUSTOM_PORT_X,-15,151.2],
          [-107.5,-9.8,152.5],[-83,-5,154],[-43,8,152],[-8,14,144.5],[43,9,149],
          [75,10.5,148],[84,20.5,153.5],[108,41,157],[119,53,147],[145,66,133],[150.3,74,132.5592],[153.05,74,127.7961]]
    def out(yp):
        r=20.
        x0=FACTORY_PORT_X+r
        a=np.linspace(0,np.pi/2,91)
        q=np.column_stack((x0-r*np.sin(a),30-r*(1-np.cos(a)),np.full(a.shape,F0_Z)))
        return np.concatenate([[[-71,30,F0_Z]],q,[[FACTORY_PORT_X,yp,F0_Z]]])
    wf=out(POST_Y)
    return {"pack":leads,
            "W075":{"original_F0_lead":True,"robot_side_trim_only":True,
                    "free_mm":round(length(w075),2),"project_total_mm":round(length(w075)+5,2),
                    "robot_cup_project_debit_mm":5.,"inner_R_mm":round(inner_radius(w075,4.8),2),
                    "limit_mm":50,"points":w075[::12].round(4).tolist()+[w075[-1].round(4).tolist()]},
            "W076_complete_FHAC_out":{"factory_full":True,"PORT_adjust_Y_mm":POST_TRAVEL,
                    "project_port_pitch_mm":FACTORY_PORT_X-CUSTOM_PORT_X,"actual_port_pitch":None,
                    "project_port_choices_plus_end_mm":sorted([round(length(out(p))+11,2) for p in POST_TRAVEL]),
                    "R_center_mm":20,"WAGO_project_debit_mm":11,"shape_points":wf[::6].round(4).tolist()+[wf[-1].tolist()],
                    "preparation_and_OD_supplier_actual":None},
            "W001":regional(w001,3.1,19,15),"W076_custom":regional(helu,4.2,26,20),
            "stock_nominal_selected_mm":{"LAPP0107001":3000,"HELU23802":9000},"physical_stock_delivered":None,"actualfit":None,"cut":None,"slack":None,"physicalPASS":False}