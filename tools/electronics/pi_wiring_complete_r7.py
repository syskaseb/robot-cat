"""One positive-X fanout bypasses retained head/AUX risers, within saved cover."""
import pi_wiring_complete_r1 as M
M.OUT=M.ROOT/'hardware/electronics/full-cat/pi-wiring-complete-r7'
M.FACTORY_LENGTH=600;M.ROUTE_STYLE='underboard-complete'
M.UNDERBOARD_LOW={'XL05','XL07'}
M.FANNED_AXES={'XL01':10,'XL10':22,'XL07':26,'XL05':14,'XL06':18}
def portals(owners):
    owners['Deck']=owners['Deck'].cut(M.box([3,20,93,28,29,115]))
    for n in ('Deck','Carrier'):
        assert owners[n].isValid() and len(owners[n].Solids)==1
        owners[n].exportBrep(str(M.OUT/(n+'_DESIGN.brep')))
    return dict(diagnostic_constructive_tools=True,new_stls=0,native_final_pending=True,
        Deck_window_world=[3,20,93,28,29,115],Carrier_unchanged=True,
        fanout_curvature_proof='Z linear45mm, X smoothstep: k<=6*max(abs(dx))/45^2; largest27.55 => R>=12.25mm; all circular bends R10')
M.PORTAL_BUILDER=portals
if __name__=='__main__':M.main()
