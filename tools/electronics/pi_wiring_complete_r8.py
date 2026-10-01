"""Fixed fanout; lower OE plane and bends below AUX with distinct north risers."""
import pi_wiring_complete_r7 as P
M=P.M
M.OUT=M.ROOT/'hardware/electronics/full-cat/pi-wiring-complete-r8'
M.FANNED_LOW=118
M.LANE_OVERRIDES={'XL10':53,'XL07':57}
M.TOP_OVERRIDES={'XL07':146.5}
def portals(owners):
    owners['Deck']=owners['Deck'].cut(M.box([3,20,93,28,29,115]))
    for name,axis,lane,direction,z in [('XL01',10,45,1,151.5),('XL10',22,53,1,151.5),('XL07',26,57,1,146.5),('XL05',14,51,-1,149),('XL06',18,53,-1,151.5)]:
        edge=M.B.arc([axis+direction*10,lane,z-10],[axis,lane,z-10],[axis+direction*10,lane,z])
        owners['Carrier']=owners['Carrier'].cut(M.tube(edge,1.2))
    for n in ('Deck','Carrier'):
        assert owners[n].isValid() and len(owners[n].Solids)==1
        owners[n].exportBrep(str(M.OUT/(n+'_DESIGN.brep')))
    return dict(diagnostic_constructive_tools=True,new_stls=0,native_final_pending=True,
        Deck_window_world=[3,20,93,28,29,115],Carrier_arc_clearance_radius=1.2,
        fanout_curvature_proof='Z linear45mm, X smoothstep: k<=6*max(abs(dx))/45^2; largest27.55 => R>=12.25mm; all circular bends R10')
M.PORTAL_BUILDER=portals
if __name__=='__main__':M.main()
