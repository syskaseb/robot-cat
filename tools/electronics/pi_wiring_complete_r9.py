"""Keep OE above the Carrier web and bypass the retained PWM return to +X."""
import pi_wiring_complete_r8 as P
M=P.M
M.OUT=M.ROOT/'hardware/electronics/full-cat/pi-wiring-complete-r9'
M.TOP_OVERRIDES={'XL07':149}
M.OUTSIDE_OVERRIDES={'XL07':125}
def portals(owners):
    owners['Deck']=owners['Deck'].cut(M.box([3,20,93,28,29,115]))
    for name,axis,lane,direction,z in [('XL01',10,45,1,151.5),('XL10',22,53,1,151.5),('XL07',26,57,-1,149),('XL05',14,51,-1,149),('XL06',18,53,-1,151.5)]:
        edge=M.B.arc([axis+direction*10,lane,z-10],[axis,lane,z-10],[axis+direction*10,lane,z])
        owners['Carrier']=owners['Carrier'].cut(M.tube(edge,1.2))
    for n in ('Deck','Carrier'):
        assert owners[n].isValid() and len(owners[n].Solids)==1
        owners[n].exportBrep(str(M.OUT/(n+'_DESIGN.brep')))
    return dict(new_stls=0,native_final_pending=True,Deck_window_world=[3,20,93,28,29,115],Carrier_arc_clearance_radius=1.2)
M.PORTAL_BUILDER=portals
if __name__=='__main__':M.main()
